import os
import logging

from pydantic import Field
from pydantic_settings import BaseSettings


WB_DATA_URL = "https://weibo.com/ajax/statuses/mymblog?uid={}&page="
WB_SHOW_URL = "https://weibo.com/ajax/statuses/show?id={}"
WB_COOKIE = "SUB={}"
WB_PROFILE = "https://weibo.com/ajax/profile/info?uid={}"
WB_URL_PREFIX = "https://weibo.com/{}/{}"
WB_COOKIE = "SUB={}"
CHUNK_SIZE = 9


class Settings(BaseSettings):
    cookie_sub: str = ""
    allow_empty_keyword: bool = False
    token: str = Field(deafult="token", exclude=True)
    db_client_type: str = "mysql"
    db_url: str = Field(deafult="", exclude=True)
    use_db_pool: bool = True
    origin: str = ""
    cdn: str = ""

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
_logger.info(settings.model_dump_json(indent=2))
