from ..http import Response
from ..errors import PrismaError


__all__ = (
    'EngineError',
    'EngineConnectionError',
    'EngineRequestError',
    'AlreadyConnectedError',
    'NotConnectedError',
    'UnprocessableEntityError',
)


class EngineError(PrismaError):
    pass


class AlreadyConnectedError(EngineError):
    pass


class NotConnectedError(EngineError):
    pass


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
