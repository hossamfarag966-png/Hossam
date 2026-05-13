"""Celery worker for background job fetching, scoring, and daily digest."""

import asyncio
from datetime import datetime
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery("job_matcher", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

digest_hour, digest_minute = 7, 0
try:
    parts = settings.DIGEST_TIME.split(":")
    digest_hour = int(parts[0])
    digest_minute = int(parts[1]) if len(parts) > 1 else 0
except (ValueError, IndexError):
    pass

celery_app.conf.beat_schedule = {
    "fetch-jobs-every-6-hours": {
        "task": "app.worker.fetch_all_jobs",
        "schedule": crontab(minute="0", hour="*/6"),
    },
    "daily-digest": {
        "task": "app.worker.send_daily_digest",
        "schedule": crontab(minute=str(digest_minute), hour=str(digest_hour)),
    },
}


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.worker.fetch_all_jobs")
def fetch_all_jobs():
    _run_async(_fetch_all_jobs_async())


@celery_app.task(name="app.worker.send_daily_digest")
def send_daily_digest():
    _run_async(_send_daily_digest_async())


async def _fetch_all_jobs_async():
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

    from app.models.models import UserProfile, Job
    from app.sources.remoteok import RemoteOKConnector
    from app.sources.remotive import RemotiveConnector
    from app.sources.weworkremotely import WeWorkRemotelyConnector
    from app.services.matching_engine import score_job

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(UserProfile).limit(1))
        profile = result.scalar_one_or_none()

        if not profile:
            print("[Worker] No profile found. Skipping job fetch.")
            return

        profile_dict = {
            "skills": profile.skills,
            "experience": profile.experience,
            "years_experience": profile.years_experience,
            "target_roles": profile.target_roles,
            "target_seniority": profile.target_seniority,
            "target_locations": profile.target_locations,
            "work_mode": profile.work_mode,
            "min_salary": profile.min_salary,
            "deal_breakers": profile.deal_breakers,
            "summary": profile.summary,
            "location": profile.location,
        }
        profile_embedding = profile.embedding

        keywords = []
        if profile.target_roles:
            roles = profile.target_roles if isinstance(profile.target_roles, list) else profile.target_roles.get("roles", [])
            keywords.extend(roles)
        if profile.skills:
            skills = profile.skills if isinstance(profile.skills, list) else profile.skills.get("skills", [])
            keywords.extend(skills[:5])

        connectors = [
            RemoteOKConnector(),
            RemotiveConnector(),
            WeWorkRemotelyConnector(),
        ]

        all_jobs = []
        for connector in connectors:
            try:
                jobs = await connector.fetch_jobs(keywords=keywords if keywords else None)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"[Worker] Error with {connector.source_name}: {e}")

        print(f"[Worker] Fetched {len(all_jobs)} total jobs from all sources")

        existing_result = await db.execute(select(Job.external_id))
        existing_ids = {row[0] for row in existing_result.fetchall() if row[0]}

        new_count = 0
        for job_data in all_jobs:
            if job_data["external_id"] in existing_ids:
                continue

            try:
                scored = await score_job(profile_dict, profile_embedding, job_data)
            except Exception as e:
                print(f"[Worker] Error scoring job {job_data.get('title')}: {e}")
                scored = job_data
                scored["match_score"] = 0

            if scored.get("match_score", 0) >= 20 or not profile_embedding:
                job = Job(
                    external_id=scored.get("external_id"),
                    source=scored.get("source", job_data.get("external_id", "").split("_")[0]),
                    title=scored.get("title", "Unknown"),
                    company=scored.get("company", "Unknown"),
                    company_logo=scored.get("company_logo"),
                    location=scored.get("location"),
                    work_mode=scored.get("work_mode"),
                    url=scored.get("url", ""),
                    description_raw=scored.get("description_raw"),
                    seniority=scored.get("seniority"),
                    skills_required=scored.get("skills_required"),
                    skills_nice_to_have=scored.get("skills_nice_to_have"),
                    responsibilities=scored.get("responsibilities"),
                    requirements=scored.get("requirements"),
                    salary_min=scored.get("salary_min"),
                    salary_max=scored.get("salary_max"),
                    salary_currency=scored.get("salary_currency"),
                    industry=scored.get("industry"),
                    embedding=scored.get("embedding"),
                    match_score=scored.get("match_score"),
                    match_explanation=scored.get("match_explanation"),
                    skill_coverage=scored.get("skill_coverage"),
                    semantic_score=scored.get("semantic_score"),
                    estimated_salary_low=scored.get("estimated_salary_low"),
                    estimated_salary_mid=scored.get("estimated_salary_mid"),
                    estimated_salary_high=scored.get("estimated_salary_high"),
                    estimated_salary_currency=scored.get("estimated_salary_currency", "USD"),
                    acceptance_likelihood=scored.get("acceptance_likelihood"),
                    acceptance_factors=scored.get("acceptance_factors"),
                    posted_at=scored.get("posted_at"),
                    tags=scored.get("tags"),
                )
                db.add(job)
                new_count += 1

        await db.commit()
        print(f"[Worker] Stored {new_count} new jobs")

    await engine.dispose()


async def _send_daily_digest_async():
    from sqlalchemy import select, desc
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

    from app.models.models import Job, JobStatus
    from app.services.email_service import send_digest_email

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(
            select(Job)
            .where(Job.status == JobStatus.NEW.value)
            .where(Job.briefing_sent == False)
            .order_by(desc(Job.match_score))
            .limit(10)
        )
        top_jobs = result.scalars().all()

        if not top_jobs:
            print("[Digest] No new jobs to report")
            return

        await send_digest_email(top_jobs)

        for job in top_jobs:
            job.briefing_sent = True
        await db.commit()

        print(f"[Digest] Sent digest with {len(top_jobs)} jobs")

    await engine.dispose()
