import logging

from typing import List, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .response_models import BlobItem, Message
from src.db.base import DBClientBase

router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/awsl_pic/list", response_model=List[BlobItem], responses={404: {"model": Message}}, tags=["Awsl Pic"])
def awsl_pic_list(uid: Optional[str] = "", limit: Optional[int] = 10, offset: Optional[int] = 0):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content=Message(message="to large limit = {}".format(limit))
        )
    return DBClientBase.get_client().awsl_pic_list(uid, limit, offset)


@router.get("/awsl_pic/list_count", response_model=int, tags=["Awsl Pic"])
def awsl_pic_list_count(uid: Optional[str] = "") -> int:
    return DBClientBase.get_client().awsl_pic_list_count(uid)


@router.get("/awsl_pic/random", response_model=str, tags=["Awsl Pic"])
def awsl_pic_random(uid: Optional[str] = "") -> str:
    return DBClientBase.get_client().awsl_pic_random(uid)


@router.get("/awsl_pic/random_json", response_model=BlobItem, tags=["Awsl Pic"])
def awsl_pic_random_json(uid: Optional[str] = "") -> str:
    return DBClientBase.get_client().awsl_pic_random_json(uid)
