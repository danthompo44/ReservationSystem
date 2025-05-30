from typing import List, Literal

from bson import ObjectId
from pydantic import BaseModel


class ParameterType(BaseModel):
    name: str
    type: Literal['string', 'int', 'boolean', 'float', 'list', 'date']


class SchemaModel(BaseModel):
    name: str
    parameters: List[ParameterType]


class InsertedSchema(BaseModel):
    name: str
    parameters: List[ParameterType]
    data: dict