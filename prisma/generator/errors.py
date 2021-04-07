from ..errors import PrismaError


class PluginError(PrismaError):
    pass


class PluginMissingHookError(PluginError):
    pass


class PluginMismatchedTypeError(PluginError):
    pass


class PluginInvalidHookError(PluginError):
    pass
