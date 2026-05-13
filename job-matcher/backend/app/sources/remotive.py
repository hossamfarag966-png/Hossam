"""Remotive job source connector. Public API, no auth required."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from app.sources.base import JobSourceConnector


class RemotiveConnector(JobSourceConnector):
    source_name = "remotive"
    API_URL = "https://remotive.com/api/remote-jobs"

    async def fetch_jobs(self, keywords: List[str] = None, location: str = None) -> List[Dict[str, Any]]:
        jobs = []

        async with httpx.AsyncClient(timeout=30) as client:
            headers = {"User-Agent": "JobMatcher/1.0 (personal job search tool)"}
            categories_to_fetch = ["software-dev", "data", "devops", "product"]

            for category in categories_to_fetch:
                try:
                    params = {"category": category, "limit": 50}
                    response = await client.get(self.API_URL, params=params, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                except (httpx.HTTPError, Exception) as e:
                    print(f"[Remotive] Error fetching {category}: {e}")
                    continue

                for item in data.get("jobs", []):
                    if keywords:
                        job_text = f"{item.get('title', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}".lower()
                        if not any(kw.lower() in job_text for kw in keywords):
                            continue

                    posted_at = None
                    if item.get("publication_date"):
                        try:
                            posted_at = datetime.fromisoformat(item["publication_date"].replace("Z", "+00:00"))
                        except (ValueError, TypeError):
                            pass

                    job = {
                        "external_id": f"remotive_{item.get('id', '')}",
                        "title": item.get("title", "Unknown Title"),
                        "company": item.get("company_name", "Unknown Company"),
                        "company_logo": item.get("company_logo_url", ""),
                        "url": item.get("url", ""),
                        "description_raw": _strip_html(item.get("description", "")),
                        "location": item.get("candidate_required_location", "Remote"),
                        "work_mode": "remote",
                        "posted_at": posted_at,
                        "tags": item.get("tags", []),
                        "salary_min": _parse_salary(item.get("salary")),
                        "salary_max": None,
                        "category": item.get("category", ""),
                    }
                    jobs.append(job)

        print(f"[Remotive] Fetched {len(jobs)} jobs")
        return jobs


def _strip_html(text: str) -> str:
    from bs4 import BeautifulSoup
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def _parse_salary(value) -> Optional[int]:
    if not value:
        return None
    try:
        import re
        numbers = re.findall(r"\d+", str(value).replace(",", ""))
        if numbers:
            return int(numbers[0])
    except (ValueError, TypeError):
        pass
    return None
