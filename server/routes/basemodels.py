from datetime import datetime
from typing import List, Literal, Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler, field_serializer
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([core_schema.str_schema(), core_schema.is_instance_schema(ObjectId)])
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    def __str__(self) -> str:
        return str(super().__str__())

class ParameterType(BaseModel):
    name: str
    type: Literal['string', 'int', 'boolean', 'float', 'list', 'date']


class SchemaInsertRequest(BaseModel):
    name: str
    parameters: List[ParameterType]

class SchemaUpdateRequest(BaseModel):
    name: Optional[str] = None
    parameters: Optional[List[ParameterType]] = None


# TODO - Update to have Object ID base basemodel
class SchemaDeletedResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    detail: str

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class InsertedSchema(SchemaInsertRequest):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}




class CreatedSchemaResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    message: str
    data: InsertedSchema

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}