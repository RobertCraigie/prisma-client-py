import sys
import subprocess
from pathlib import Path


def main(*args: str) -> None:
    rootdir = Path(__file__).parent
    subprocess.check_call(['maturin', 'develop', *args], cwd=str(rootdir.absolute()))


if __name__ == '__main__':
    main(*sys.argv[1:])
