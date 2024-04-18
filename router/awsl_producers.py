import logging

from typing import List

from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import APIRouter

from .models.models import AwslProducer
from .config import WB_PROFILE, settings
from .tools import Tools, DBSession
from .response_models import ProducerItem, ProducerRes, Message


router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/producers", response_model=List[ProducerRes], tags=["producers"])
def awsl_producers():
    with DBSession() as session:
        producers = session.query(
            AwslProducer
        ).filter(
            AwslProducer.in_verification.isnot(True)
        ).filter(
            AwslProducer.deleted.isnot(True)
        ).all()
        res = [{
            "uid": producer.uid,
            "name": producer.name
        } for producer in producers]
        return res


@router.post("/producers", response_model=bool, responses={404: {"model": Message}}, tags=["producers"])
def add_awsl_producers(producer: ProducerItem):
    if not producer.uid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "uid is None"}
        )
    if not producer.keyword:
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

    with DBSession() as session:
        res = session.query(AwslProducer).filter(
            AwslProducer.uid == producer.uid).one_or_none()
        if res:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Weibo user uid = {} already exist".format(producer.uid)}
            )
        awsl_producer = AwslProducer(
            uid=producer.uid,
            keyword=producer.keyword or "",
            name=profile["data"]['user']["screen_name"],
            profile=profile["data"]['user'],
            in_verification=True
        )
        session.add(awsl_producer)
        _logger.info("awsl add awsl_producer done %s" % awsl_producer.name)
        session.commit()
    return True


@router.get("/in_verification_producers", response_model=List[ProducerRes], tags=["producers"])
def awsl_in_verification_producers():
    with DBSession() as session:
        producers = session.query(
            AwslProducer
        ).filter(
            AwslProducer.in_verification.is_(True)
        ).filter(
            AwslProducer.deleted.isnot(True)
        ).all()
        res = [{
            "uid": producer.uid,
            "name": producer.name
        } for producer in producers]
        return res


@router.post("/approve_producers", response_model=bool, responses={404: {"model": Message}}, tags=["producers"])
def add_approve_producers(uid: str, token: str):
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

    with DBSession() as session:
        awsl_producer = session.query(
            AwslProducer
        ).filter(
            AwslProducer.uid == uid
        ).filter(
            AwslProducer.in_verification.is_(True)
        ).filter(
            AwslProducer.deleted.isnot(True)
        ).one_or_none()
        if not awsl_producer:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Weibo user uid = {} in_verification not exist".format(uid)
                }
            )
        awsl_producer.in_verification = False
        _logger.info("awsl approve awsl_producer done %s" % awsl_producer.name)
        session.commit()
        return True
