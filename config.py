import json
import os
import logging
import threading
from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings


WB_DATA_URL = "https://weibo.com/ajax/statuses/mymblog?uid={}&page="
WB_SHOW_URL = "https://weibo.com/ajax/statuses/show?id={}"
WB_PROFILE = "https://weibo.com/ajax/profile/info?uid={}"
WB_URL_PREFIX = "https://weibo.com/{}/{}"
CHUNK_SIZE = 9

WB_HEADERS_KEY = "wb_headers"


class Settings(BaseSettings):
    cookie_sub: str = ""
    allow_empty_keyword: bool = False
    token: str = Field(deafult="token", exclude=True)
    db_client_type: str = "mysql"
    db_url: str = Field(deafult="", exclude=True)
    use_db_pool: bool = True
    db_pool_size: int = 20
    origin: str = ""
    cdn: str = ""

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
_logger.info(settings.model_dump_json(indent=2))


class WeiboHeaders:
    """Thread-safe mutable store for Weibo API request headers, persisted to DB."""

    def __init__(self):
        self._lock = threading.Lock()
        self._headers: Dict[str, str] = {
            "cookie": f"SUB={settings.cookie_sub}"
        } if settings.cookie_sub else {}

    def load_from_db(self):
        from src.db.base import DBClientBase
        try:
            raw = DBClientBase.get_client().get_setting(WB_HEADERS_KEY)
            if raw:
                with self._lock:
                    self._headers = json.loads(raw)
                _logger.info("wb_headers loaded from db")
        except Exception as e:
            _logger.warning("failed to load wb_headers from db: %s", e)

    def _save_to_db(self, data: Dict[str, str]):
        from src.db.base import DBClientBase
        try:
            DBClientBase.get_client().set_setting(WB_HEADERS_KEY, json.dumps(data))
        except Exception as e:
            _logger.warning("failed to save wb_headers to db: %s", e)

    def get(self) -> Dict[str, str]:
        with self._lock:
            return dict(self._headers)

    def update(self, headers: Dict[str, str]):
        with self._lock:
            self._headers.update(headers)
            snapshot = dict(self._headers)
        self._save_to_db(snapshot)

    def replace(self, headers: Dict[str, str]):
        snapshot = dict(headers)
        with self._lock:
            self._headers = snapshot
        self._save_to_db(snapshot)


wb_headers = WeiboHeaders()
