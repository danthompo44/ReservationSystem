from datetime import datetime
from typing import Dict, Any, Literal, Annotated

from pydantic import constr, conint, confloat, create_model, BaseModel, Field


def datetime_as_string(d: datetime):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


schema = {
    "schema_name": "schema-1",
    "fields": {
        "name": {
            "type": "str",
            "required": True,
            "min_length": 1,
            "max_length": 100,
            "regex": "^[a-zA-Z0-9]+$",
            "description": "Name of the person"
        },
        "price": {
            "type": "float",
            "required": True,
            "min": 0.01,
            "max": 99.9
        },
        "category": {
            "type": "str",
            "required": True,
            "enum": ["book", "movie", "music", "sports", "other"]
        }
    }
}

def __build_num_constraints(fields: dict, required: bool, type_name: str):
    constraints = {}
    if fields.get("min") is not None:
        constraints["ge"] = fields["min"]
    if fields.get("max") is not None:
        constraints["le"] = fields["max"]
    
    field_type = float if type_name == "float" else int
    return (
        Annotated[field_type, Field(**constraints)],
        ... if required else None,
    )


def build_constrained_field(fields: Dict[str, Any]):
    type_name: str = fields.get("type")
    required: bool = fields.get("required", False)
    enum: list = fields.get("enum")

    # Handle enum fields
    if enum:
        return Literal[tuple(enum)], ... if required else None

    # Handle string fields
    if type_name == "str":
        constraints = {}
        if fields.get("min_length") is not None:
            constraints["min_length"] = fields["min_length"]
        if fields.get("max_length") is not None:
            constraints["max_length"] = fields["max_length"]
        if fields.get("regex") is not None:
            constraints["pattern"] = fields["regex"]
        return (
            Annotated[str, Field(**constraints)],
            ... if required else None,
        )

    # Handle integer and float fields
    if type_name == "int" or type_name == "float":
        return __build_num_constraints(fields, required, type_name)

    # Handle basic types
    base_type = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool
    }.get(type_name, str)

    return base_type, ... if required else None


def build_pydantic_model(name: str, fields: Dict[str, Any]):
    model_fields = {}

    for field_name, field_def in fields.items():
        model_fields[field_name] = build_constrained_field(field_def)

    return create_model(name, **model_fields)


model = build_pydantic_model(schema["schema_name"], schema["fields"])
model_instance = model(name="John", price=10.0, category="book")
print("########################  SCHEMA #################################")
print(model_instance.model_json_schema())
print("########################  DATA  #################################")
print(model_instance.model_dump())