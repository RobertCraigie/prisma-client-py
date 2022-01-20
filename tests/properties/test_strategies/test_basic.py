from typing import Iterator

import pytest
from pydantic.typing import ForwardRef

from prisma._types import TypedDict

from .. import strategies
from ...utils import Testdir


class Foo(TypedDict):
    bar: 'Bar'


class Bar(TypedDict):
    baz: 'Baz'


class Baz(TypedDict):
    point: int


@pytest.fixture(autouse=True)
def reset_annotations() -> Iterator[None]:
    foo = Foo.__annotations__.copy()
    bar = Bar.__annotations__.copy()

    yield

    Foo.__annotations__ = foo
    Bar.__annotations__ = bar


def test_recursive_forwardref() -> None:
    assert Foo.__annotations__ == {'bar': ForwardRef('Bar')}
    assert Bar.__annotations__ == {'baz': ForwardRef('Baz')}
    strategies._update_forward_refs(
        Foo, 'tests.test_properties.test_strategies.test_basic'
    )
    assert Foo.__annotations__ == {'bar': Bar}
    assert Bar.__annotations__ == {'baz': Baz}


@pytest.mark.skip
def test_incorrect_module() -> None:
    assert Foo.__annotations__ == {'bar': ForwardRef('Bar')}

    with pytest.raises(NameError) as exc:
        strategies._update_forward_refs(Foo, 'tests.test_properties.test_strategies')

    assert exc.match('name \'Bar\' is not defined')


def test_module_following(testdir: Testdir) -> None:
    def types() -> None:
        from prisma._types import TypedDict
        from .bar import Bar

        class Foo(TypedDict):
            bar: Bar

    def bar() -> None:
        from prisma._types import TypedDict

        class Bar(TypedDict):
            baz: 'Baz'

        class Baz(TypedDict):
            point: int

    def tests() -> None:
        from pydantic.typing import ForwardRef
        from strategies_example.types import Foo
        from strategies_example.bar import Bar, Baz
        from tests.properties import strategies

        def test_foo() -> None:
            assert Foo.__annotations__ == {'bar': Bar}
            assert Bar.__annotations__ == {'baz': ForwardRef('Baz')}
            assert Baz.__annotations__ == {'point': int}

            strategies._update_forward_refs(Foo, Foo.__module__)

            assert Foo.__annotations__ == {'bar': Bar}
            assert Bar.__annotations__ == {'baz': Baz}
            assert Baz.__annotations__ == {'point': int}

    p = testdir.create_module(mod='strategies_example')
    testdir.make_from_function(bar, name=p / 'bar.py')
    testdir.make_from_function(types, name=p / 'types.py')
    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=1)
