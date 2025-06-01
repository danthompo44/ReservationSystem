from datetime import datetime
from typing import Dict, Any, Literal

from pydantic import constr, conint, confloat, create_model, BaseModel


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

def build_constrained_field(fields: Dict[str, Any]):
    type_name: str = fields.get("type")
    required: bool = fields.get("required", False)
    enum: list = fields.get("enum")

    # Create field constraints
    field_args = {}
    if enum:
        return Literal[tuple(enum)], ... if required else None

    if type_name == "str":
        return (
            constr(
                min_length=fields.get("min_length"),
                max_length=fields.get("max_length"),
                pattern=fields.get("regex")
            ),
            ... if required else None,
        )

    if type_name == "int":
        return (
            conint(
                ge=fields.get("min"),
                le=fields.get("max")
            ),
            ... if required else None,
        )

    if type_name == "float":
        return confloat(
            ge=fields.get("min"),
            le=fields.get("max")
        )

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