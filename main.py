import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.awsl_producers import router as producer_router
from src.awsl_blob import router as blob_router
from src.awsl_pic import router as pic_router
from src.health_check import router as health_check_router


app = FastAPI(title="AWSL API", version="0.1.0", )


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return all(
            path not in record.getMessage()
            for path in ["/health_check", "/docs", "/openapi.json"]
        )


# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

if os.environ.get("CORS"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(producer_router, prefix="")
app.include_router(blob_router, prefix="")
app.include_router(pic_router, prefix="")
app.include_router(health_check_router, prefix="")

# 301 Redirect to /docs
app.get("/")(lambda: RedirectResponse("/docs"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
