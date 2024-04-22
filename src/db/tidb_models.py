import json
from typing import Any, List, Optional
from pydantic import BaseModel


class Field(BaseModel):
    name: str
    type: str
    nullable: bool


class TiDBResponse(BaseModel):
    types: Optional[List[Field]] = None
    rows: Optional[List[List[Optional[str]]]] = None

    def get_json(self) -> dict:
        if not self.rows or not self.types:
            return []
        return [
            {field.name: cast(field, value) for field, value in zip(self.types, row)}
            for row in self.rows
        ]


def cast(field: Field, value: Optional[str]) -> Any:
    if value is None:
        return None

    if field.type in (
        'TINYINT',
        'UNSIGNED TINYINT',
        'SMALLINT',
        'UNSIGNED SMALLINT',
        'MEDIUMINT',
        'UNSIGNED MEDIUMINT',
        'INT',
        'UNSIGNED INT',
        'YEAR'
    ):
        return int(value)
    if field.type in ('FLOAT', 'DOUBLE'):
        return float(value)
    if field.type in (
        'BLOB',
        'TINYBLOB',
        'MEDIUMBLOB',
        'LONGBLOB',
        'BINARY',
        'VARBINARY',
        'BIT'
    ):
        raise NotImplementedError(f'Unsupported type: {field.type}')
    if field.type == 'JSON':
        return json.loads(value)
    return value
