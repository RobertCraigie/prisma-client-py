# -*- coding: utf-8 -*-

import sys
from prisma import generator


__all__ = ('main',)


def main():
    args = sys.argv
    if len(args) > 1 and args[1] == 'generate':
        generator.run()
    else:
        print('Prisma CLI has not been implemented yet.')


if __name__ == '__main__':
    main()
