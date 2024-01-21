import tempfile
from pathlib import Path

import nox
import distro

CACHE_DIR = Path.cwd() / '.cache'
TMP_DIR = Path(tempfile.gettempdir())
PIPELINES_DIR = Path(__file__).parent.parent


def get_pkg_location(session: nox.Session, pkg: str) -> str:
    location = session.run(
        'python',
        '-c',
        f'import {pkg}; print({pkg}.__file__)',
        silent=True,
    )
    assert isinstance(location, str)
    return str(Path(location).parent)


def setup_coverage(session: nox.Session, identifier: str) -> None:
    if identifier:
        identifier = f'.{identifier}'

    coverage_file = f'.coverage.{session.name}{identifier}'
    session.env['COVERAGE_FILE'] = str(CACHE_DIR / coverage_file)


def setup_env(session: nox.Session) -> None:
    setup_coverage(
        session,
        identifier=session.python if isinstance(session.python, str) else '',
    )
    session.env['PRISMA_PY_DEBUG'] = '1'
    session.env['PYTEST_ADDOPTS'] = ' '.join(
        [
            f'"{opt}"'
            for opt in [
                '-W error',
                # httpx deprecation warnings
                "-W ignore:'cgi' is deprecated and slated for removal in Python 3.13:DeprecationWarning",
                '-W ignore:path is deprecated:DeprecationWarning',
            ]
        ]
    )


def maybe_install_nodejs_bin(session: nox.Session) -> bool:
    # nodejs-bin is not available on alpine yet, we need to wait until this fix is released:
    # https://github.com/samwillis/nodejs-pypi/issues/11
    if distro.id() == 'alpine':
        return False

    session.install('-r', str(PIPELINES_DIR / 'requirements/node.txt'))
    return True
