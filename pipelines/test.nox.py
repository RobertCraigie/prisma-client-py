import nox

from pipelines.utils import setup_env
from pipelines.utils.prisma import generate


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11'])
def test(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/test.txt')
    session.install('-r', 'pipelines/requirements/node.txt')
    session.install('.')

    generate(session)

    session.run('coverage', 'run', '-m', 'pytest', *session.posargs)
