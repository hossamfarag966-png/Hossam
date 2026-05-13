from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from typing import Optional, List
import os

from app.core.database import get_db
from app.core.config import settings
from app.models.models import UserProfile, Job, JobStatus
from app.api.schemas import (
    ProfileResponse,
    ProfilePreferencesUpdate,
    JobResponse,
    JobStatusUpdate,
    JobListResponse,
    DashboardStats,
)
from app.services.profile_parser import parse_cv, parse_linkedin_export
from app.services.embedding_service import generate_embedding

router = APIRouter()


# ─── Profile ─────────────────────────────────────────────────────────────────


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found. Upload a CV or LinkedIn export first.")
    return profile


@router.post("/profile/cv", response_model=ProfileResponse)
async def upload_cv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    parsed = await parse_cv(filepath, ext)

    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()

    if profile:
        for key, value in parsed.items():
            if value is not None:
                setattr(profile, key, value)
        profile.cv_filename = file.filename
    else:
        profile = UserProfile(**parsed, cv_filename=file.filename)
        db.add(profile)

    profile_text = _build_profile_text(profile)
    profile.embedding = await generate_embedding(profile_text)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/profile/linkedin", response_model=ProfileResponse)
async def upload_linkedin_export(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext != "zip":
        raise HTTPException(status_code=400, detail="Please upload the LinkedIn data export ZIP file")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    parsed = await parse_linkedin_export(filepath)

    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()

    if profile:
        for key, value in parsed.items():
            if value is not None:
                setattr(profile, key, value)
        profile.linkedin_export_filename = file.filename
    else:
        profile = UserProfile(**parsed, linkedin_export_filename=file.filename)
        db.add(profile)

    profile_text = _build_profile_text(profile)
    profile.embedding = await generate_embedding(profile_text)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.put("/profile/preferences", response_model=ProfileResponse)
async def update_preferences(prefs: ProfilePreferencesUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found. Upload a CV first.")

    update_data = prefs.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    profile_text = _build_profile_text(profile)
    profile.embedding = await generate_embedding(profile_text)

    await db.commit()
    await db.refresh(profile)
    return profile


# ─── Jobs ─────────────────────────────────────────────────────────────────────


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = None,
    source: Optional[str] = None,
    min_match: Optional[float] = None,
    sort_by: str = Query(default="match_score", enum=["match_score", "posted_at", "acceptance_likelihood"]),
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Job)

    if status:
        query = query.where(Job.status == status)
    if source:
        query = query.where(Job.source == source)
    if min_match:
        query = query.where(Job.match_score >= min_match)

    if sort_by == "match_score":
        query = query.order_by(desc(Job.match_score))
    elif sort_by == "posted_at":
        query = query.order_by(desc(Job.posted_at))
    elif sort_by == "acceptance_likelihood":
        query = query.order_by(desc(Job.acceptance_likelihood))

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()

    from sqlalchemy import func
    count_query = select(Job)
    if status:
        count_query = count_query.where(Job.status == status)
    if source:
        count_query = count_query.where(Job.source == source)
    if min_match:
        count_query = count_query.where(Job.match_score >= min_match)
    count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
    total = count_result.scalar()

    return JobListResponse(jobs=jobs, total=total, limit=limit, offset=offset)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/jobs/{job_id}/status")
async def update_job_status(job_id: str, body: JobStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = body.status
    if body.notes:
        job.user_notes = body.notes

    await db.commit()
    return {"status": "updated", "job_id": job_id, "new_status": body.status}


# ─── Dashboard Stats ──────────────────────────────────────────────────────────


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func

    total = await db.execute(select(func.count(Job.id)))
    new_count = await db.execute(select(func.count(Job.id)).where(Job.status == JobStatus.NEW.value))
    applied_count = await db.execute(select(func.count(Job.id)).where(Job.status == JobStatus.APPLIED.value))
    interested_count = await db.execute(select(func.count(Job.id)).where(Job.status == JobStatus.INTERESTED.value))
    avg_match = await db.execute(select(func.avg(Job.match_score)).where(Job.match_score.isnot(None)))

    return DashboardStats(
        total_jobs=total.scalar() or 0,
        new_jobs=new_count.scalar() or 0,
        applied_jobs=applied_count.scalar() or 0,
        interested_jobs=interested_count.scalar() or 0,
        avg_match_score=round(avg_match.scalar() or 0, 1),
    )


# ─── Manual Triggers ──────────────────────────────────────────────────────────


@router.post("/fetch-jobs")
async def trigger_fetch_jobs():
    from app.worker import fetch_all_jobs
    fetch_all_jobs.delay()
    return {"status": "triggered", "message": "Job fetching started in background"}


@router.post("/send-digest")
async def trigger_digest():
    from app.worker import send_daily_digest
    send_daily_digest.delay()
    return {"status": "triggered", "message": "Digest generation started in background"}


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _build_profile_text(profile: UserProfile) -> str:
    parts = []
    if profile.headline:
        parts.append(f"Headline: {profile.headline}")
    if profile.summary:
        parts.append(f"Summary: {profile.summary}")
    if profile.skills:
        skills_list = profile.skills if isinstance(profile.skills, list) else profile.skills.get("skills", [])
        parts.append(f"Skills: {', '.join(skills_list)}")
    if profile.experience:
        exp_list = profile.experience if isinstance(profile.experience, list) else profile.experience.get("experience", [])
        for exp in exp_list[:5]:
            if isinstance(exp, dict):
                parts.append(f"Experience: {exp.get('title', '')} at {exp.get('company', '')} - {exp.get('description', '')}")
            else:
                parts.append(f"Experience: {exp}")
    if profile.target_roles:
        roles = profile.target_roles if isinstance(profile.target_roles, list) else profile.target_roles.get("roles", [])
        parts.append(f"Target roles: {', '.join(roles)}")
    return "\n".join(parts)
