import json
import logging
import requests
import base64
from typing import List
from urllib.parse import urlparse
from sqlalchemy.dialects.mysql.mysqlconnector import MySQLDialect_mysqlconnector
from sqlalchemy.orm import Query
from mysql.connector.conversion import MySQLConverter

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from config import WB_URL_PREFIX, settings
from src.db.tidb_models import TiDBResponse
from src.models.models import AwslProducer
from src.models.pydantic_models import Blob, Blobs
from src.response_models import BlobItem, PicInfo, ProducerItem, ProducerRes

from .base import DBClientBase

_logger = logging.getLogger(__name__)
dialect = MySQLDialect_mysqlconnector()
sql_escape = MySQLConverter().escape


class TidbHttpClient(DBClientBase):

    _type = "tidb_http"

    req_url = None
    session = None

    @classmethod
    def init_db_client(cls):
        db_url_parsed = urlparse(settings.db_url)
        cls.session = requests.Session()
        cls.req_url = f"https://http-{db_url_parsed.hostname}/v1beta/sql"
        basic_auth = f"{db_url_parsed.username}:{db_url_parsed.password}"
        basic_auth = base64.b64encode(basic_auth.encode()).decode()
        cls.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': "serverless-js/0.1.1",
            'Authorization': f"Basic {basic_auth}",
            'TiDB-Database': db_url_parsed.path.replace("/", ""),
            'Accept-Encoding': 'gzip'
        })

    @classmethod
    def post_query(cls, query: str) -> dict:
        _logger.info("tidb post_query %s" % query)
        res = cls.session.post(cls.req_url, json={"query": query})
        if res.status_code >= 400:
            _logger.error("tidb post_query error %s" % res.text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="TiDB query error"
            )
        tidb_res = TiDBResponse.model_validate(res.json())
        return tidb_res.get_json()

    @classmethod
    def get_awsl_producers(cls) -> List[ProducerRes]:
        producers_json = cls.post_query(
            "SELECT uid, name FROM awsl_producer"
            " WHERE in_verification IS NOT true AND deleted IS NOT true"
        )
        return producers_json

    @classmethod
    def add_awsl_producers(cls, producer: ProducerItem, profile: dict) -> None:
        res = cls.post_query(
            f"SELECT * FROM awsl_producer WHERE uid = '{sql_escape(producer.uid)}'"
        )
        if res:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Weibo user uid = {} already exist".format(producer.uid)}
            )
        insert_sql = """
        INSERT INTO awsl_producer
            (uid, name, keyword, profile, in_verification)
        VALUES('%s', '%s', '%s', '%s', True)
        """ % (
            sql_escape(producer.uid),
            sql_escape(profile["data"]['user']["screen_name"]),
            sql_escape(producer.keyword or ""),
            sql_escape(json.dumps(profile["data"]['user'])),
        )
        cls.post_query(insert_sql)
        _logger.info("awsl add awsl_producer done %s" % profile["data"]['user']["screen_name"])

    @classmethod
    def awsl_in_verification_producers(cls) -> List[ProducerRes]:
        res_query = Query(AwslProducer).filter(
            AwslProducer.in_verification.is_(True)
        ).filter(
            AwslProducer.deleted.isnot(True)
        )
        producers_json = cls.post_query(str(res_query.statement))
        producers = [
            AwslProducer(**producer)
            for producer in producers_json
        ]
        res = [{
            "uid": producer.uid,
            "name": producer.name
        } for producer in producers]
        return res

    @classmethod
    def approve_producers(cls, uid: str) -> None:
        awsl_producer_query = Query(
            AwslProducer
        ).filter(
            AwslProducer.uid == uid
        ).filter(
            AwslProducer.in_verification.is_(True)
        ).filter(
            AwslProducer.deleted.isnot(True)
        )
        compiled_query = awsl_producer_query.statement.compile(
            dialect=dialect,
            compile_kwargs={"literal_binds": True}
        )
        awsl_producer = cls.post_query(str(compiled_query))
        if not awsl_producer:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Weibo user uid = {} in_verification not exist".format(uid)
                }
            )
        awsl_producer = AwslProducer(**awsl_producer[0])
        cls.post_query(
            f"UPDATE awsl_producer SET in_verification = False WHERE id = '{awsl_producer.id}'"
        )
        _logger.info("awsl approve awsl_producer done %s" % awsl_producer.name)

    @classmethod
    def awsl_list(cls, uid: str, limit: int, offset: int) -> List[BlobItem]:
        blobs_json = cls.post_query(
            "SELECT awsl_blob.pic_id, awsl_blob.pic_info,"
            " awsl_mblog.re_user_id, awsl_mblog.re_mblogid"
            " FROM awsl_blob"
            " INNER JOIN awsl_mblog ON awsl_blob.awsl_id=awsl_mblog.id"
            + (f" WHERE awsl_mblog.uid = '{sql_escape(uid)}'" if uid else "")
            + " ORDER BY awsl_blob.awsl_id DESC"
            f" LIMIT {sql_escape(offset)}, {sql_escape(limit)}"
        )
        res = [BlobItem(
            wb_url=WB_URL_PREFIX.format(blob['re_user_id'], blob['re_mblogid']),
            pic_id=blob['pic_id'],
            pic_info={
                blob_key: Blob(
                    url=blob_pic.url.replace(settings.origin, settings.cdn),
                    width=blob_pic.width, height=blob_pic.height
                )
                for blob_key, blob_pic in Blobs.model_validate_json(blob['pic_info']).blobs.items()
            }
        ) for blob in blobs_json]
        return res

    @classmethod
    def awsl_list_count(cls, uid: str) -> int:
        res = cls.post_query(
            "SELECT count(1) AS count FROM awsl_blob"
            + (
                " INNER JOIN awsl_mblog ON awsl_blob.awsl_id=awsl_mblog.id"
                f" WHERE awsl_mblog.uid = '{sql_escape(uid)}'"
            ) if uid else ""
        )
        if not res or not res[0] or not res[0].get("count"):
            return 0
        return res[0]["count"]

    @classmethod
    def awsl_random(cls) -> str:
        res = cls.post_query("SELECT pic_info FROM awsl_blob ORDER BY rand() LIMIT 1")
        if not res or not res[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No random pic found"
            )
        url_dict = Blobs.model_validate_json(res[0]['pic_info']).blobs
        return url_dict["original"].url

    @classmethod
    def awsl_random_json(cls) -> str:
        blobs_json = cls.post_query(
            "SELECT awsl_blob.pic_id, awsl_blob.pic_info,"
            " awsl_mblog.re_user_id, awsl_mblog.re_mblogid"
            " FROM awsl_blob"
            " INNER JOIN awsl_mblog ON awsl_blob.awsl_id=awsl_mblog.id"
            " ORDER BY rand() LIMIT 1"
        )
        if not blobs_json:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No random pic found"
            )
        blob = blobs_json[0]
        return BlobItem(
            wb_url=WB_URL_PREFIX.format(blob['re_user_id'], blob['re_mblogid']),
            pic_id=blob['pic_id'],
            pic_info={
                blob_key: Blob(
                    url=blob_pic.url.replace(settings.origin, settings.cdn),
                    width=blob_pic.width, height=blob_pic.height
                )
                for blob_key, blob_pic in Blobs.model_validate_json(blob['pic_info']).blobs.items()
            }
        )

    @classmethod
    def awsl_pic_list(cls, uid: str, limit: int, offset: int) -> List[BlobItem]:
        res_json = cls.post_query(
            "SELECT awsl_pic.pic_id, awsl_pic.pic_info,"
            " awsl_mblog.re_user_id, awsl_mblog.re_mblogid"
            " FROM awsl_pic"
            " INNER JOIN awsl_mblog ON awsl_pic.awsl_id=awsl_mblog.id"
            + (f" WHERE awsl_mblog.uid = '{sql_escape(uid)}'" if uid else "")
            + " ORDER BY awsl_pic.awsl_id DESC"
            f" LIMIT {sql_escape(offset)}, {sql_escape(limit)}"
        )
        res = [BlobItem(
            wb_url=WB_URL_PREFIX.format(pic['re_user_id'], pic['re_mblogid']),
            pic_id=pic['pic_id'],
            pic_info=PicInfo.model_validate_json(pic['pic_info']).root
        ) for pic in res_json]
        return res

    @classmethod
    def awsl_pic_list_count(cls, uid: str) -> int:
        res = cls.post_query(
            "SELECT count(1) AS count FROM awsl_pic"
            + (
                " INNER JOIN awsl_mblog ON awsl_pic.awsl_id=awsl_mblog.id"
                f" WHERE awsl_mblog.uid = '{sql_escape(uid)}'"
            ) if uid else ""
        )
        if not res or not res[0] or not res[0].get("count"):
            return 0
        return res[0]["count"]

    @classmethod
    def awsl_pic_random(cls) -> str:
        res = cls.post_query("SELECT pic_info FROM awsl_pic ORDER BY rand() LIMIT 1")
        if not res or not res[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No random pic found"
            )
        url_dict = PicInfo.model_validate_json(res[0]['pic_info']).root
        return url_dict["original"].url

    @classmethod
    def awsl_pic_random_json(cls) -> str:
        res_json = cls.post_query(
            "SELECT awsl_pic.pic_id, awsl_pic.pic_info,"
            " awsl_mblog.re_user_id, awsl_mblog.re_mblogid"
            " FROM awsl_pic"
            " INNER JOIN awsl_mblog ON awsl_pic.awsl_id=awsl_mblog.id"
            " ORDER BY rand() LIMIT 1"
        )
        if not res_json:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No random pic found"
            )
        res = res_json[0]
        return BlobItem(
            wb_url=WB_URL_PREFIX.format(res['re_user_id'], res['re_mblogid']),
            pic_id=res['pic_id'],
            pic_info=PicInfo.model_validate_json(res['pic_info']).root
        )
