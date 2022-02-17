from typing import Any
from typing_extensions import Protocol


class Admin(Protocol):
    # TODO: fields
    @classmethod
    def prisma(cls) -> Any:
        ...
