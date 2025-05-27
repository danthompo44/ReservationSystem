from typing import List, Literal

from pydantic import BaseModel


class ParameterType(BaseModel):
    name: str
    type: Literal['string', 'int', 'boolean', 'float', 'list', 'date']


class ObjectSchema(BaseModel):
    name: str
    parameters: List[ParameterType]
