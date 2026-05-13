# Job Matcher - Personal Job Intelligence System

A personal job-matching system that aggregates opportunities from multiple platforms, scores them against your profile, and delivers a daily morning briefing with ranked opportunities, salary estimates, and acceptance-likelihood scores.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Next.js        │────▶│  FastAPI      │────▶│ PostgreSQL  │
│  Dashboard      │     │  Backend      │     │ + pgvector  │
│  (port 3000)    │     │  (port 8000)  │     │             │
└─────────────────┘     └──────┬───────┘     └─────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
              ┌──────────┐ ┌────────┐ ┌────────┐
              │  Celery  │ │ Redis  │ │ OpenAI │
              │  Worker  │ │        │ │  API   │
              └──────────┘ └────────┘ └────────┘
```

## Features

- **Profile Ingestion**: Upload CV (PDF/DOCX) or LinkedIn data export (ZIP)
- **3 Job Sources**: RemoteOK, Remotive, We Work Remotely (all ToS-compliant)
- **Smart Matching**: Hybrid scoring with semantic similarity + skill coverage + seniority alignment
- **Salary Estimation**: LLM-powered salary range prediction (low/mid/high)
- **Acceptance Likelihood**: Probability scoring with positive/negative factors
- **Daily Email Digest**: Beautiful HTML briefing at your configured time
- **Feedback Loop**: Mark jobs as Interested/Applied/Rejected to improve recommendations
- **Web Dashboard**: Browse, filter, sort, and manage all job matches

## Quick Start

### 1. Clone and configure

```bash
cd job-matcher
cp .env.example .env
# Edit .env with your API keys
```

### 2. Required API Keys

| Key | Purpose | How to get |
|-----|---------|-----------|
| `OPENAI_API_KEY` | Embeddings + JD parsing + salary/acceptance estimation | [platform.openai.com](https://platform.openai.com) |
| `SMTP_USER` / `SMTP_PASSWORD` | Daily digest email delivery | Gmail App Password or SendGrid |
| `DIGEST_EMAIL_TO` | Where to receive daily briefing | Your email address |

> **Note**: The system works without an OpenAI key (uses keyword matching fallback), but matching quality is significantly better with it.

### 3. Run with Docker Compose

```bash
docker compose up --build
```

This starts:
- **Backend API**: http://localhost:8000
- **Dashboard**: http://localhost:3000
- **PostgreSQL + pgvector**: port 5432
- **Redis**: port 6379
- **Celery Worker**: processes jobs in background
- **Celery Beat**: schedules periodic tasks

### 4. Set up your profile

1. Open http://localhost:3000/settings
2. Upload your CV (PDF/DOCX) or LinkedIn data export ZIP
3. Set your preferences (target roles, locations, salary, etc.)
4. Click "Fetch New Jobs" on the dashboard

### 5. Daily Digest

The system automatically:
- Fetches new jobs every 6 hours
- Sends a morning digest email at your configured time (default 7:00 AM UTC)

You can trigger both manually from the dashboard.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/profile` | Get user profile |
| POST | `/api/profile/cv` | Upload and parse CV |
| POST | `/api/profile/linkedin` | Upload LinkedIn export |
| PUT | `/api/profile/preferences` | Update job preferences |
| GET | `/api/jobs` | List jobs (with filters) |
| GET | `/api/jobs/{id}` | Get single job |
| PATCH | `/api/jobs/{id}/status` | Update job feedback |
| GET | `/api/stats` | Dashboard statistics |
| POST | `/api/fetch-jobs` | Trigger job fetching |
| POST | `/api/send-digest` | Trigger digest email |

## Matching Algorithm

The match score (0-100) is computed as:

```
Score = Semantic Similarity x 35%
      + Skill Coverage x 40%
      + Seniority Alignment x 15%
      + Hard Filter Bonus x 10%
```

**Hard filters** (instant disqualification):
- Salary below minimum
- Deal-breaker keywords present
- Incompatible work mode

**Skill coverage** uses fuzzy matching with alias resolution (e.g., "JS" = "JavaScript", "K8s" = "Kubernetes").

## Job Sources

| Source | Method | Rate Limit |
|--------|--------|-----------|
| RemoteOK | Public JSON API | ~1 req/min |
| Remotive | Public REST API | Respectful |
| We Work Remotely | RSS feeds | Respectful |

## Extending with New Sources

Create a new connector in `backend/app/sources/`:

```python
from app.sources.base import JobSourceConnector

class MySourceConnector(JobSourceConnector):
    source_name = "mysource"

    async def fetch_jobs(self, keywords=None, location=None):
        # Fetch and return list of job dicts
        return [...]
```

Then add it to the worker's connector list in `backend/app/worker.py`.

## Roadmap

- [ ] Add Greenhouse/Lever/Ashby ATS API connectors
- [ ] Wuzzuf & Bayt (MENA market) integration
- [ ] Indeed official API connector
- [ ] Telegram/WhatsApp bot delivery channel
- [ ] Auto-apply via pre-filled forms
- [ ] Interview prep briefings per company
- [ ] Feedback-weighted reranking (online learning)
- [ ] Salary data enrichment from Levels.fyi
- [ ] Company health signals (layoff trackers, growth indicators)

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Celery
- **Database**: PostgreSQL + pgvector for semantic search
- **Queue**: Redis + Celery Beat
- **LLM**: OpenAI GPT-4o-mini + text-embedding-3-small
- **Frontend**: Next.js 14, React, Tailwind CSS
- **Deployment**: Docker Compose

## Privacy

- All data stays in your local PostgreSQL database
- Your CV is never sent to third parties (only to OpenAI for parsing if configured)
- No tracking, no analytics, no data sharing
- Designed as a personal single-user tool
