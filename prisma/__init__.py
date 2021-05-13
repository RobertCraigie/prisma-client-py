# -*- coding: utf-8 -*-

__title__ = 'prisma'
__author__ = 'RobertCraigie'
__license__ = 'APACHE'
__copyright__ = 'Copyright 2020 RobertCraigie'
__version__ = '0.0.1'

from .plugins import *
from . import binaries, jsonrpc, engine, utils


try:
    from .client import *
except ModuleNotFoundError:
    # code has not been generated yet
    # TODO: this could swallow unexpected errors
    pass


utils.setup_logging()
