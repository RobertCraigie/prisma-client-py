from ..errors import PrismaError


__all__ = (
    'EngineError',
    'BinaryNotFoundError',
    'MismatchedVersionsError',
    'EngineConnectionError',
    'EngineRequestError',
    'AlreadyConnectedError',
)


class EngineError(PrismaError):
    pass


class BinaryNotFoundError(EngineError):
    pass


class AlreadyConnectedError(EngineError):
    pass


class MismatchedVersionsError(EngineError):
    def __init__(self, message=None, *, expected=None, got=None):
        super().__init__(
            message or f'Expected query engine version `{expected}` but got `{got}`'
        )
        self.expected = expected
        self.got = got


class EngineConnectionError(EngineError):
    pass


class EngineRequestError(EngineError):
    def __init__(self, response, body):
        self.response = response

        # TODO: better error message
        super().__init__(f'{response.status}: {body}')
