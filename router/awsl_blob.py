import logging
import random

from typing import List, Optional
from fastapi import APIRouter
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse

from router.models.pydantic_models import Blob, Blobs

from .tools import DBSession
from .models.models import Mblog, AwslBlob
from .config import WB_URL_PREFIX, settings
from .response_models import BlobItem, Message


router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/v2/list", response_model=List[BlobItem], responses={404: {"model": Message}})
def awsl_list(uid: Optional[str] = "", limit: Optional[int] = 10, offset: Optional[int] = 0):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content=Message(message="to large limit = {}".format(limit))
        )
    _logger.info("list get uid %s limit %s offest %s" % (uid, limit, offset))
    session = DBSession()
    try:
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
    finally:
        session.close()
    return res


@router.get("/v2/list_count", response_model=int)
def awsl_list_count(uid: Optional[str] = "") -> int:
    session = DBSession()
    try:
        res = session.query(func.count(AwslBlob.id)).filter(
            Mblog.uid == uid
        ).one() if uid else session.query(func.count(AwslBlob.id)).one()
    finally:
        session.close()
    return int(res[0]) if res else 0


@router.get("/v2/random", response_model=str)
def awsl_random() -> str:
    session = DBSession()
    try:
        blob = session.query(AwslBlob).order_by(
            func.rand()
        ).limit(1).one()
        url_dict = Blobs.parse_raw(blob.pic_info).blobs
        return url_dict["original"].url
    finally:
        session.close()
