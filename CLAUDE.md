# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run locally
python main.py
# Or
uvicorn main:app --host 0.0.0.0 --port 8000

# Lint
flake8 .    # max-line-length=120

# Docker
docker build -f docker/dockerfile -t awsl-fastapi .
docker compose -f docker/docker-compose.yml up
```

No test suite exists in this project.

## Architecture

FastAPI REST API for Weibo content aggregation. Collects producer (Weibo user) profiles and serves their image content.

### Key Patterns

- **DB abstraction**: `src/db/base.py` defines `DBClientBase` with metaclass auto-registration. Providers (`mysql_provider.py`, `tidb_http_provider.py`) register via `_type` class attribute. Selected at runtime by `settings.db_client_type`.
- **Models submodule**: `src/models/` is a **git submodule** (separate repo). ORM models live there. Commit model changes in the submodule first, then update the ref in this repo.
- **Admin auth**: All admin endpoints under `/admin` prefix use Bearer Token via `HTTPBearer` + `hmac.compare_digest`. Token value from `settings.token`.
- **WeiboHeaders**: Thread-safe singleton in `config.py` (`wb_headers`). Loaded from DB on startup, persisted on update. DB writes happen outside the lock.
- **Config**: Pydantic `BaseSettings` in `config.py`, loaded from `.env`. Sensitive fields (`token`, `db_url`) have `exclude=True`.

### Deployment

- **Vercel**: Serverless Python, configured in `vercel.json`. CI deploys two projects in parallel (`.github/workflows/main.yml`).
- **Docker**: Released to `ghcr.io` on git tags (`.github/workflows/release.yml`).

### Constants

Weibo API URLs and `WB_HEADERS_KEY` are centralized in `config.py`.
