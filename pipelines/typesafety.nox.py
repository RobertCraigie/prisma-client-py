import nox

from pipelines.utils import setup_env
from pipelines.utils.prisma import generate


@nox.session(name='typesafety-mypy')
def mypy(session: nox.Session) -> None:
    """Runs our typing-only tests against mypy"""
    setup_env(session)
    session.install('-r', 'pipelines/requirements/typesafety-mypy.txt')
    session.install('.')

    generate(session, schema='typesafety/mypy/schema.prisma')

    session.run('pytest', '--mypy-ini-file=tests/data/mypy.ini', 'typesafety/mypy', *session.posargs)


@nox.session(name='typesafety-pyright')
def pyright(session: nox.Session) -> None:
    """Runs our typing-only tests against pyright"""
    setup_env(session)
    session.install('-r', 'pipelines/requirements/typesafety-pyright.txt')
    session.install('.')

    generate(session, schema='typesafety/pyright/schema.prisma')

    session.run('pytest', '--pyright-dir=typesafety/pyright', 'typesafety/pyright', *session.posargs)
