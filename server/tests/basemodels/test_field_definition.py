import pytest
from src.basemodels.schema_base_models import FieldDefinition


def test_validate_constraints_string_with_min_max():
    """Test that a ValueError is raised when a string FieldDefinition is created with min and max constraints."""
    with pytest.raises(ValueError, match="min and max constraints are not supported for strings"):
        FieldDefinition(type="str", min=1, max=10)


def test_validate_constraints_string_with_regex():
    """Test that a ValueError is raised when a string FieldDefinition is created with regex and min_length or
     max_length constraints."""
    with pytest.raises(ValueError, match="regex and min_length and max_length not supported for strings"):
        FieldDefinition(type="str", min_length=1, max_length=10, regex=r"\d{15}")


def test_validate_constraints_int_with_min_length():
    """Test that a ValueError is raised when an integer FieldDefinition is created with min_length constraint."""
    with pytest.raises(ValueError, match="min_length, max_length and regex constraints are not "
                                         "supported for integers and floats"):
        FieldDefinition(type="int", min_length=1)


def test_validate_constraints_float_with_min_length():
    """Test that a ValueError is raised when a float FieldDefinition is created with min_length constraint."""
    with pytest.raises(ValueError, match="min_length, max_length and regex constraints are not supported "
                                         "for integers and floats"):
        FieldDefinition(type="float", min_length=1)


def test_validate_constraints_boolean_with_min_max():
    """Test that a ValueError is raised when a boolean FieldDefinition is created with min and max constraints."""
    with pytest.raises(ValueError, match="min, max and regex constraints are not supported for booleans"):
        FieldDefinition(type="boolean", min=0, max=1)


def test_validate_constraints_list_with_min_max():
    """Test that a ValueError is raised when a list FieldDefinition is created with min and max constraints."""
    with pytest.raises(ValueError, match="min and max constraints are not supported for lists"):
        FieldDefinition(type="list", min=1, max=10)


def test_validate_constraints_valid_field_definition():
    """Test that a valid FieldDefinition does not raise any exceptions during validation."""
    field_def = FieldDefinition(type="str", required=True)
    field_def.model_dump(exclude_none=True)
