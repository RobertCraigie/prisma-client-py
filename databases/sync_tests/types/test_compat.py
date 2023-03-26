from prisma.models import Types


def test_json_schema_compatible() -> None:
    """Ensure a JSON Schema can be created for all types"""
    # this is just a catch-all to check if any errors are raised during schema creation
    # actual schema definitions are tested individually for each type
    schema = Types.schema()
    assert isinstance(schema, dict)
