import logging
import requests

from functools import wraps
from threading import Semaphore, Timer
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models.models import ApiConfig
from .config import settings, WB_COOKIE

engine = create_engine(settings.db_url, pool_size=100, pool_recycle=3600)
DBSession = sessionmaker(bind=engine)

_logger = logging.getLogger(__name__)


def ratelimit(limit, every):
    def limitdecorator(fn):
        semaphore = Semaphore(limit)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            semaphore.acquire()
            try:
                return fn(*args, **kwargs)
            finally:
                timer = Timer(every, semaphore.release)
                timer.setDaemon(True)
                timer.start()
        return wrapper
    return limitdecorator


class Tools:

    @staticmethod
    def wb_get(url) -> dict:
        try:
            res = requests.get(url=url, headers={
                "cookie": WB_COOKIE.format(settings.cookie_sub)
            })
            return res.json()
        except Exception as e:
            _logger.exception(e)
            return None

    @staticmethod
    @lru_cache()
    def get_chatgpt_access_token():
        with DBSession() as session:
            return ApiConfig.get("chatgpt_access_token", session)

    @staticmethod
    @lru_cache()
    def get_api_token():
        with DBSession() as session:
            return ApiConfig.get("api_token", session)
