import nox
from nox import Session


BASE_REQUIREMENTS = ['pytest==6.2.5', 'pytest-benchmark==3.4.1']


@nox.session()
def prisma(session: Session) -> None:
    with session.chdir('prisma'):
        session.install(*BASE_REQUIREMENTS, '../..')

        # https://github.com/prisma/prisma/issues/10265
        session.run('prisma', 'db', 'push', '--skip-generate')
        session.run('prisma', 'generate')

        # confcutdir and -c are required to stop pytest from traversing previous
        # directories for configuration files
        session.run(
            'pytest',
            '--confcutdir=.',
            '-c',
            'pytest.ini',
            '--benchmark-max-time=10',
            *session.posargs
        )

        # TODO: check pyright
