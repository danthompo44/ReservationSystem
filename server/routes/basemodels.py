from typing import List, Literal

from bson import ObjectId
from pydantic import BaseModel


class ParameterType(BaseModel):
    name: str
    type: Literal['string', 'int', 'boolean', 'float', 'list', 'date']


class SchemaInsertRequest(BaseModel):
    name: str
    parameters: List[ParameterType]


class InsertedSchema(SchemaInsertRequest):
    created_at: str


class InsertedSchemaResponse(BaseModel):
    id: str
    message: str
    data: InsertedSchema