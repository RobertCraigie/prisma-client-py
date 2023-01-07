from pathlib import Path

import nox

from pipelines.utils import get_pkg_location, setup_env
from pipelines.utils.prisma import generate


@nox.session
def lint(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/lint.txt')
    session.install('.')

    generate(session)

    session.run('blue', '--check', '.')
    session.run(
        'pyright',
        get_pkg_location(session, 'prisma'),
        'tests',
    )
    session.run('pyright', '--ignoreexternal', '--verifytypes', 'prisma')
    session.run(
        'interrogate',
        '-v',
        '--omit-covered-files',
        '--fail-under',
        '100',
        '--whitelist-regex',
        'test_.*',
        '--exclude',
        '*/.venv/*',
        'tests',
    )
    session.run('slotscheck', '-m', 'prisma')


@nox.session
def mypy(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/mypy.txt')
    session.install('.')

    generate(session)

    session.run(
        'coverage',
        'run',
        '-m',
        'mypy',
        '--show-traceback',
        '--namespace-packages',
        '--package',
        'prisma',
        '--package',
        'tests',
    )


@nox.session
def format(session: nox.Session) -> None:
    """Format Python source code and all Prisma Schema files"""
    session.install('-r', 'pipelines/requirements/deps/blue.txt')
    session.install('-e', '.')

    session.run('blue', '.')

    for entry in Path.cwd().glob('**/*.schema.prisma'):
        session.run('prisma', 'format', f'--schema={entry}')
