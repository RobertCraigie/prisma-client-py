from nox_poetry import session
from nox import Session

from pipelines.utils import (
    get_pkg_location,
    setup_env,
    install_group_dependencies,
)
from pipelines.utils.prisma import generate


@session
def lint(session: Session) -> None:
    setup_env(session)
    session.install('.')
    session.install('pyright', 'blue', 'interrogate')

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


@session
def mypy(session: Session) -> None:
    setup_env(session)
    session.install('.')
    session.install('coverage', 'mypy')

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
