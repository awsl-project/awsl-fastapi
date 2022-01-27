from typing import Dict
from pydantic import BaseModel

from .models.pydantic_models import Blob


class ProducerItem(BaseModel):
    uid: str
    keyword: str


class ProducerRes(BaseModel):
    uid: str
    name: str


class PicItem(BaseModel):
    wb_url: str
    pic_info: dict


class BlobItem(BaseModel):
    pic_id: str
    wb_url: str
    pic_info: Dict[str, Blob]


class Message(BaseModel):
    message: str
