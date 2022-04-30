from typing import Any, Optional


__all__ = (
    'PrismaError',
    'DataError',
    'UniqueViolationError',
    'ForeignKeyViolationError',
    'MissingRequiredValueError',
    'RawQueryError',
    'TableNotFoundError',
    'RecordNotFoundError',
    'HTTPClientClosedError',
    'ClientNotConnectedError',
    'PrismaWarning',
    'UnsupportedSubclassWarning',
)


class PrismaError(Exception):
    pass


class ClientNotRegisteredError(PrismaError):
    def __init__(self) -> None:
        super().__init__(
            'No client instance registered; You must call prisma.register(prisma.Prisma())'
        )


class ClientAlreadyRegisteredError(PrismaError):
    def __init__(self) -> None:
        super().__init__('A client has already been registered.')


class ClientNotConnectedError(PrismaError):
    def __init__(self) -> None:
        super().__init__(
            'Client is not connected to the query engine, '
            'you must call `connect()` before attempting to query data.'
        )


class HTTPClientClosedError(PrismaError):
    def __init__(self) -> None:
        super().__init__('Cannot make a request from a closed client.')


class UnsupportedDatabaseError(PrismaError):
    context: str
    database: str

    def __init__(self, database: str, context: str) -> None:
        super().__init__(f'{context} is not supported by {database}')
        self.database = database
        self.context = context


class DataError(PrismaError):
    data: Any
    code: Any
    meta: Any

    def __init__(self, data: Any, *, message: Optional[str] = None):
        self.data = data

        user_facing_error = data.get('user_facing_error', {})
        self.code = user_facing_error.get('error_code')
        self.meta = user_facing_error.get('meta')

        message = message or user_facing_error.get('message')
        super().__init__(message or 'An error occurred while processing data.')


class UniqueViolationError(DataError):
    pass


class ForeignKeyViolationError(DataError):
    pass


class MissingRequiredValueError(DataError):
    pass


class RawQueryError(DataError):
    def __init__(self, data: Any):
        try:
            super().__init__(
                data, message=data['user_facing_error']['meta']['message']
            )
        except KeyError:
            super().__init__(data)


class TableNotFoundError(DataError):
    def __init__(self, data: Any):
        super().__init__(data)
        self.table = self.meta.get('table')  # type: Optional[str]


class FieldNotFoundError(DataError):
    # currently we cannot easilt resolve the erroneous field as Prisma
    # returns different results for unknown fields in different situations
    # e.g. root query, nested query and mutation queries
    ...


class RecordNotFoundError(DataError):
    pass


class InputError(DataError):
    pass


class BuilderError(PrismaError):
    pass


class UnknownModelError(BuilderError):
    def __init__(self, model: str) -> None:
        super().__init__(f'Model: "{model}" does not exist.')


class UnknownRelationalFieldError(BuilderError):
    def __init__(self, model: str, field: str) -> None:
        super().__init__(
            f'Field: "{field}" either does not exist or is not a relational field on the {model} model'
        )


class GeneratorError(PrismaError):
    pass


class UnsupportedListTypeError(GeneratorError):
    type: str

    def __init__(self, typ: str) -> None:
        super().__init__(
            f'Cannot use {typ} as a list yet; Please create a '
            'feature request at https://github.com/RobertCraigie/prisma-client-py/issues/new'
        )
        self.type = typ


class PrismaWarning(Warning):
    pass


class UnsupportedSubclassWarning(PrismaWarning):
    pass
