import logging
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings, WB_COOKIE

engine = create_engine(settings.db_url, pool_size=100)
DBSession = sessionmaker(bind=engine)

_logger = logging.getLogger(__name__)


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
