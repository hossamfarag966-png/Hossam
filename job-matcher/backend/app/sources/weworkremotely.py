"""We Work Remotely job source connector. RSS feeds, no auth required."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import feedparser

from app.sources.base import JobSourceConnector


class WeWorkRemotelyConnector(JobSourceConnector):
    source_name = "weworkremotely"

    FEEDS = [
        "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
        "https://weworkremotely.com/categories/remote-data-jobs.rss",
        "https://weworkremotely.com/categories/remote-design-jobs.rss",
        "https://weworkremotely.com/categories/remote-product-jobs.rss",
    ]

    async def fetch_jobs(self, keywords: List[str] = None, location: str = None) -> List[Dict[str, Any]]:
        jobs = []

        async with httpx.AsyncClient(timeout=30) as client:
            headers = {"User-Agent": "JobMatcher/1.0 (personal job search tool)"}

            for feed_url in self.FEEDS:
                try:
                    response = await client.get(feed_url, headers=headers)
                    response.raise_for_status()
                    feed_content = response.text
                except (httpx.HTTPError, Exception) as e:
                    print(f"[WWR] Error fetching feed {feed_url}: {e}")
                    continue

                feed = feedparser.parse(feed_content)

                for entry in feed.entries:
                    if keywords:
                        job_text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
                        if not any(kw.lower() in job_text for kw in keywords):
                            continue

                    title_parts = entry.get("title", "").split(":", 1)
                    if len(title_parts) == 2:
                        company = title_parts[0].strip()
                        title = title_parts[1].strip()
                    else:
                        company = "Unknown"
                        title = entry.get("title", "Unknown Title")

                    posted_at = None
                    if entry.get("published_parsed"):
                        try:
                            posted_at = datetime(*entry.published_parsed[:6])
                        except (ValueError, TypeError):
                            pass

                    description = _strip_html(entry.get("summary", ""))

                    job = {
                        "external_id": f"wwr_{entry.get('id', entry.get('link', ''))}",
                        "title": title,
                        "company": company,
                        "company_logo": "",
                        "url": entry.get("link", ""),
                        "description_raw": description,
                        "location": "Remote",
                        "work_mode": "remote",
                        "posted_at": posted_at,
                        "tags": [tag.get("term", "") for tag in entry.get("tags", [])],
                        "salary_min": None,
                        "salary_max": None,
                    }
                    jobs.append(job)

        seen = set()
        unique_jobs = []
        for job in jobs:
            if job["external_id"] not in seen:
                seen.add(job["external_id"])
                unique_jobs.append(job)

        print(f"[WWR] Fetched {len(unique_jobs)} jobs")
        return unique_jobs


def _strip_html(text: str) -> str:
    from bs4 import BeautifulSoup
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator="\n", strip=True)
