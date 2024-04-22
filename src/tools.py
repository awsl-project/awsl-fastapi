import logging
import requests

from config import settings, WB_COOKIE

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
