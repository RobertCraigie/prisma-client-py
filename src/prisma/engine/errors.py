from ..http import Response
from ..errors import PrismaError


__all__ = (
    'EngineError',
    'BinaryNotFoundError',
    'MismatchedVersionsError',
    'EngineConnectionError',
    'EngineRequestError',
    'AlreadyConnectedError',
    'NotConnectedError',
    'UnprocessableEntityError',
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
    got: str
    expected: str

    def __init__(self, *, expected: str, got: str):
        super().__init__(f'Expected query engine version `{expected}` but got `{got}`')
        self.expected = expected
        self.got = got


class EngineConnectionError(EngineError):
    pass


class EngineRequestError(EngineError):
    response: Response

    def __init__(self, response: Response, body: str):
        self.response = response

        # TODO: better error message
        super().__init__(f'{response.status}: {body}')


class UnprocessableEntityError(EngineRequestError):
    def __init__(self, response: Response):
        super().__init__(
            response,
            (
                'Error occurred, '
                'it is likely that the internal GraphQL query '
                'builder generated a malformed request.\n'
                'Please create an issue at https://github.com/RobertCraigie/prisma-client-py/issues'
            ),
        )
