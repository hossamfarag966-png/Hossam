"""LLM-powered services for CV parsing, JD analysis, and matching explanations."""

import json
from typing import Dict, Any, Optional, List

from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


async def parse_cv_with_llm(cv_text: str) -> Dict[str, Any]:
    """Use LLM to parse CV text into structured profile fields."""
    if not client:
        return _basic_cv_parse(cv_text)

    prompt = """Parse this CV/resume into structured JSON. Extract:
- name: full name
- email: email address
- headline: professional headline/title
- summary: brief professional summary
- location: location
- skills: list of technical and soft skills
- experience: list of {title, company, description, started_on, finished_on, location}
- education: list of {school, degree, field, start_date, end_date}
- languages: list of spoken languages
- years_experience: estimated total years of professional experience (integer)

Return ONLY valid JSON, no markdown or explanation.

CV Text:
"""
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a precise CV parser. Return only valid JSON."},
            {"role": "user", "content": prompt + cv_text[:8000]},
        ],
        temperature=0.1,
        max_tokens=3000,
    )

    try:
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except (json.JSONDecodeError, IndexError):
        return _basic_cv_parse(cv_text)


async def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """Parse a job description into structured fields."""
    if not client:
        return _basic_jd_parse(jd_text)

    prompt = """Parse this job description into structured JSON. Extract:
- title: job title
- seniority: one of [junior, mid, senior, lead, principal, manager, director, vp, c-level]
- skills_required: list of must-have skills
- skills_nice_to_have: list of nice-to-have skills
- responsibilities: list of key responsibilities
- requirements: list of requirements (years of exp, education, etc.)
- work_mode: one of [remote, hybrid, onsite, unknown]
- salary_min: minimum salary if mentioned (integer, USD equivalent)
- salary_max: maximum salary if mentioned (integer, USD equivalent)
- salary_currency: currency if mentioned
- industry: industry/domain

Return ONLY valid JSON.

Job Description:
"""
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a job description parser. Return only valid JSON."},
            {"role": "user", "content": prompt + jd_text[:6000]},
        ],
        temperature=0.1,
        max_tokens=2000,
    )

    try:
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except (json.JSONDecodeError, IndexError):
        return _basic_jd_parse(jd_text)


async def generate_match_explanation(
    profile_summary: str,
    job_title: str,
    job_company: str,
    match_score: float,
    skill_coverage: float,
    matching_skills: List[str],
    missing_skills: List[str],
) -> str:
    """Generate a short explanation of why a job matches."""
    if not client:
        if matching_skills:
            return f"Matches {len(matching_skills)} key skills: {', '.join(matching_skills[:3])}"
        return f"Match score: {match_score:.0f}%"

    prompt = f"""Write a concise one-line explanation (max 100 chars) of why this job matches this candidate.

Job: {job_title} at {job_company}
Match Score: {match_score:.0f}%
Skill Coverage: {skill_coverage:.0f}%
Skills Matched: {', '.join(matching_skills[:5])}
Skills Missing: {', '.join(missing_skills[:3])}

One line explanation:"""

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=60,
    )
    return response.choices[0].message.content.strip()


async def estimate_salary(
    title: str, location: str, seniority: str, skills: List[str], company: str
) -> Dict[str, int]:
    """Estimate salary range using LLM knowledge."""
    if not client:
        return {"low": 50000, "mid": 75000, "high": 100000}

    prompt = f"""Estimate the annual salary range in USD for this role. Consider the location and seniority.
Return ONLY JSON: {{"low": number, "mid": number, "high": number}}

Role: {title}
Company: {company}
Location: {location or "Remote"}
Seniority: {seniority or "mid"}
Key Skills: {', '.join(skills[:5]) if skills else 'general'}
"""

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a compensation analyst. Return only valid JSON with low/mid/high salary estimates in USD."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=100,
    )

    try:
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except (json.JSONDecodeError, IndexError):
        return {"low": 50000, "mid": 75000, "high": 100000}


async def compute_acceptance_likelihood(
    profile: Dict[str, Any], job: Dict[str, Any]
) -> Dict[str, Any]:
    """Compute acceptance likelihood and top factors."""
    if not client:
        return {
            "likelihood": 50.0,
            "factors": {
                "positive": ["Skills partially match"],
                "negative": ["Cannot determine full alignment without LLM"],
            },
        }

    prompt = f"""Estimate the likelihood (0-100%) that this candidate would get an interview for this role.
Consider skill match, experience level, and location fit.

Return ONLY JSON: {{"likelihood": number, "positive_factors": [top 3 strings], "negative_factors": [top 3 strings]}}

Candidate:
- Skills: {json.dumps(profile.get('skills', []))[:500]}
- Years Experience: {profile.get('years_experience', 'unknown')}
- Location: {profile.get('location', 'unknown')}
- Seniority Target: {profile.get('target_seniority', 'any')}

Job:
- Title: {job.get('title', '')}
- Required Skills: {json.dumps(job.get('skills_required', []))[:300]}
- Seniority: {job.get('seniority', 'unknown')}
- Location: {job.get('location', 'unknown')}
- Work Mode: {job.get('work_mode', 'unknown')}
"""

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a hiring analyst. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=300,
    )

    try:
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        result = json.loads(content)
        return {
            "likelihood": result.get("likelihood", 50),
            "factors": {
                "positive": result.get("positive_factors", []),
                "negative": result.get("negative_factors", []),
            },
        }
    except (json.JSONDecodeError, IndexError):
        return {"likelihood": 50.0, "factors": {"positive": [], "negative": []}}


def _basic_cv_parse(text: str) -> Dict[str, Any]:
    lines = text.strip().split("\n")
    return {
        "name": lines[0] if lines else "Unknown",
        "summary": text[:500],
        "skills": _extract_common_skills(text),
    }


def _basic_jd_parse(text: str) -> Dict[str, Any]:
    return {
        "skills_required": _extract_common_skills(text),
        "skills_nice_to_have": [],
        "responsibilities": [],
        "requirements": [],
    }


def _extract_common_skills(text: str) -> List[str]:
    common_skills = [
        "python", "javascript", "typescript", "react", "node.js", "java", "c++",
        "aws", "azure", "gcp", "docker", "kubernetes", "sql", "postgresql",
        "mongodb", "redis", "graphql", "rest", "api", "git", "ci/cd",
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "html", "css", "vue", "angular", "next.js", "fastapi", "django",
        "flask", "spring", "microservices", "agile", "scrum",
        "data science", "analytics", "tableau", "power bi",
        "linux", "terraform", "ansible", "jenkins", "github actions",
    ]
    text_lower = text.lower()
    found = [skill for skill in common_skills if skill in text_lower]
    return found
