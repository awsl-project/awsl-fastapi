import os
import logging

from pydantic_settings import BaseSettings


WB_DATA_URL = "https://weibo.com/ajax/statuses/mymblog?uid={}&page="
WB_SHOW_URL = "https://weibo.com/ajax/statuses/show?id={}"
WB_COOKIE = "SUB={}"
WB_PROFILE = "https://weibo.com/ajax/profile/info?uid={}"
WB_URL_PREFIX = "https://weibo.com/{}/{}"
WB_COOKIE = "SUB={}"
CHUNK_SIZE = 9


class Settings(BaseSettings):
    cookie_sub: str
    token: str
    db_url: str
    origin: str
    cdn: str

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
_logger.info(settings.model_dump_json(indent=2))
