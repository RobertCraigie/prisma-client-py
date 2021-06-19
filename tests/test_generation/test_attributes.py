import typing
from ..utils import Testdir


def test_field_map(testdir: Testdir) -> None:
    # NOTE: this just tests that map can be used with Prisma Client Python
    #       prisma handles mapping for us
    @typing.no_type_check
    def tests() -> None:  # mark: filedef
        # pylint: disable=all
        from prisma.models import User

        def test_field_map() -> None:
            user = User(id='1', my_field='bar', foo_field='baz')
            assert user.id == '1'
            assert user.my_field == 'bar'
            assert user.foo_field == 'baz'

    schema = '''
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
    '''
    testdir.generate(schema=schema)
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)
