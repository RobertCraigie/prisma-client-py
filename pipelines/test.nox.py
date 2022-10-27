import nox

from pipelines.utils import setup_env
from pipelines.utils.prisma import generate


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11'])
def test(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/test.txt')
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
        *session.posargs,
    )
