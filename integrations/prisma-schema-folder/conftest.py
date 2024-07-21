import sys

sys.path.insert(0, '../../')

import prisma
from lib.testing.shared_conftest import *
from lib.testing.shared_conftest.async_client import *

prisma.register(Prisma())
