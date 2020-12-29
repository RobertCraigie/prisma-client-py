import aiohttp
from ..errors import PrismaError


__all__ = (
    'EngineError',
    'BinaryNotFoundError',
    'MismatchedVersionsError',
    'EngineConnectionError',
    'EngineRequestError',
    'AlreadyConnectedError',
    'NotConnectedError',
)


class EngineError(PrismaError):
    pass


class BinaryNotFoundError(EngineError):
    pass


class AlreadyConnectedError(EngineError):
    pass


class NotConnectedError(EngineError):
    pass


class MismatchedVersionsError(EngineError):
    def __init__(self, *, expected: str, got: str):
        super().__init__(f'Expected query engine version `{expected}` but got `{got}`')
        self.expected = expected
        self.got = got


class EngineConnectionError(EngineError):
    pass


class EngineRequestError(EngineError):
    def __init__(self, response: aiohttp.ClientResponse, body: str):
        self.response = response

        # TODO: better error message
        super().__init__(f'{response.status}: {body}')
