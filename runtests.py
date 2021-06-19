#!/usr/bin/env python3
import sys
import subprocess


def main():
    process = subprocess.Popen(['tox'] + sys.argv[1:])
    process.wait()
    sys.exit(process.returncode)


if __name__ == '__main__':
    main()
