import sys
import logging
import inspect
from typing import Type, Dict, Tuple, List, Optional, NamedTuple, Any


from prisma import types
from prisma._types import FuncType
from pydantic.typing import ForwardRef, get_args, _eval_type
from hypothesis import strategies as st


TYPES_NS = vars(types)

log = logging.getLogger('prisma.tests')


def _is_forwardref(typ: Type[Any]) -> bool:
    return typ == ForwardRef or isinstance(typ, ForwardRef)


def _get_module(typ: Type[Any], fallback: str) -> str:
    mod = getattr(typ, '__module__', fallback)
    if mod in {'builtins', 'typing', 'typing_extensions'}:
        # TODO: naive handling, we return the fallback as we want
        # to evaluate the type in the current module context
        return fallback
    return mod


def _evaluate_forward_ref(
    typ: Type[Any], base_globals: Optional[Dict[str, Any]], module_name: str
) -> Type[Any]:
    resolved = _eval_type(typ, base_globals, None)
    return _update_forward_refs(resolved, _get_module(resolved, module_name))[0]


def _update_forward_refs(typ: Type[Any], module_name: str) -> Tuple[Type[Any], bool]:
    # print(getattr(typ, '__module__', None))

    module_name = _get_module(typ, module_name)
    # print(f'Evaluating from module: {module_name}')

    # TODO: this doesn't follow forward references to other modules properly
    base_globals: Optional[Dict[str, Any]] = None
    if module_name:
        try:
            module = sys.modules[module_name]
        except KeyError:
            # happens occasionally, see https://github.com/samuelcolvin/pydantic/issues/2363
            pass
        else:
            base_globals = module.__dict__

    if _is_forwardref(typ):
        return _evaluate_forward_ref(typ, base_globals, module_name), True

    do_update = False
    new_args = []
    args = get_args(typ)
    for arg in args:
        if _is_forwardref(arg):
            do_update = True
            new_args.append(_evaluate_forward_ref(arg, base_globals, module_name))
        else:
            value, updated = _update_forward_refs(arg, _get_module(arg, module_name))
            if updated:
                do_update = True
            new_args.append(value)

    if do_update:
        typ.__args__ = tuple(new_args)

    if hasattr(typ, '__annotations__'):
        _update_forward_refs_from_annotations(typ.__annotations__, module_name)

    return typ, do_update


def _update_forward_refs_from_annotations(
    annotations: Dict[str, Type[Any]], module_name: str
) -> None:
    new = {}
    for field, annotation in annotations.items():
        new[field] = _update_forward_refs(annotation, module_name)[0]
    annotations.update(new)


def from_prisma_type(typ: Type[Any]) -> st.SearchStrategy[Any]:
    """
    if hasattr(typ, '__annotations__'):
        _update_forward_refs_from_annotations(typ.__annotations__, 'prisma.types')
    else:
        raise RuntimeError(typ)
    """
    _update_forward_refs(typ, 'prisma.types')

    # raise RuntimeError(typ.__annotations__)
    return st.from_type(typ)


def from_typeddict(typ, **types) -> st.SearchStrategy[Any]:
    optional = getattr(typ, "__optional_keys__", ())
    anns = {
        k: types.get(k) or from_prisma_type(v) for k, v in typ.__annotations__.items()
    }
    return st.fixed_dictionaries(
        mapping={k: v for k, v in anns.items() if k not in optional},
        optional={k: v for k, v in anns.items() if k in optional},
    )


from prisma.builder import DEFAULT_FIELDS_MAPPING


# TODO: type defs
def register_type_for_models(attr: str, strategy, *models: str) -> None:
    if not models:
        models = DEFAULT_FIELDS_MAPPING.keys()

    for model in models:
        st.register_type_strategy(getattr(types, attr.format(model=model)), strategy)


class FromMethod(NamedTuple):
    args: List[Any]
    kwargs: Dict[str, Any]
    returntype: Type[Any]


class CustomStrategy(st.SearchStrategy):
    def __init__(
        self,
        strategy: st.SearchStrategy[Any],
        varargs: Optional[str],
        returntype: Type[Any],
    ) -> None:
        self._strategy = strategy
        self._varargs = varargs
        self._returntype = returntype

    def do_draw(self, data) -> None:
        # raise RuntimeError(self._strategy)
        data = self._strategy.do_draw(data)
        import logging

        logging.getLogger('prisma.tests.debug').debug(data)
        # raise RuntimeError(d)

        if self._varargs:
            args = data.pop(self._varargs, [])
        else:
            args = []

        return FromMethod(args=args, kwargs=data, returntype=self._returntype)


def from_method(meth: FuncType) -> st.SearchStrategy[Any]:
    # TODO: should mix and match args and kwargs
    # i.e. every non-kwonly argument should be used in either
    # the args or the kwargs
    spec = inspect.getfullargspec(meth)

    # hints = get_type_hints(meth)
    hints = spec.annotations
    args = {}
    for arg, typ in hints.items():
        if arg in {'return'}:
            continue

        if arg == spec.varargs:
            args[arg] = st.lists(from_prisma_type(typ))
        else:
            args[arg] = from_prisma_type(typ)

    # TODO: handle unions properly
    return CustomStrategy(
        st.fixed_dictionaries(args), varargs=spec.varargs, returntype=hints['return']
    )
