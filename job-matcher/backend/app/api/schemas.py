from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProfilePreferencesUpdate(BaseModel):
    target_roles: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None
    target_seniority: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    work_mode: Optional[str] = None
    min_salary: Optional[int] = None
    salary_currency: Optional[str] = None
    work_authorization: Optional[List[str]] = None
    deal_breakers: Optional[List[str]] = None
    languages: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[dict] = None
    experience: Optional[dict] = None
    education: Optional[dict] = None
    languages: Optional[dict] = None
    target_roles: Optional[dict] = None
    target_industries: Optional[dict] = None
    target_seniority: Optional[dict] = None
    target_locations: Optional[dict] = None
    work_mode: Optional[str] = None
    min_salary: Optional[int] = None
    salary_currency: Optional[str] = None
    work_authorization: Optional[dict] = None
    deal_breakers: Optional[dict] = None
    years_experience: Optional[int] = None
    cv_filename: Optional[str] = None
    linkedin_export_filename: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: str
    external_id: Optional[str] = None
    source: str
    title: str
    company: str
    company_logo: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    url: str
    seniority: Optional[str] = None
    skills_required: Optional[dict] = None
    skills_nice_to_have: Optional[dict] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    match_score: Optional[float] = None
    match_explanation: Optional[str] = None
    skill_coverage: Optional[float] = None
    semantic_score: Optional[float] = None
    company_size: Optional[str] = None
    company_rating: Optional[float] = None
    estimated_salary_low: Optional[int] = None
    estimated_salary_mid: Optional[int] = None
    estimated_salary_high: Optional[int] = None
    estimated_salary_currency: Optional[str] = None
    acceptance_likelihood: Optional[float] = None
    acceptance_factors: Optional[dict] = None
    status: str = "new"
    user_notes: Optional[str] = None
    posted_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    tags: Optional[dict] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int


class JobStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class DashboardStats(BaseModel):
    total_jobs: int
    new_jobs: int
    applied_jobs: int
    interested_jobs: int
    avg_match_score: float
