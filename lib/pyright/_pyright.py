from __future__ import annotations

from typing_extensions import Literal, TypedDict


class PyrightDiagnostics(TypedDict, total=False):
    # NOTE: not exhaustive
    reportPrivateUsage: bool
    reportUnusedImport: bool
    reportPrivateUsage: bool
    reportImportCycles: bool
    reportImplicitOverride: bool
    reportUnusedCallResult: bool
    reportUnknownMemberType: bool
    reportUnknownVariableType: bool
    reportUnknownArgumentType: bool
    reportCallInDefaultInitializer: bool
    reportImplicitStringConcatenation: bool
    reportUnnecessaryTypeIgnoreComment: bool


class PyrightConfig(PyrightDiagnostics):
    include: list[str]
    exclude: list[str]
    extraPaths: list[str]
    typeCheckingMode: Literal['basic', 'strict']


Config = PyrightConfig
