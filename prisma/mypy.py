from typing import Optional, Callable, Type as TypingType

from mypy.types import CallableType
from mypy.plugin import Plugin, MethodSigContext


class PrismaPlugin(Plugin):
    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodSigContext], CallableType]]:
        return None


def plugin(version: str) -> TypingType[Plugin]:
    return PrismaPlugin
