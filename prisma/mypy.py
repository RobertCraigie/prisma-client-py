import re
import copy
import logging
import builtins
import operator
from configparser import ConfigParser
from typing import Optional, Callable, Dict, Any, Type as TypingType, cast

# pylint: disable=no-name-in-module
from mypy.options import Options
from mypy.errorcodes import ErrorCode
from mypy.types import (
    UnionType,
    NoneType,
    Type,
    Instance,
)
from mypy.nodes import (
    Expression,
    DictExpr,
    StrExpr,
    NameExpr,
    Var,
    BytesExpr,
    UnicodeExpr,
    CallExpr,
    IntExpr,
    Context,
    TypeInfo,
    SymbolTable,
)
from mypy.plugin import Plugin, MethodContext, CheckerPluginInterface

# pylint: enable=no-name-in-module


# match any direct children of an actions class
CLIENT_ACTION_CHILD = re.compile(
    r'prisma\.client\.(.*)Actions\.(?P<name>(((?!\.).)*$))'
)
ACTIONS = [
    # implemented
    'create',
    'find_unique',
    # not implemented
    'find_first',
    'find_many',
    'update',
    'upsert',
    'delete',
    'update_many',
    'delete_many',
    'count',
]

PRISMA_TYPE = re.compile(r'prisma\.types\.(?P<name>(((?!\.).)*$))')
CONFIGFILE_KEY = 'prisma-mypy'

log = logging.getLogger(__name__)


def plugin(version: str) -> TypingType[Plugin]:
    return PrismaPlugin


class PrismaPluginConfig:
    __slots__ = ('warn_parsing_errors',)
    warn_parsing_errors: bool

    def __init__(self, options: Options) -> None:
        if options.config_file is None:  # pragma: no cover
            return

        plugin_config = ConfigParser()
        plugin_config.read(options.config_file)
        for key in self.__slots__:
            setting = plugin_config.getboolean(CONFIGFILE_KEY, key, fallback=True)
            setattr(self, key, setting)


# pylint: disable=no-self-use


class PrismaPlugin(Plugin):
    def __init__(self, options: Options) -> None:
        self.config = PrismaPluginConfig(options)
        super().__init__(options)

    def get_method_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodContext], Type]]:
        match = CLIENT_ACTION_CHILD.match(fullname)
        if not match:
            return None

        if match.group('name') in ACTIONS:
            return self.handle_action_invocation

        return None

    def handle_action_invocation(self, ctx: MethodContext) -> Type:
        # TODO: if an error occurs, log it so that we don't cause mypy to
        #       exit prematurely.
        return self._handle_include(ctx)

    def _handle_include(self, ctx: MethodContext) -> Type:
        include_expr = self.get_arg_named('include', ctx)
        if include_expr is None:
            return ctx.default_return_type

        if not isinstance(ctx.default_return_type, Instance):
            # TODO: resolve this
            return ctx.default_return_type

        is_coroutine = self.is_coroutine_type(ctx.default_return_type)
        if is_coroutine:
            actual_ret = ctx.default_return_type.args[2]
        else:
            actual_ret = ctx.default_return_type

        is_optional = self.is_optional_type(actual_ret)
        if is_optional:
            actual_ret = cast(UnionType, actual_ret)
            model_type = actual_ret.items[0]
        else:
            model_type = actual_ret

        if not isinstance(model_type, Instance):
            return ctx.default_return_type

        try:
            include = self.parse_expression_to_dict(include_expr, recursive=False)
        except Exception as exc:  # pylint: disable=broad-except
            log.debug(
                'Ignoring %s exception while parsing include: %s',
                type(exc).__name__,
                exc,
            )

            # TODO: test this, pytest-mypy-plugins does not bode well with multiple line output
            if self.config.warn_parsing_errors:
                # TODO: add more details
                # e.g. "include" to "find_unique" of "UserActions"
                error_unable_to_parse(ctx.api, include_expr, 'the "include" argument')

            return ctx.default_return_type

        names = SymbolTable()
        for key, node in model_type.type.names.items():
            value = include.get(key)
            if value is False or value is None:
                names[key] = node
                continue

            # we do not want to remove the Optional from a field that is not a list
            # as the Optional indicates that the field is optional on a database level
            if (
                not isinstance(node.node, Var)
                or node.node.type is None
                or not isinstance(node.node.type, UnionType)
                or not self.is_optional_union_type(node.node.type)
                or not self.is_list_type(node.node.type.items[0])
            ):
                log.debug(
                    'Not modifying included field: %s',
                    key,
                )
                names[key] = node
                continue

            # this whole mess with copying is so that the modified field is not leaked
            new = node.copy()
            new.node = copy.copy(new.node)
            assert isinstance(new.node, Var)
            new.node.type = node.node.type.items[0]
            names[key] = new

        new_model = self.copy_modified_instance(model_type, names)

        if is_optional:
            actual_ret = cast(UnionType, actual_ret)
            modified_ret = self.copy_modified_optional_type(actual_ret, new_model)
        else:
            modified_ret = new_model  # type: ignore

        if is_coroutine:
            arg1, arg2, _ = ctx.default_return_type.args
            return ctx.default_return_type.copy_modified(
                args=[arg1, arg2, modified_ret]
            )

        return modified_ret

    def get_arg_named(self, name: str, ctx: MethodContext) -> Optional[Expression]:
        """Return the expression for an argument."""
        # keyword arguments
        for i, names in enumerate(ctx.arg_names):
            for j, arg_name in enumerate(names):
                if arg_name == name:
                    return ctx.args[i][j]

        # positional arguments
        for i, arg_name in enumerate(ctx.callee_arg_names):
            if arg_name == name and ctx.args[i]:
                return ctx.args[i][0]

        return None

    def is_optional_type(self, typ: Type) -> bool:
        return isinstance(typ, UnionType) and self.is_optional_union_type(typ)

    def is_optional_union_type(self, typ: UnionType) -> bool:
        return len(typ.items) == 2 and isinstance(typ.items[1], NoneType)

    # TODO: why is fullname Any?

    def is_coroutine_type(self, typ: Instance) -> bool:
        return bool(typ.type.fullname == 'typing.Coroutine')

    def is_list_type(self, typ: Type) -> bool:
        return isinstance(typ, Instance) and typ.type.fullname == 'builtins.list'

    def copy_modified_instance(
        self, instance: Instance, names: SymbolTable
    ) -> Instance:
        new = copy.copy(instance)
        new.type = TypeInfo(names, new.type.defn, new.type.module_name)
        new.type.mro = [new.type, *new.type.mro]
        return new

    def copy_modified_optional_type(self, original: UnionType, typ: Type) -> UnionType:
        new = copy.copy(original)
        new.items = new.items.copy()
        new.items[0] = typ
        return new

    def parse_expression_to_dict(
        self, expression: Expression, recursive: bool = True
    ) -> Dict[Any, Any]:
        if isinstance(expression, DictExpr):
            return self._dictexpr_to_dict(expression, recursive=recursive)

        if isinstance(expression, CallExpr):
            return self._callexpr_to_dict(expression, recursive=recursive)

        raise TypeError(
            f'Cannot parse expression of type={type(expression).__name__} to a dictionary.'
        )

    def _dictexpr_to_dict(self, expr: DictExpr, recursive: bool) -> Dict[Any, Any]:
        parsed = {}
        for key_expr, value_expr in expr.items:
            if key_expr is None:
                # TODO: what causes this?
                raise TypeError('Cannot resolve key as the key expression is missing')

            key = self._resolve_expression(key_expr, recursive)
            value = self._resolve_expression(value_expr, recursive)
            parsed[key] = value

        return parsed

    def _callexpr_to_dict(
        self, expr: CallExpr, recursive: bool, strict: bool = True
    ) -> Dict[str, Any]:
        if not isinstance(expr.callee, NameExpr):
            raise TypeError(
                f'Expected CallExpr.callee to be a NameExpr but got {type(expr.callee)} instead.'
            )

        if strict and expr.callee.fullname != 'builtins.dict':
            raise TypeError(
                f'Expected builtins.dict to be called but got {expr.callee.fullname} instead'
            )

        parsed = {}
        for arg_name, value_expr in zip(expr.arg_names, expr.args):
            if arg_name is None:
                continue

            value = self._resolve_expression(value_expr, recursive)
            parsed[arg_name] = value

        return parsed

    def _resolve_expression(self, expression: Expression, recursive: bool) -> Any:
        if isinstance(expression, (StrExpr, BytesExpr, UnicodeExpr, IntExpr)):
            return expression.value

        if isinstance(expression, NameExpr):
            return self._resolve_name_expression(expression)

        if isinstance(expression, DictExpr):
            if not recursive:
                return expression
            return self._dictexpr_to_dict(expression, recursive)

        raise TypeError(
            f'Cannot resolve value for an expression of type={type(expression).__name__}'
        )

    def _resolve_name_expression(self, expression: NameExpr) -> Any:
        if isinstance(expression.node, Var):
            return self._resolve_var_node(expression.node)

        raise TypeError('Cannot resolve value for a NameExpr expression')

    def _resolve_var_node(self, node: Var) -> Any:
        if node.is_final:
            return node.final_value

        if node.fullname.startswith('builtins.'):
            return self._resolve_builtin(node.fullname)

        raise TypeError(f'Cannot resolve value for a Var node {node.fullname}')

    def _resolve_builtin(self, fullname: str) -> Any:
        return operator.attrgetter(*fullname.split('.')[1:])(builtins)


ERROR_PARSING = ErrorCode('prisma-parsing', 'Unable to parse', 'Prisma')


def error_unable_to_parse(
    api: CheckerPluginInterface, context: Context, detail: str
) -> None:
    link = 'https://github.com/RobertCraigie/prisma-client-py/issues/new/choose'
    full_message = f'The prisma mypy plugin was unable to parse: {detail}\n'
    full_message += (
        f'Please consider reporting this bug at {link} so we can try to fix it!'
    )
    api.fail(full_message, context, code=ERROR_PARSING)
