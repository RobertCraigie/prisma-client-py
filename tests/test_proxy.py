from typing_extensions import final, override

from pytest_mock import MockerFixture

from prisma._proxy import LazyProxy


class MyObject:
    @override
    def __repr__(self) -> str:
        return '<MyObject foo!>'

    @override
    def __str__(self) -> str:
        return 'foo!'

    @property
    def foo(self) -> str:
        return 'FOO'


@final
class MyProxy(LazyProxy[MyObject]):
    @override
    def __load__(self) -> MyObject:
        return MyObject()


def test_proxied_data_methods() -> None:
    """Supported data methods work as expected"""
    obj = MyProxy().__as_proxied__()
    assert str(obj) == 'foo!'
    assert repr(obj) == '<MyObject foo!>'

    props = [p for p in dir(obj) if not p.startswith('_')]
    assert props == ['foo']


def test_proxied_properties() -> None:
    """Ensure properties can be accessed"""
    obj = MyProxy().__as_proxied__()
    assert obj.foo == 'FOO'


def test_load_once(mocker: MockerFixture) -> None:
    """The `__load__` function is only called once for multiple proxy attribute accesses"""
    obj = MyProxy().__as_proxied__()
    spy = mocker.spy(MyProxy, '__load__')

    assert obj.foo == 'FOO'
    assert obj.foo == 'FOO'

    assert spy.call_count == 1
