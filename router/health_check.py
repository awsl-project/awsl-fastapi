import logging

from fastapi import APIRouter, status

router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/health_check", tags=["health check"])
def health_check():
    return status.HTTP_200_OK
