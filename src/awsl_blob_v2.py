import logging

from typing import List, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .response_models import BlobItem, Message
from src.db.base import DBClientBase

router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/v2/list", response_model=List[BlobItem], responses={404: {"model": Message}}, tags=["AwslV2"])
def awsl_v2_list(uid: Optional[str] = "", limit: Optional[int] = 10, offset: Optional[int] = 0):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content=Message(message="to large limit = {}".format(limit))
        )
    return DBClientBase.get_client().awsl_v2_list(uid, limit, offset)


@router.get("/v2/list_count", response_model=int, tags=["AwslV2"])
def awsl_v2_list_count(uid: Optional[str] = "") -> int:
    return DBClientBase.get_client().awsl_v2_list_count(uid)


@router.get("/v2/random", response_model=str, tags=["AwslV2"])
def awsl_v2_random(uid: Optional[str] = "") -> str:
    return DBClientBase.get_client().awsl_v2_random(uid)


@router.get("/v2/random_json", response_model=BlobItem, tags=["AwslV2"])
def awsl_v2_random_json(uid: Optional[str] = "") -> BlobItem:
    return DBClientBase.get_client().awsl_v2_random_json(uid)
