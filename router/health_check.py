import logging

from fastapi import APIRouter, status

router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/health_check")
def health_check():
    _logger.info("health check")
    return status.HTTP_200_OK
