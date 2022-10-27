from pathlib import Path
from typing import Literal

import subprocess

import nox


PROJECT_ROOT = Path(__file__).parent.parent.parent

assert (
    PROJECT_ROOT / 'pyproject.toml'
).exists(), f'Project root is not correct: {PROJECT_ROOT}'


CACHE_DIR = PROJECT_ROOT / '.cache'


def get_pkg_location(session: nox.Session, pkg: str) -> str:
    location = session.run(
        'python',
        '-c',
        f'import {pkg}; print({pkg}.__file__)',
        silent=True,
    )
    assert isinstance(location, str)
    return str(Path(location).parent)


def setup_env(session: nox.Session) -> None:
    coverage_file = f'.coverage.{session.name}{session.python if isinstance(session.python, str) else ""}'
    session.env['COVERAGE_FILE'] = str(CACHE_DIR / coverage_file)
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


GROUP = Literal['dev']


def install_group_dependencies(session: nox.Session, group: GROUP) -> None:
    """
    This is a utility function that works around the fact that the

    """
    deps_text: str = subprocess.getoutput(
        f'poetry export --only {group} --without-urls --without-hashes'
    )
    # Get only the package name
    dependencies_for_group = [
        line.split(';')[0].strip() for line in deps_text.splitlines()
    ]

    session.install(*dependencies_for_group)
