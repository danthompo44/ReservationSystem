import pytest
from server.src.basemodels.schema_base_models import FieldDefinition

def test_validate_constraints_string_with_min_max():
    with pytest.raises(ValueError, match="min and max constraints are not supported for strings"):
        FieldDefinition(type="str", min=1, max=10)

def test_validate_constraints_int_with_min_length():
    with pytest.raises(ValueError, match="min_length, max_length and regex constraints are not supported for integers and floats"):
        FieldDefinition(type="int", min_length=1)

def test_validate_constraints_float_with_min_length():
    with pytest.raises(ValueError, match="min_length, max_length and regex constraints are not supported for integers and floats"):
        FieldDefinition(type="float", min_length=1)

def test_validate_constraints_boolean_with_min_max():
    with pytest.raises(ValueError, match="min, max and regex constraints are not supported for booleans"):
        FieldDefinition(type="boolean", min=0, max=1)

def test_validate_constraints_list_with_min_max():
    with pytest.raises(ValueError, match="min and max constraints are not supported for lists"):
        FieldDefinition(type="list", min=1, max=10)

def test_validate_constraints_valid_field_definition():
    field_def = FieldDefinition(type="str", required=True)
    assert field_def.validate_constraints() == field_def
