# -*- coding: utf-8 -*-

__title__ = 'prisma'
__author__ = 'RobertCraigie'
__license__ = 'APACHE'
__copyright__ = 'Copyright 2020-2021 RobertCraigie'
__version__ = '0.6.0a'


from .utils import setup_logging
from . import errors as errors
from .validator import *


try:
    from .client import *
    from .fields import *
    from . import (
        models as models,
        partials as partials,
        types as types,
        utils as utils,
    )

    # Inheriting Client to rename it for signature purposes.
    class Prisma(Client):
        def __init__(
            self,
            *,
            use_dotenv: bool = True,
            log_queries: bool = False,
            auto_register: bool = False,
            datasource: types.Optional[types.DatasourceOverride] = None,
            connect_timeout: int = 10,
            http: types.Optional[types.HttpConfig] = None,
        ) -> None:
            super().__init__(
                use_dotenv=use_dotenv,
                log_queries=log_queries,
                auto_register=auto_register,
                datasource=datasource,
                connect_timeout=connect_timeout,
                http=http,
            )

        def __repr__(self) -> str:
            client_sig = utils.fn_signature(Client.__init__)
            return f"Prisma({client_sig})"

except ModuleNotFoundError:
    # code has not been generated yet
    # TODO: this could swallow unexpected errors
    pass


setup_logging()
