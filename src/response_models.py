from typing import Any, Dict
from pydantic import BaseModel, RootModel, model_validator

from .models.pydantic_models import Blob


class ProducerItem(BaseModel):
    uid: str
    keyword: str


class ProducerRes(BaseModel):
    uid: str
    name: str


class BlobItem(BaseModel):
    pic_id: str
    wb_url: str
    pic_info: Dict[str, Blob]


class PicInfo(RootModel):
    root: Dict[str, Blob]

    @model_validator(mode='before')
    @classmethod
    def pre_process_and_validate(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return {
            k: v
            for k, v in values.items()
            if isinstance(v, dict)
            and all(
                kk in v.keys()
                for kk in Blob.model_fields.keys()
            )
        }


class Message(BaseModel):
    message: str
