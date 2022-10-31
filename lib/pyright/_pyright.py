from typing_extensions import TypedDict, Literal


class PyrightDiagnostics(TypedDict, total=False):
    # NOTE: not exhaustive
    reportPrivateUsage: bool
    reportUnnecessaryTypeIgnoreComment: bool


class PyrightConfig(PyrightDiagnostics):
    include: list[str]
    exclude: list[str]
    extraPaths: list[str]
    typeCheckingMode: Literal['basic', 'strict']


Config = PyrightConfig
