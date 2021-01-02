from typing import Any


__all__ = (
    'PrismaError',
    'DataError',
    'UniqueViolationError',
)


class PrismaError(Exception):
    pass


class DataError(PrismaError):
    def __init__(self, data: Any):
        self.data = data

        user_facing_error = data.get('user_facing_error', {})
        self.code = user_facing_error.get('error_code')
        self.meta = user_facing_error.get('meta')

        message = user_facing_error.get('message')
        super().__init__(message or 'An error occurred while processing data.')


class UniqueViolationError(DataError):
    pass


class MissingRequiredValueError(DataError):
    pass
