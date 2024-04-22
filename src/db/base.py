from typing import List
from fastapi import HTTPException, status

from config import settings
from src.response_models import BlobItem, ProducerItem, ProducerRes


class MetaDBClient(type):

    cilent_map = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if hasattr(cls, '_type'):
            MetaDBClient.cilent_map[cls._type] = cls


class DBClientBase(metaclass=MetaDBClient):

    @staticmethod
    def get_client() -> "DBClientBase":
        cls = MetaDBClient.cilent_map.get(settings.db_client_type)
        if cls is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DB type not supported"
            )
        cls.init_db_client()
        return cls

    @classmethod
    def init_db_client(cls):
        ...

    @classmethod
    def get_awsl_producers(cls) -> List[ProducerRes]:
        ...

    @classmethod
    def add_awsl_producers(cls, producer: ProducerItem, profile: dict) -> None:
        ...

    @classmethod
    def awsl_in_verification_producers(cls) -> List[ProducerRes]:
        ...

    @classmethod
    def approve_producers(cls, uid: str) -> None:
        ...

    @classmethod
    def awsl_list(cls, uid: str, limit: int, offset: int) -> List[BlobItem]:
        ...

    @classmethod
    def awsl_list_count(cls, uid: str) -> int:
        ...

    @classmethod
    def awsl_random(cls) -> str:
        ...

    @classmethod
    def awsl_random_json(cls) -> str:
        ...
