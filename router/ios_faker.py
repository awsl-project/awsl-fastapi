import logging

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse
from router.awsl_blob import ProducerPhotos, producer_photos

from router.models.pydantic_models import Blob, Blobs

from .tools import DBSession
from .models.models import Mblog, AwslBlob
from .config import WB_URL_PREFIX, settings
from .response_models import BlobItem, Message


class Review(BaseModel):
    version: str


router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/in_review", response_model=Review, tags=["ios faker"])
def in_review():
    return Review(version=settings.ios_in_review)


@router.get("/list_in_review", response_model=List[BlobItem], responses={404: {"model": Message}}, tags=["ios faker"])
def list_in_review(limit: Optional[int] = 10, offset: Optional[int] = 0):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content=Message(message="to large limit = {}".format(limit))
        )
    _logger.info("list_in_review get limit %s offest %s" % (limit, offset))
    session = DBSession()
    try:
        blobs = session.query(AwslBlob).join(Mblog, AwslBlob.awsl_id == Mblog.id).filter(
            Mblog.uid.in_(settings.ios_in_review_uids)
        ).order_by(AwslBlob.awsl_id.desc()).limit(limit).offset(offset).all()
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
    finally:
        session.close()
    return res


@router.get("/list_count_review", response_model=int, tags=["ios faker"])
def list_count_review() -> int:
    session = DBSession()
    try:
        res = session.query(func.count(AwslBlob.id)).join(Mblog, AwslBlob.awsl_id == Mblog.id).filter(
            Mblog.uid.in_(settings.ios_in_review_uids)
        ).one_or_none()
        return int(res[0]) if res else 0
    finally:
        session.close()


@router.get(
    "/producer_photos_in_review",
    response_model=List[ProducerPhotos],
    responses={404: {"model": Message}}, tags=["ios faker"]
)
def producer_photos_in_review(limit: Optional[int] = 5):
    return producer_photos(uids=settings.ios_in_review_uids, limit=limit)
