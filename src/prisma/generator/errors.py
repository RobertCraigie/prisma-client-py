from typing import Union

from ..errors import PrismaError


class TemplateError(PrismaError):
    pass


class CompoundConstraintError(ValueError):
    def __init__(self, constraint: Union['PrimaryKey', 'UniqueIndex']) -> None:
        if isinstance(constraint, PrimaryKey):
            annotation = '@@id'
        else:
            annotation = '@@unique'

        super().__init__(
            f'Compound constraint with name: {constraint.name} is already used as a name for a field; '
            'Please choose a different name. For example: \n'
            f'  {annotation}([{", ".join(constraint.fields)}], name: "my_custom_primary_key")'
        )


from .models import PrimaryKey, UniqueIndex
