from datetime import datetime
from typing import List, Literal, Any, Optional, Dict

from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler, field_serializer, root_validator, model_validator
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

class FieldDefinition(BaseModel):

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "extra": "allow"
    }

    type: Literal['str', 'int', 'boolean', 'float', 'list', 'date']
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    regex: Optional[str] = None
    enum: Optional[List[str]] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    min: Optional[float] = None
    max: Optional[float] = None

    @model_validator(mode="after")
    def validate_constraints(self) -> 'FieldDefinition':
        if self.type == "string":
            if self.min is not None or self.max is not None:
                raise ValueError("min and max constraints are not supported for strings")

        if self.type in ["int", "float"]:
            if self.min_length is not None or self.max_length is not None or self.regex is not None:
                raise ValueError("min_length, max_length and regex constraints are not supported for integers and floats")

        if self.type == "boolean":
            if self.min is not None or self.max is not None or self.regex is not None:
                raise ValueError("min, max and regex constraints are not supported for booleans")

        if self.type == "list":
            # TODO - Is regex required for validation?
            if self.min is not None or self.max is not None:
                raise ValueError("min and max constraints are not supported for lists")

        return self


class SchemaInsertRequest(BaseModel):
    schema_name: str
    fields: Dict[str, FieldDefinition]

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {"examples": [{}]},  # Optional: for OpenAPI documentation
    }


class SchemaUpdateRequest(BaseModel):
    name: Optional[str] = None
    parameters: Optional[List[FieldDefinition]] = None


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