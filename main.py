import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.awsl_producers import router as producer_router
from router.awsl_pic import router as pic_router
from router.awsl_blob import router as blob_router

app = FastAPI()

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
