import os
import sys
import subprocess


PYTHON_MAPPING = {
    '3.7': '3.7',
    '3.8': '3.8',
    '3.9': '3.9',
    '3.10': '3.10',
    '3.11': '3.11',
    '3.11.0-rc.1': '3.11',
}


def main() -> None:
    python_version = PYTHON_MAPPING[os.environ['TARGET_PYTHON']]
    subprocess.check_call(['nox', '-p', python_version, *sys.argv[1:]])


if __name__ == '__main__':
    main()
