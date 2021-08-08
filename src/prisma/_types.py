import sys
from typing import Callable, Coroutine, TypeVar, Union, List, Dict, Any

from pydantic import BaseModel


if sys.version_info >= (3, 8):
    # pyright: reportUnusedImport=false
    from typing import (  # pylint: disable=no-name-in-module, unused-import
        TypedDict,
        Literal,
    )
else:
    from typing_extensions import TypedDict, Literal


Method = Literal['GET', 'POST']

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)

# TODO: use a TypeVar
FuncType = Callable[..., Any]
CoroType = Callable[..., Coroutine[Any, Any, Any]]

# NOTE: this should be a recursive type
Serializable = Union[None, bool, float, int, str, List[Any], Dict[Any, Any]]
