# -*- coding: utf-8 -*-

import os
import sys
import logging

from prisma import generator


__all__ = ('main',)


def main():
    if os.environ.get('PRISMA_PY_DEBUG'):
        logging.basicConfig()
        logging.root.setLevel(logging.DEBUG)

    args = sys.argv
    if len(args) > 1 and args[1] == 'generate':
        generator.run(args[2:])
    else:
        print('Prisma CLI has not been implemented yet.')


if __name__ == '__main__':
    main()
