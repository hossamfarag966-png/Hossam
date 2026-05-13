"""RemoteOK job source connector. Public JSON API, no auth required."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from app.sources.base import JobSourceConnector


class RemoteOKConnector(JobSourceConnector):
    source_name = "remoteok"
    API_URL = "https://remoteok.com/api"

    async def fetch_jobs(self, keywords: List[str] = None, location: str = None) -> List[Dict[str, Any]]:
        jobs = []

        async with httpx.AsyncClient(timeout=30) as client:
            headers = {"User-Agent": "JobMatcher/1.0 (personal job search tool)"}
            try:
                response = await client.get(self.API_URL, headers=headers)
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, Exception) as e:
                print(f"[RemoteOK] Error fetching jobs: {e}")
                return []

        for item in data[1:]:
            if not isinstance(item, dict):
                continue

            if keywords:
                job_text = f"{item.get('position', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}".lower()
                if not any(kw.lower() in job_text for kw in keywords):
                    continue

            posted_at = None
            if item.get("date"):
                try:
                    posted_at = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            job = {
                "external_id": f"remoteok_{item.get('id', '')}",
                "title": item.get("position", "Unknown Title"),
                "company": item.get("company", "Unknown Company"),
                "company_logo": item.get("company_logo", ""),
                "url": item.get("url", f"https://remoteok.com/remote-jobs/{item.get('id', '')}"),
                "description_raw": item.get("description", ""),
                "location": item.get("location", "Remote"),
                "work_mode": "remote",
                "posted_at": posted_at,
                "tags": item.get("tags", []),
                "salary_min": _parse_salary(item.get("salary_min")),
                "salary_max": _parse_salary(item.get("salary_max")),
            }
            jobs.append(job)

        print(f"[RemoteOK] Fetched {len(jobs)} jobs")
        return jobs


def _parse_salary(value) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
