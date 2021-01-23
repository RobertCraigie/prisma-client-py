from typing import Callable, Coroutine, Any
from typing_extensions import Literal


Method = Literal['GET', 'POST']

# TODO: use a TypeVar
FuncType = Callable[..., Any]
CoroType = Callable[..., Coroutine[Any, Any, Any]]
