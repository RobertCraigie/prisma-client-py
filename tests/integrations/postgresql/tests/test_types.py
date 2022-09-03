from prisma.models import Types


def test_json_schema_compatible() -> None:
    """Ensure a JSON Schema definition can be created"""
    assert isinstance(Types.schema(), dict)
