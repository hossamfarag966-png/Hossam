import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.core.config import settings

import enum


class JobStatus(str, enum.Enum):
    NEW = "new"
    INTERESTED = "interested"
    APPLIED = "applied"
    REJECTED = "rejected"
    NOT_RELEVANT = "not_relevant"


class JobSource(str, enum.Enum):
    REMOTEOK = "remoteok"
    REMOTIVE = "remotive"
    WEWORKREMOTELY = "weworkremotely"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    MANUAL = "manual"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Parsed data
    skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    experience: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    education: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    languages: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    certifications: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Preferences
    target_roles: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    target_industries: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    target_seniority: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    target_locations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    work_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    min_salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")
    work_authorization: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    deal_breakers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Embedding of full profile text
    embedding: Mapped[Optional[list]] = mapped_column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=True)

    # Meta
    cv_filename: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_export_filename: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Total years of experience (computed)
    years_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(50), index=True)

    # Core fields
    title: Mapped[str] = mapped_column(String(500))
    company: Mapped[str] = mapped_column(String(500))
    company_logo: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    work_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    url: Mapped[str] = mapped_column(String(2000))
    description_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Parsed structured fields
    seniority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    skills_required: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    skills_nice_to_have: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    responsibilities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    requirements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Embedding
    embedding: Mapped[Optional[list]] = mapped_column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=True)

    # Matching scores
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skill_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    semantic_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Company analysis
    company_size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_funding: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    company_industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Salary estimation
    estimated_salary_low: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_salary_mid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_salary_high: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")

    # Acceptance likelihood
    acceptance_likelihood: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    acceptance_factors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # User feedback
    status: Mapped[str] = mapped_column(String(20), default=JobStatus.NEW.value, index=True)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Meta
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    briefing_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class FeedbackWeight(Base):
    """Stores learned weights from user feedback to improve ranking."""
    __tablename__ = "feedback_weights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feature_name: Mapped[str] = mapped_column(String(255), unique=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
