from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer

from basemodels.schema_base_models import PyObjectId


class CreateObjectResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    message: str
    data: dict

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    @field_serializer("data")
    def serialize_data(self, v: dict, _info):
        for key, value in v.items():
            if isinstance(value, ObjectId):
                v[key] = str(value)
        return v

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude_none": True
    }


# TODO - Update to have Object ID base basemodel
class CreateObjectRequest(BaseModel):
    schema_id: PyObjectId
    fields: dict

    # Field serializer tell FastAPI how to serialise ObjectIds in the response
    @field_serializer("schema_id")
    def serialize_object_id(self, v: ObjectId, _info):
        return str(v)

    @field_serializer("fields")
    def serialize_data(self, v: dict, _info):
        for key, value in v.items():
            if isinstance(value, ObjectId):
                v[key] = str(value)
        return v


    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude_none": True
    }