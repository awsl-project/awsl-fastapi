import os
from typing import List

from pydantic import BaseSettings


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
    ios_in_review_path: str
    ios_in_review_uids: List[str]
    ios_in_review_fake_path: str
    db_url: str
    origin: str
    cdn: str
    enable_prometheus: bool
    prometheus_host: str
    instance_name: str
    repeat_seconds: int

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
