import nox

from pipelines.utils import setup_env, maybe_install_nodejs_bin
from pipelines.utils.prisma import generate


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11'])
def test(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/test.txt')
    session.install('.')
    maybe_install_nodejs_bin(session)

    if '--pydantic-v2=true' in session.posargs:
        session.install('pydantic==2.0b2')

    generate(session)

    session.run(
        'coverage',
        'run',
        '-m',
        'pytest',
        '--ignore=databases',
        *session.posargs,
        env={
            'PYTEST_PLUGINS': 'pytester',
        },
    )
