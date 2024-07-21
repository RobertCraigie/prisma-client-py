import nox

from pipelines.utils import setup_env, maybe_install_nodejs_bin
from pipelines.utils.prisma import generate


@nox.session(name='i:prisma-schema-folder')
def prisma_schema_folder(session: nox.Session) -> None:
    setup_env(session)
    maybe_install_nodejs_bin(session)

    session.install('-r', 'pipelines/requirements/integration-prisma-schema-folder.txt')

    if '-e' in session.posargs:
        session.install('-e', '.')
    else:
        session.install('.')

    with session.chdir('integrations/prisma-schema-folder'):
        generate(session, schema=None)

        session.run('python', '-m', 'prisma', 'db', 'push', '--skip-generate', '--accept-data-loss', '--force-reset')

        session.run('pytest')
