"""Email service for sending daily digest briefings."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List

from jinja2 import Template

from app.core.config import settings


DIGEST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }
        .header h1 { margin: 0 0 5px 0; font-size: 24px; }
        .header p { margin: 0; opacity: 0.9; font-size: 14px; }
        .job-card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #667eea; }
        .job-title { font-size: 18px; font-weight: 600; color: #1a1a2e; margin: 0 0 5px 0; }
        .job-company { font-size: 14px; color: #555; margin: 0 0 10px 0; }
        .job-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
        .badge-match { background: #e8f5e9; color: #2e7d32; }
        .badge-salary { background: #e3f2fd; color: #1565c0; }
        .badge-acceptance { background: #fce4ec; color: #c62828; }
        .badge-location { background: #f3e5f5; color: #6a1b9a; }
        .explanation { font-size: 13px; color: #666; font-style: italic; margin-top: 8px; }
        .apply-link { display: inline-block; margin-top: 10px; padding: 8px 16px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: 500; }
        .footer { text-align: center; padding: 20px; color: #888; font-size: 12px; }
        .pulse { background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .pulse h3 { color: #667eea; margin: 0 0 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Your Daily Job Briefing</h1>
        <p>{{ date }} | {{ job_count }} new opportunities matched</p>
    </div>

    {% for job in jobs %}
    <div class="job-card">
        <h3 class="job-title">{{ job.title }}</h3>
        <p class="job-company">{{ job.company }} {% if job.location %} | {{ job.location }}{% endif %}</p>
        <div class="job-meta">
            <span class="badge badge-match">Match: {{ job.match_score|round(0)|int }}%</span>
            {% if job.estimated_salary_mid %}
            <span class="badge badge-salary">${{ (job.estimated_salary_mid / 1000)|round(0)|int }}k est.</span>
            {% endif %}
            {% if job.acceptance_likelihood %}
            <span class="badge badge-acceptance">Acceptance: {{ job.acceptance_likelihood|round(0)|int }}%</span>
            {% endif %}
            {% if job.work_mode %}
            <span class="badge badge-location">{{ job.work_mode|capitalize }}</span>
            {% endif %}
        </div>
        {% if job.match_explanation %}
        <p class="explanation">{{ job.match_explanation }}</p>
        {% endif %}
        <a href="{{ job.url }}" class="apply-link">View & Apply</a>
    </div>
    {% endfor %}

    <div class="pulse">
        <h3>Market Pulse</h3>
        <p>{{ job_count }} new roles matched your profile today across {{ sources|length }} sources. Average match score: {{ avg_score|round(1) }}%.</p>
    </div>

    <div class="footer">
        <p>Job Matcher | Your personal career intelligence system</p>
        <p>Manage preferences and give feedback on your <a href="http://localhost:3000">dashboard</a>.</p>
    </div>
</body>
</html>
"""


async def send_digest_email(jobs: List) -> bool:
    """Send the daily digest email."""
    if not settings.SMTP_USER or not settings.DIGEST_EMAIL_TO:
        print("[Email] SMTP not configured. Skipping email send.")
        print("[Email] Would have sent digest with these jobs:")
        for job in jobs:
            print(f"  - {job.title} at {job.company} (Match: {job.match_score}%)")
        return False

    template = Template(DIGEST_TEMPLATE)
    sources = list(set(job.source for job in jobs))
    avg_score = sum(job.match_score or 0 for job in jobs) / max(1, len(jobs))

    html_content = template.render(
        jobs=jobs,
        date=datetime.now().strftime("%A, %B %d, %Y"),
        job_count=len(jobs),
        sources=sources,
        avg_score=avg_score,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Job Briefing - {len(jobs)} Matches ({datetime.now().strftime('%b %d')})"
    msg["From"] = settings.SMTP_USER
    msg["To"] = settings.DIGEST_EMAIL_TO

    text_content = f"Daily Job Briefing - {len(jobs)} new matches\n\n"
    for job in jobs:
        text_content += f"* {job.title} at {job.company}\n"
        text_content += f"  Match: {job.match_score}% | Salary: ~${(job.estimated_salary_mid or 0) // 1000}k\n"
        text_content += f"  {job.url}\n\n"

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False,
            start_tls=True,
        )
        print(f"[Email] Digest sent to {settings.DIGEST_EMAIL_TO}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send: {e}")
        return False
