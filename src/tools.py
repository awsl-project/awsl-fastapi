import logging
import requests

from config import wb_headers

_logger = logging.getLogger(__name__)


class Tools:

    @staticmethod
    def wb_get(url) -> dict:
        try:
            res = requests.get(url=url, headers=wb_headers.get())
            return res.json()
        except Exception as e:
            _logger.exception(e)
            return None
