from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest


def request_has_client(request: 'FixtureRequest') -> bool:
    """Return whether or not the current request uses the prisma client"""
    return request.node.get_closest_marker('prisma') is not None or 'client' in request.fixturenames
