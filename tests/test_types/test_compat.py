from syrupy.assertion import SnapshotAssertion

from prisma.models import Types


def test_json_schema_compatible(snapshot: SnapshotAssertion) -> None:
    """Ensure a JSON Schema can be created for all types"""
    schema = Types.schema()
    assert schema == snapshot
