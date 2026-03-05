# AWSL FastAPI

Weibo content aggregation API. Manages producers (Weibo users) and serves their image content.

## Quick Start

```bash
cp .env.example .env
# Edit .env with your config
pip install -r requirements.txt
python main.py
```

API docs at `http://localhost:8000/docs`

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `db_url` | Yes | Database connection string, e.g. `mysql+mysqlconnector://user:pass@host/db` |
| `token` | Yes | Admin API Bearer Token |
| `cookie_sub` | No | Weibo SUB cookie (fallback, prefer `/admin/wb_headers` API) |
| `db_client_type` | No | `mysql` (default) or `tidb_http` |
| `use_db_pool` | No | Enable connection pooling (default: `true`) |
| `db_pool_size` | No | Pool size (default: `20`) |
| `origin` | No | Original image domain for CDN replacement |
| `cdn` | No | CDN domain to replace origin |
| `CORS` | No | Set to any value to enable CORS |
| `ENV_FILE` | No | Path to env file (default: `.env`) |

## Docker

```bash
docker build -f docker/dockerfile -t awsl-fastapi .
docker compose -f docker/docker-compose.yml up
```

Docker Compose includes MySQL, Prometheus, Pushgateway, and Grafana.

## Deployment

- **Vercel**: Auto-deploys on push to `main`
- **Docker**: Pushes to `ghcr.io` on git tag (`*.*.*`)
