from datetime import datetime
from typing import List, Literal, Any, Optional, Dict

from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler, field_serializer, model_validator
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
        "exclude_none": True
    }

    type: Optional[Literal['str', 'int', 'boolean', 'float', 'list', 'date']] = "str"
    required: Optional[bool] = True
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
        if self.type == "str":
            if self.min is not None or self.max is not None:
                raise ValueError("min and max constraints are not supported for strings")

            if self.regex is not None:
                if self.min_length is not None or self.max_length is not None:
                    raise ValueError("regex and min_length and max_length not supported for strings")

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


class CreateSchemaRequest(BaseModel):
    """
    Represents a request to insert a schema.

    This class is responsible for defining the structure of a schema insertion request,
    including the schema name and its associated fields. It supports various configurations
    for parsing the schema data and is particularly useful in applications requiring
    schema validation and management.

    :ivar schema_name: The name of the schema to be inserted.
    :type schema_name: str
    :ivar fields: A dictionary containing the field definitions for the schema,
        where the keys are field names, and the values are `FieldDefinition` objects
        describing the field's properties.
    :type fields: Dict[str, FieldDefinition]
    """
    schema_name: str
    fields: Dict[str, FieldDefinition]

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude_none": True
    }


class SchemaUpdateRequest(BaseModel):
    """
    Represents a request to update a schema.

    This class is designed to encapsulate the necessary information for
    updating a schema, including its name and associated field definitions.
    It leverages the Pydantic BaseModel for data validation and serialization.

    :ivar name: The name of the schema to update. It is optional and can be
        left as None if not provided.
    :type name: Optional[str]
    :ivar fields: A list of field definitions associated with the schema.
        It is optional and can be None.
    :type fields: Optional[List[FieldDefinition]]
    """
    schema_name: Optional[str] = None
    fields: Optional[Dict[str, FieldDefinition]] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude_none": True
    }


# TODO - Update to have Object ID base basemodel
class SchemaDeletedResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    detail: str

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    model_config = {
        "populate_by_name": True,
        "json_encoder": {ObjectId: str}
    }


class InsertedSchema(CreateSchemaRequest):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CreatedSchemaResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    message: str
    data: InsertedSchema

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude_none": True
    }


example_create_request = CreateSchemaRequest(schema_name="SIM", fields={
    "imsi": FieldDefinition(type="str", required=True, regex=r"$2343(0|3)\d{10}"),
    "msisdn": FieldDefinition(type="str", required=True, regex=r"44\d{9}"),
    "environment": FieldDefinition(type="str", required=True, enum=["Dev_1", "Dev_2", "Stable_1", "Stable_2", "Production"]),
    "use_count": FieldDefinition(type="int", required=True, default=0, min=0, max=10000),
})