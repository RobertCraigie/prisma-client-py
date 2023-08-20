from prisma.models import Types
from prisma._compat import model_json_schema


def test_json_schema_compatible() -> None:
    """Ensure a JSON Schema can be created for all types"""
    # this is just a catch-all to check if any errors are raised during schema creation
    # actual schema definitions are tested individually for each type
    schema = model_json_schema(Types)
    assert isinstance(schema, dict)
