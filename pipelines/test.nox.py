from nox_poetry import session
from nox import Session

from pipelines.utils import (
    setup_env,
    SUPPORTED_PYTHON_VERSIONS,
    install_group_dependencies,
)
from pipelines.utils.prisma import generate


@session(python=SUPPORTED_PYTHON_VERSIONS, reuse_venv=True)
def test(session: Session) -> None:
    setup_env(session)
    session.install('.')
    install_group_dependencies(session, 'dev')

    generate(session)

    session.install('coverage')
    # https://coverage.readthedocs.io/en/6.4.4/contexts.html
    session.run(
        'coverage',
        'run',
        '--context',
        f'{session.python}',
        '-m',
        'pytest',
        '--ignore=tests/integrations',
        *session.posargs,
    )


@session(python=SUPPORTED_PYTHON_VERSIONS, reuse_venv=True)
def test_integration_without_postgres(session: Session) -> None:
    setup_env(session)
    session.install('.')

    generate(session)

    # https://coverage.readthedocs.io/en/6.4.4/contexts.html
    session.run(
        'coverage',
        'run',
        '--context',
        f'{session.python}',
        '-m',
        'pytest',
        '--ignore=tests/integrations/postgresql',
        *session.posargs,
    )


@session(name='typesafety-mypy')
def test_mypy(session: Session) -> None:
    setup_env(session)
    session.install('.')
    install_group_dependencies(session, 'dev')

    generate(session, schema='typesafety/mypy/schema.prisma')

    session.run(
        'pytest',
        '--mypy-ini-file=tests/data/mypy.ini',
        'typesafety/mypy',
        *session.posargs,
    )


@session(name='typesafety-pyright')
def test_pyright(session: Session) -> None:
    setup_env(session)
    session.install('.')
    install_group_dependencies(session, 'dev')

    generate(session, schema='typesafety/pyright/schema.prisma')

    session.run(
        'pytest',
        '--pyright-dir=typesafety/pyright',
        'typesafety/pyright',
        *session.posargs,
    )
