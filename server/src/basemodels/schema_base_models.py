from datetime import datetime
from typing import List, Literal, Any, Optional, Dict

from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler, field_serializer, model_validator
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic models.

    This class extends the default ObjectId from bson to provide
    additional validation and serialization capabilities for use
    in Pydantic models.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        """Get the Pydantic core schema for the PyObjectId.

        Args:
            source_type (Any): The source type for the schema.
            handler (GetCoreSchemaHandler): The handler for getting core schemas.

        Returns:
            core_schema.CoreSchema: The core schema for the PyObjectId.
        """
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([core_schema.str_schema(), core_schema.is_instance_schema(ObjectId)])
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """Validate the value as a valid ObjectId.

        Args:
            v (Any): The value to validate.

        Raises:
            ValueError: If the value is not a valid ObjectId.

        Returns:
            ObjectId: The validated ObjectId.
        """
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    def __str__(self) -> str:
        """Return the string representation of the ObjectId.

        Returns:
            str: The string representation of the ObjectId.
        """
        return str(super().__str__())


class FieldDefinition(BaseModel):
    """Class representing a field definition in a schema.

    This class defines the properties of a field in a schema,
    including its type, constraints, and validation rules.

    Attributes:
        type (Optional[Literal['str', 'int', 'boolean', 'float', 'list', 'date']]): The type of the field.
        required (Optional[bool]): Indicates if the field is required.
        min_length (Optional[int]): Minimum length for string fields.
        max_length (Optional[int]): Maximum length for string fields.
        regex (Optional[str]): Regular expression for string validation.
        enum (Optional[List[str]]): List of valid values for the field.
        description (Optional[str]): Description of the field.
        default (Optional[Any]): Default value for the field.
        min (Optional[float]): Minimum value for numeric fields.
        max (Optional[float]): Maximum value for numeric fields.
    """

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

    def _validate_str(self):
        """Validate constraints specific to string fields.

        Raises:
            ValueError: If min/max or regex constraints are invalid for strings.
        """
        if self.min is not None or self.max is not None:
            raise ValueError("min and max constraints are not supported for strings")

        if self.regex is not None:
            if self.min_length is not None or self.max_length is not None:
                raise ValueError("regex and min_length and max_length not supported for strings")

    def _validate_number(self):
        """Validate constraints specific to numeric fields.

        Raises:
            ValueError: If min_length, max_length, or regex constraints are invalid for numbers.
        """
        if self.min_length is not None or self.max_length is not None or self.regex is not None:
            raise ValueError("min_length, max_length and regex constraints are not supported for integers and floats")

    def _validate_boolean(self):
        """Validate constraints specific to boolean fields.

        Raises:
            ValueError: If min, max, or regex constraints are invalid for booleans.
        """
        if self.min is not None or self.max is not None or self.regex is not None:
            raise ValueError("min, max and regex constraints are not supported for booleans")

    def _validate_list(self):
        """Validate constraints specific to list fields.

        Raises:
            ValueError: If min or max constraints are invalid for lists.
        """
        if self.min is not None or self.max is not None:
            raise ValueError("min and max constraints are not supported for lists")

    @model_validator(mode="after")
    def constraints(self) -> 'FieldDefinition':
        """Validate the field constraints based on the field type.

        Raises:
            ValueError: If any constraints are invalid based on the field type.

        Returns:
            FieldDefinition: The validated FieldDefinition instance.
        """
        if self.type == "str":
            self._validate_str()

        if self.type in ["int", "float"]:
            self._validate_number()

        if self.type == "boolean":
            self._validate_boolean()

        if self.type == "list":
            self._validate_list()

        return self


class CreateSchemaRequest(BaseModel):
    """Represents a request to insert a schema.

    This class is responsible for defining the structure of a schema insertion request,
    including the schema name and its associated fields. It supports various configurations
    for parsing the schema data and is particularly useful in applications requiring
    schema validation and management.

    Attributes:
        schema_name (str): The name of the schema to be inserted.
        fields (Dict[str, FieldDefinition]): A dictionary containing the field definitions for the schema,
            where the keys are field names, and the values are `FieldDefinition` objects
            describing the field's properties.
    """
    schema_name: str
    fields: Dict[str, FieldDefinition]

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude_none": True
    }


class SchemaUpdateRequest(BaseModel):
    """Represents a request to update a schema.

    This class is designed to encapsulate the necessary information for
    updating a schema, including its name and associated field definitions.
    It leverages the Pydantic BaseModel for data validation and serialization.

    Attributes:
        schema_name (Optional[str]): The name of the schema to update. It is optional and can be
            left as None if not provided.
        fields (Optional[Dict[str, FieldDefinition]]): A dictionary of field definitions associated with the schema.
    """
    schema_name: Optional[str] = None
    fields: Optional[Dict[str, FieldDefinition]] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude_none": True
    }


class SchemaDeletedResponse(BaseModel):
    """Response model for deleting a schema.

    This class represents the response returned when a schema is successfully deleted.
    It includes the ID of the deleted schema and a detail message.

    Attributes:
        id (PyObjectId): The ID of the deleted schema.
        detail (str): A message indicating the result of the deletion.
    """
    id: PyObjectId = Field(alias="_id")
    detail: str

    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        """Serialize the ObjectId to a string for the response.

        Args:
            v (ObjectId): The ObjectId to serialize.
            _info: Additional information for serialization.

        Returns:
            str: The serialized string representation of the ObjectId.
        """
        return str(v)

    model_config = {
        "populate_by_name": True,
        "json_encoder": {ObjectId: str}
    }


class InsertedSchema(CreateSchemaRequest):
    """Represents a schema that has been inserted into the database.

    This class extends the CreateSchemaRequest to include additional fields
    that are generated upon insertion, such as the ID and timestamps.

    Attributes:
        id (PyObjectId): The ID of the inserted schema.
        created_at (datetime): The timestamp when the schema was created.
        updated_at (datetime): The timestamp when the schema was last updated.
    """
    id: PyObjectId = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        """Serialize the ObjectId to a string for the response.

        Args:
            v (ObjectId): The ObjectId to serialize.
            _info: Additional information for serialization.

        Returns:
            str: The serialized string representation of the ObjectId.
        """
        return str(v)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CreatedSchemaResponse(BaseModel):
    """Response model for creating a schema.

    This class represents the response returned when a schema is successfully created.
    It includes the ID of the created schema, a message, and the schema data.

    Attributes:
        id (PyObjectId): The ID of the created schema.
        message (str): A message indicating the result of the creation.
        data (InsertedSchema): The data of the created schema.
    """
    id: PyObjectId = Field(alias="_id")
    message: str
    data: InsertedSchema

    @field_serializer("id")
    def serialize_object_id(self, v: ObjectId, _info):
        """Serialize the ObjectId to a string for the response.

        Args:
            v (ObjectId): The ObjectId to serialize.
            _info: Additional information for serialization.

        Returns:
            str: The serialized string representation of the ObjectId.
        """
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
