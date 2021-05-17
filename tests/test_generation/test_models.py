from pathlib import Path
from prisma.generator.models import Module


def test_module_serialization() -> None:
    path = Path(__file__).parent.parent.joinpath('scripts/partial_type_generator.py')
    module = Module(spec=str(path))
    assert Module.parse_raw(module.json()).spec.name == module.spec.name
