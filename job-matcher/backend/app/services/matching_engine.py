"""Matching engine: computes match score between profile and job postings."""

from typing import Dict, Any, List, Optional, Tuple

from app.services.embedding_service import cosine_similarity, generate_embedding
from app.services.llm_service import (
    parse_job_description,
    generate_match_explanation,
    estimate_salary,
    compute_acceptance_likelihood,
)


async def score_job(
    profile: Dict[str, Any],
    profile_embedding: List[float],
    job_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Score a job against the user profile. Returns enriched job data."""

    # 1. Parse job description into structured fields
    if not job_data.get("skills_required"):
        parsed = await parse_job_description(job_data.get("description_raw", ""))
        job_data.update({
            "seniority": parsed.get("seniority"),
            "skills_required": parsed.get("skills_required", []),
            "skills_nice_to_have": parsed.get("skills_nice_to_have", []),
            "responsibilities": parsed.get("responsibilities", []),
            "requirements": parsed.get("requirements", []),
            "work_mode": parsed.get("work_mode") or job_data.get("work_mode"),
            "salary_min": parsed.get("salary_min") or job_data.get("salary_min"),
            "salary_max": parsed.get("salary_max") or job_data.get("salary_max"),
            "industry": parsed.get("industry"),
        })

    # 2. Hard filters
    hard_filter_pass, hard_filter_penalty = _apply_hard_filters(profile, job_data)
    if not hard_filter_pass:
        job_data["match_score"] = 0
        job_data["match_explanation"] = "Failed hard filter (location/salary/deal-breaker)"
        return job_data

    # 3. Semantic similarity
    job_text = _build_job_text(job_data)
    job_embedding = await generate_embedding(job_text)
    semantic_score = 0.0
    if profile_embedding and job_embedding:
        semantic_score = max(0, cosine_similarity(profile_embedding, job_embedding))

    # 4. Skill coverage
    profile_skills = _normalize_skills(profile.get("skills", []))
    required_skills = _normalize_skills(job_data.get("skills_required", []))
    nice_skills = _normalize_skills(job_data.get("skills_nice_to_have", []))

    skill_coverage, matching_skills, missing_skills = _compute_skill_coverage(
        profile_skills, required_skills, nice_skills
    )

    # 5. Seniority alignment
    seniority_score = _compute_seniority_score(profile, job_data)

    # 6. Combined score
    raw_score = (
        semantic_score * 35
        + skill_coverage * 40
        + seniority_score * 15
        + (1.0 - hard_filter_penalty) * 10
    )
    match_score = min(100, max(0, raw_score))

    # 7. Match explanation
    explanation = await generate_match_explanation(
        profile_summary=profile.get("summary", ""),
        job_title=job_data.get("title", ""),
        job_company=job_data.get("company", ""),
        match_score=match_score,
        skill_coverage=skill_coverage * 100,
        matching_skills=matching_skills,
        missing_skills=missing_skills,
    )

    # 8. Salary estimation
    salary_est = await estimate_salary(
        title=job_data.get("title", ""),
        location=job_data.get("location", "Remote"),
        seniority=job_data.get("seniority", "mid"),
        skills=required_skills[:5],
        company=job_data.get("company", ""),
    )

    # 9. Acceptance likelihood
    acceptance = await compute_acceptance_likelihood(profile, job_data)

    job_data["match_score"] = round(match_score, 1)
    job_data["match_explanation"] = explanation
    job_data["skill_coverage"] = round(skill_coverage * 100, 1)
    job_data["semantic_score"] = round(semantic_score * 100, 1)
    job_data["embedding"] = job_embedding
    job_data["estimated_salary_low"] = salary_est.get("low")
    job_data["estimated_salary_mid"] = salary_est.get("mid")
    job_data["estimated_salary_high"] = salary_est.get("high")
    job_data["estimated_salary_currency"] = "USD"
    job_data["acceptance_likelihood"] = acceptance.get("likelihood", 50)
    job_data["acceptance_factors"] = acceptance.get("factors", {})

    return job_data


def _apply_hard_filters(profile: Dict[str, Any], job: Dict[str, Any]) -> Tuple[bool, float]:
    penalty = 0.0

    min_salary = profile.get("min_salary")
    job_salary_max = job.get("salary_max")
    if min_salary and job_salary_max and job_salary_max < min_salary:
        return False, 1.0

    preferred_mode = profile.get("work_mode", "any")
    job_mode = job.get("work_mode", "unknown")
    if preferred_mode != "any" and job_mode != "unknown":
        if preferred_mode != job_mode:
            penalty += 0.3

    deal_breakers = profile.get("deal_breakers", [])
    if deal_breakers:
        job_text = f"{job.get('title', '')} {job.get('description_raw', '')} {job.get('company', '')}".lower()
        for breaker in deal_breakers:
            if breaker.lower() in job_text:
                return False, 1.0

    target_locations = profile.get("target_locations", [])
    if target_locations and "remote" not in [loc.lower() for loc in target_locations]:
        job_location = (job.get("location") or "").lower()
        if not any(loc.lower() in job_location for loc in target_locations):
            penalty += 0.2

    return True, min(1.0, penalty)


def _compute_skill_coverage(
    profile_skills: List[str],
    required_skills: List[str],
    nice_skills: List[str],
) -> Tuple[float, List[str], List[str]]:
    if not required_skills:
        return 0.5, [], []

    matching = []
    missing = []

    for skill in required_skills:
        if _skill_matches(skill, profile_skills):
            matching.append(skill)
        else:
            missing.append(skill)

    nice_matches = sum(1 for s in nice_skills if _skill_matches(s, profile_skills))
    nice_bonus = (nice_matches / max(1, len(nice_skills))) * 0.1 if nice_skills else 0

    coverage = (len(matching) / max(1, len(required_skills))) + nice_bonus
    return min(1.0, coverage), matching, missing


def _skill_matches(skill: str, profile_skills: List[str]) -> bool:
    skill_lower = skill.lower().strip()

    if skill_lower in profile_skills:
        return True

    skill_variants = _get_skill_variants(skill_lower)
    for variant in skill_variants:
        if variant in profile_skills:
            return True
        for ps in profile_skills:
            if variant in ps or ps in variant:
                return True

    return False


def _get_skill_variants(skill: str) -> List[str]:
    variants = [skill]
    aliases = {
        "javascript": ["js", "es6", "ecmascript"],
        "typescript": ["ts"],
        "python": ["py"],
        "react": ["reactjs", "react.js"],
        "node": ["nodejs", "node.js"],
        "vue": ["vuejs", "vue.js"],
        "angular": ["angularjs"],
        "postgres": ["postgresql", "psql"],
        "mongo": ["mongodb"],
        "kubernetes": ["k8s"],
        "ci/cd": ["cicd", "ci cd", "continuous integration"],
        "aws": ["amazon web services"],
        "gcp": ["google cloud"],
        "azure": ["microsoft azure"],
        "machine learning": ["ml"],
        "deep learning": ["dl"],
        "artificial intelligence": ["ai"],
        "natural language processing": ["nlp"],
    }

    for key, alts in aliases.items():
        if skill == key:
            variants.extend(alts)
        elif skill in alts:
            variants.append(key)

    return variants


def _normalize_skills(skills) -> List[str]:
    if isinstance(skills, dict):
        skills = skills.get("skills", []) or skills.get("list", []) or list(skills.values())
    if not isinstance(skills, list):
        return []
    return [s.lower().strip() for s in skills if isinstance(s, str)]


def _compute_seniority_score(profile: Dict[str, Any], job: Dict[str, Any]) -> float:
    seniority_levels = {
        "intern": 0, "junior": 1, "mid": 2, "senior": 3,
        "lead": 4, "principal": 5, "staff": 5,
        "manager": 4, "director": 5, "vp": 6, "c-level": 7,
    }

    job_seniority = (job.get("seniority") or "mid").lower()
    job_level = seniority_levels.get(job_seniority, 2)

    target_seniority = profile.get("target_seniority", [])
    if target_seniority:
        if isinstance(target_seniority, list) and target_seniority:
            profile_level = max(seniority_levels.get(s.lower(), 2) for s in target_seniority)
        elif isinstance(target_seniority, dict):
            levels = target_seniority.get("levels", [])
            profile_level = max((seniority_levels.get(s.lower(), 2) for s in levels), default=2)
        else:
            profile_level = 2
    else:
        years = profile.get("years_experience", 3)
        if years is None:
            years = 3
        if years < 2:
            profile_level = 1
        elif years < 5:
            profile_level = 2
        elif years < 8:
            profile_level = 3
        elif years < 12:
            profile_level = 4
        else:
            profile_level = 5

    distance = abs(job_level - profile_level)
    if distance == 0:
        return 1.0
    elif distance == 1:
        return 0.7
    elif distance == 2:
        return 0.3
    else:
        return 0.1


def _build_job_text(job: Dict[str, Any]) -> str:
    parts = []
    if job.get("title"):
        parts.append(f"Title: {job['title']}")
    if job.get("company"):
        parts.append(f"Company: {job['company']}")
    if job.get("description_raw"):
        parts.append(f"Description: {job['description_raw'][:3000]}")
    if job.get("skills_required"):
        skills = job["skills_required"]
        if isinstance(skills, list):
            parts.append(f"Required Skills: {', '.join(skills)}")
    return "\n".join(parts)
