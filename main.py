import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_prometheus_pusher import FastApiPusher

from router.awsl_producers import router as producer_router
from router.awsl_pic import router as pic_router
from router.awsl_blob import router as blob_router
from router.health_check import router as health_check_router
from router.moyuban import router as moyu_router
from router.ios_faker import router as ios_faker_router
from router.chatgpt import router as chatgpt_router
from router.config import settings


app = FastAPI()


if settings.enable_prometheus:
    @app.on_event("startup")
    async def startup():
        FastApiPusher(
            excluded_handlers=["health_check", "docs"]
        ).start(
            app, settings.prometheus_host,
            settings.instance_name,
            repeat_seconds=settings.repeat_seconds
        )


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return all(
            path not in record.getMessage()
            for path in ["/health_check", "/docs", "/openapi.json"]
        )


# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

if os.environ.get("DEV"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(producer_router, prefix="")
app.include_router(pic_router, prefix="")
app.include_router(blob_router, prefix="")
app.include_router(health_check_router, prefix="")
app.include_router(moyu_router, prefix="")
app.include_router(ios_faker_router, prefix="")
app.include_router(chatgpt_router, prefix="")
