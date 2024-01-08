from ..utils import Testdir


def test_field_map(testdir: Testdir) -> None:
    """Mapping fields does not rename pydantic model fields"""

    # NOTE: this just tests that map can be used with Prisma Client Python
    #       prisma handles mapping for us
    def tests() -> None:  # mark: filedef
        from prisma.models import User

        def test_field_map() -> None:  # pyright: ignore[reportUnusedFunction]
            """Correct model field name access"""
            user = User(id='1', my_field='bar', foo_field='baz')  # type: ignore[call-arg]
            assert user.id == '1'
            assert user.my_field == 'bar'  # type: ignore[attr-defined]
            assert user.foo_field == 'baz'  # type: ignore[attr-defined]

    schema = """
        datasource db {{
          provider = "sqlite"
          url      = "file:dev.db"
        }}

        generator db {{
          provider = "coverage run -m prisma"
          output = "{output}"
          {options}
        }}

        model User {{
            id        String @id
            my_field  String @map("myField")
            foo_field String @map(name: "fooField")
        }}
    """
    testdir.generate(schema=schema)
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)
