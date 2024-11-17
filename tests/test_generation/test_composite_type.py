from textwrap import dedent

from ..utils import Testdir


def test_composite_type_not_supported(testdir: Testdir) -> None:
    """Composite types are now supported"""
    schema = (
        testdir.default_generator
        + """
        datasource db {{
            provider = "mongodb"
            url      = env("foo")
        }}

        model User {{
            id       String @id @map("_id")
            prouuuut String
            settings UserSettings
        }}

        type UserSettings {{
            theme String
        }}
    """
    )
    testdir.generate(schema=schema)

    client_types_path = testdir.path / 'prisma' / 'types.py'
    client_types = client_types_path.read_text()

    assert (
        dedent("""
        class UserSettings(TypedDict, total=False):
            theme: _str
    """).strip()
        in client_types
    )

    for line in client_types.splitlines():
        line = line.strip()
        if line.startswith('settings:'):
            assert line == "settings: 'UserSettings'"
