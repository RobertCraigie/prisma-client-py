from pathlib import Path

import nox


CACHE_DIR = Path.cwd() / '.cache'


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
    session.env['PYTEST_ADDOPTS'] = '"-W error"'
