from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import LiteralString as LiteralString
else:
    # for pydantic support
    LiteralString = str
