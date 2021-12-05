from typing import TYPE_CHECKING
from ..utils import module_exists

# we don't type the LibraryEngine when type checking for convenience
# type checkers don't like the conditional import we do below
if TYPE_CHECKING:
    from .library import LibraryEngine
else:
    if module_exists('_prisma_query_engine'):
        from .library import LibraryEngine
    else:
        LibraryEngine = None  # pylint: disable=invalid-name


__all__ = ('LibraryEngine',)
