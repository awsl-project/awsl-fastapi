import logging
from typing import List

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from config import WB_URL_PREFIX, settings
from src.models.models import AwslBlob, AwslProducer, Mblog, Pic
from src.models.pydantic_models import Blob, Blobs
from src.response_models import BlobItem, PicInfo, ProducerItem, ProducerRes

from .base import DBClientBase


_logger = logging.getLogger(__name__)


class MysqlClient(DBClientBase):

    _type = "mysql"

    DBSession = None

    @classmethod
    def init_db_client(cls):
        engine = create_engine(settings.db_url, pool_size=100, pool_recycle=3600)
        cls.DBSession = sessionmaker(bind=engine)

    @classmethod
    def get_awsl_producers(cls) -> List[ProducerRes]:
        with cls.DBSession() as session:
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

    @classmethod
    def add_awsl_producers(cls, producer: ProducerItem, profile: dict) -> None:
        with cls.DBSession() as session:
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

    @classmethod
    def awsl_in_verification_producers(cls) -> List[ProducerRes]:
        with cls.DBSession() as session:
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

    @classmethod
    def approve_producers(cls, uid: str) -> None:
        with cls.DBSession() as session:
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

    @classmethod
    def awsl_list(cls, uid: str, limit: int, offset: int) -> List[BlobItem]:
        with cls.DBSession() as session:
            blobs = session.query(AwslBlob).join(
                Mblog, AwslBlob.awsl_id == Mblog.id
            ).filter(
                Mblog.uid == uid
            ).order_by(
                AwslBlob.awsl_id.desc()
            ).limit(limit).offset(offset).all() if uid else session.query(
                AwslBlob
            ).join(
                Mblog, AwslBlob.awsl_id == Mblog.id
            ).order_by(
                AwslBlob.awsl_id.desc()
            ).limit(limit).offset(offset).all()
            res = [BlobItem(
                wb_url=WB_URL_PREFIX.format(
                    blob.awsl_mblog.re_user_id, blob.awsl_mblog.re_mblogid),
                pic_id=blob.pic_id,
                pic_info={
                    blob_key: Blob(
                        url=blob_pic.url.replace(settings.origin, settings.cdn),
                        width=blob_pic.width, height=blob_pic.height
                    )
                    for blob_key, blob_pic in Blobs.model_validate_json(blob.pic_info).blobs.items()
                }
            ) for blob in blobs if blob.awsl_mblog]
            return res

    @classmethod
    def awsl_list_count(cls, uid: str) -> int:
        with cls.DBSession() as session:
            res = session.query(func.count(AwslBlob.id)).join(Mblog, AwslBlob.awsl_id == Mblog.id).filter(
                Mblog.uid == uid
            ).one() if uid else session.query(func.count(AwslBlob.id)).one()
            return int(res[0]) if res else 0

    @classmethod
    def awsl_random(cls) -> str:
        with cls.DBSession() as session:
            blob = session.query(AwslBlob).order_by(
                func.rand()
            ).limit(1).one()
            url_dict = Blobs.model_validate_json(blob.pic_info).blobs
            return url_dict["original"].url

    @classmethod
    def awsl_random_json(cls) -> str:
        with cls.DBSession() as session:
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
                    for blob_key, blob_pic in Blobs.model_validate_json(blob.pic_info).blobs.items()
                }
            )

    @classmethod
    def awsl_pic_list(cls, uid: str, limit: int, offset: int) -> List[BlobItem]:
        with cls.DBSession() as session:
            pics = session.query(Pic).join(
                Mblog, Pic.awsl_id == Mblog.id
            ).filter(
                Mblog.uid == uid
            ).order_by(
                Pic.awsl_id.desc()
            ).limit(limit).offset(offset).all() if uid else session.query(
                Pic
            ).join(
                Mblog, Pic.awsl_id == Mblog.id
            ).order_by(
                Pic.awsl_id.desc()
            ).limit(limit).offset(offset).all()
            res = [BlobItem(
                wb_url=WB_URL_PREFIX.format(
                    pic.awsl_mblog.re_user_id, pic.awsl_mblog.re_mblogid),
                pic_id=pic.pic_id,
                pic_info=PicInfo.model_validate_json(pic.pic_info).root
            ) for pic in pics if pic.awsl_mblog]
            return res

    @classmethod
    def awsl_pic_list_count(cls, uid: str) -> int:
        with cls.DBSession() as session:
            res = session.query(func.count(Pic.id)).join(
                Mblog, Pic.awsl_id == Mblog.id
            ).filter(
                Mblog.uid == uid
            ).one() if uid else session.query(func.count(Pic.id)).one()
            return int(res[0]) if res else 0

    @classmethod
    def awsl_pic_random(cls) -> str:
        with cls.DBSession() as session:
            pic = session.query(Pic).order_by(
                func.rand()
            ).limit(1).one()
            url_dict = PicInfo.model_validate_json(pic.pic_info).root
            return url_dict["original"].url

    @classmethod
    def awsl_pic_random_json(cls) -> str:
        with cls.DBSession() as session:
            blob = session.query(Pic).order_by(
                func.rand()
            ).limit(1).one()
            return BlobItem(
                wb_url=WB_URL_PREFIX.format(
                    blob.awsl_mblog.re_user_id, blob.awsl_mblog.re_mblogid),
                pic_id=blob.pic_id,
                pic_info=PicInfo.model_validate_json(blob.pic_info).root
            )
