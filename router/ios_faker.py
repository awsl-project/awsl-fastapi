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


class FakeBlobItems(BaseModel):
    __root__: List[BlobItem]


FAKE_UID = "0"
router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/in_review", response_model=Review, tags=["ios faker"])
def in_review():
    return Review.parse_file(settings.ios_in_review_path)


@router.post("/in_review", response_model=bool, tags=["ios faker"])
def set_review(review: Review):
    with open(settings.ios_in_review_path, "w") as f:
        f.write(review.json())
    return True


@router.get("/list_in_review", response_model=List[BlobItem], responses={404: {"model": Message}}, tags=["ios faker"])
def list_in_review(uid: Optional[str] = "", limit: Optional[int] = 10, offset: Optional[int] = 0):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content=Message(message="to large limit = {}".format(limit))
        )
    _logger.info("list_in_review get limit %s offest %s" % (limit, offset))
    session = DBSession()
    try:
        res = []
        if uid == FAKE_UID or not uid:
            res = FakeBlobItems.parse_file(
                settings.ios_in_review_fake_path).__root__
            if offset+limit <= len(res):
                return res[offset:offset+limit]
            if offset >= len(res):
                offset -= len(res)
                res = []
            elif res:
                res = res[offset:]
                limit -= len(res)
                offset = 0
        blobs = session.query(AwslBlob).join(Mblog, AwslBlob.awsl_id == Mblog.id).filter(
            Mblog.uid.in_(settings.ios_in_review_uids)
            if not uid else Mblog.uid == uid
        ).order_by(AwslBlob.awsl_id.desc()).limit(limit).offset(offset).all()
        return res + [
            BlobItem(
                wb_url=WB_URL_PREFIX.format(
                    blob.awsl_mblog.re_user_id, blob.awsl_mblog.re_mblogid),
                pic_id=blob.pic_id,
                pic_info={
                    blob_key: Blob(
                        url=blob_pic.url.replace(
                            settings.origin, settings.cdn),
                        width=blob_pic.width, height=blob_pic.height
                    )
                    for blob_key, blob_pic in Blobs.parse_raw(blob.pic_info).blobs.items()
                }
            ) for blob in blobs if blob.awsl_mblog]
    finally:
        session.close()


@router.get("/list_count_review", response_model=int, tags=["ios faker"])
def list_count_review(uid: Optional[str] = "", ) -> int:
    session = DBSession()
    try:
        fake = FakeBlobItems.parse_file(
            settings.ios_in_review_fake_path).__root__
        if uid == FAKE_UID:
            return len(fake)
        res = session.query(func.count(AwslBlob.id)).join(Mblog, AwslBlob.awsl_id == Mblog.id).filter(
            Mblog.uid.in_(settings.ios_in_review_uids)
            if not uid else Mblog.uid == uid
        ).one_or_none()
        res = int(res[0]) if res else 0
        if not uid:
            res += len(fake)
        return res
    finally:
        session.close()


@router.get(
    "/producer_photos_in_review",
    response_model=List[ProducerPhotos],
    responses={404: {"model": Message}}, tags=["ios faker"]
)
def producer_photos_in_review(limit: Optional[int] = 5):
    return [
        ProducerPhotos(
            uid=FAKE_UID,
            name="春风抚绿芭蕉",
            photos=FakeBlobItems.parse_file(
                settings.ios_in_review_fake_path).__root__
        )
    ][:limit] + producer_photos(
        uids=settings.ios_in_review_uids, limit=limit
    )
