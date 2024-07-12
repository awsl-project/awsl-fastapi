import logging

from typing import List

from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import APIRouter

from config import WB_PROFILE, settings
from .tools import Tools
from .response_models import ProducerItem, ProducerRes, Message
from src.db.base import DBClientBase

router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/producers", response_model=List[ProducerRes], tags=["producers"])
def awsl_producers():
    return DBClientBase.get_client().get_awsl_producers()


@router.post("/producers", response_model=bool, responses={404: {"model": Message}}, tags=["producers"])
def add_awsl_producers(producer: ProducerItem):
    if not producer.uid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "uid is None"}
        )
    if not settings.allow_empty_keyword and not producer.keyword:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "keyword is null"}
        )

    profile = Tools.wb_get(url=WB_PROFILE.format(producer.uid))
    if not profile or not profile.get("data", {}).get("user"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "No weibo user uid = {}".format(producer.uid)}
        )
    DBClientBase.get_client().add_awsl_producers(producer=producer, profile=profile)
    return True


@router.get("/in_verification_producers", response_model=List[ProducerRes], tags=["producers"])
def awsl_in_verification_producers():
    return DBClientBase.get_client().awsl_in_verification_producers()


@router.post("/approve_producers", response_model=bool, responses={404: {"model": Message}}, tags=["producers"])
def approve_producers(uid: str, token: str):
    if not uid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "uid is None"}
        )
    if token != settings.token:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "token is not correct"}
        )

    DBClientBase.get_client().approve_producers(uid=uid)
    return True
