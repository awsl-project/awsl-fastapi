import logging

from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse

from router.models.pydantic_models import Blob, Blobs

from .tools import DBSession
from .models.models import AwslProducer, Mblog, AwslBlob
from .config import WB_URL_PREFIX, settings
from .response_models import BlobItem, Message


router = APIRouter()
_logger = logging.getLogger(__name__)


class ProducerPhotos(BaseModel):
    uid: str
    name: str
    photos: List[BlobItem]


@router.get("/producer_photos", response_model=List[ProducerPhotos], responses={404: {"model": Message}}, tags=["AwslV2"])
def producer_photos(uids: Optional[List[str]] = None, limit: Optional[int] = 5):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content=Message(message="to large limit = {}".format(limit))
        )
    _logger.info("producer_photos get limit %s" % limit)
    with DBSession() as session:
        q = session.query(
            AwslProducer
        ).filter(
            AwslProducer.in_verification.isnot(True)
        ).filter(
            AwslProducer.deleted.isnot(True)
        )
        if uids:
            q = q.filter(AwslProducer.uid.in_(uids))
        producers = q.all()
        return [
            ProducerPhotos(
                uid=producer.uid,
                name=producer.name,
                photos=awsl_list(uid=producer.uid, limit=limit)
            ) for producer in producers
        ]


@router.get("/v2/list", response_model=List[BlobItem], responses={404: {"model": Message}}, tags=["AwslV2"])
def awsl_list(uid: Optional[str] = "", limit: Optional[int] = 10, offset: Optional[int] = 0):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content=Message(message="to large limit = {}".format(limit))
        )
    _logger.info("list get uid %s limit %s offest %s" % (uid, limit, offset))
    with DBSession() as session:
        blobs = session.query(AwslBlob).join(Mblog, AwslBlob.awsl_id == Mblog.id).filter(
            Mblog.uid == uid
        ).order_by(AwslBlob.awsl_id.desc()).limit(limit).offset(offset).all() if uid else session.query(AwslBlob).join(
            Mblog, AwslBlob.awsl_id == Mblog.id).order_by(AwslBlob.awsl_id.desc()).limit(limit).offset(offset).all()
        res = [BlobItem(
            wb_url=WB_URL_PREFIX.format(
                blob.awsl_mblog.re_user_id, blob.awsl_mblog.re_mblogid),
            pic_id=blob.pic_id,
            pic_info={
                blob_key: Blob(
                    url=blob_pic.url.replace(settings.origin, settings.cdn),
                    width=blob_pic.width, height=blob_pic.height
                )
                for blob_key, blob_pic in Blobs.parse_raw(blob.pic_info).blobs.items()
            }
        ) for blob in blobs if blob.awsl_mblog]
        return res


@router.get("/v2/list_count", response_model=int, tags=["AwslV2"])
def awsl_list_count(uid: Optional[str] = "") -> int:
    with DBSession() as session:
        res = session.query(func.count(AwslBlob.id)).join(Mblog, AwslBlob.awsl_id == Mblog.id).filter(
            Mblog.uid == uid
        ).one() if uid else session.query(func.count(AwslBlob.id)).one()
        return int(res[0]) if res else 0


@router.get("/v2/random", response_model=str, tags=["AwslV2"])
def awsl_random() -> str:
    with DBSession() as session:
        blob = session.query(AwslBlob).order_by(
            func.rand()
        ).limit(1).one()
        url_dict = Blobs.parse_raw(blob.pic_info).blobs
        return url_dict["original"].url


@router.get("/v2/random_json", response_model=BlobItem, tags=["AwslV2"])
def awsl_random_json() -> str:
    with DBSession() as session:
        blob = session.query(AwslBlob).order_by(
            func.rand()
        ).limit(1).one()
        return BlobItem(
            wb_url=WB_URL_PREFIX.format(
                blob.awsl_mblog.re_user_id, blob.awsl_mblog.re_mblogid),
            pic_id=blob.pic_id,
            pic_info={
                blob_key: Blob(
                    url=blob_pic.url.replace(settings.origin, settings.cdn),
                    width=blob_pic.width, height=blob_pic.height
                )
                for blob_key, blob_pic in Blobs.parse_raw(blob.pic_info).blobs.items()
            }
        )
