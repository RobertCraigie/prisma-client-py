import nox
import distro

from pipelines.utils import setup_env
from pipelines.utils.prisma import generate


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11'])
def test(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/test.txt')
    session.install('.')

    # nodejs-bin is not available on alpine yet, we need to wait until this fix is released:
    # https://github.com/samwillis/nodejs-pypi/issues/11
    if distro.id() != 'alpine':
        session.install('-r', 'pipelines/requirements/node.txt')

    generate(session)

    session.run(
        'coverage',
        'run',
        '-m',
        'pytest',
        '--ignore=databases',
        *session.posargs
    )
