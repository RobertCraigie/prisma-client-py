from ...utils import module_exists


if module_exists('prisma.client'):
    from .plugin import *
