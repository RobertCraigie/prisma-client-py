import nox

from pipelines.generator import generate_all


# TODO: split this up properly
# TODO: add reuse_venv ?


def _setup_env(session: nox.Session) -> None:
    session.install('-r', 'databases/requirements.txt')
    session.install('.')
    session.run('python', '-m', 'prisma_cleanup')


@nox.session
def databases(session: nox.Session) -> None:
    with session.chdir('databases'):
        generate_all()


@nox.session
def postgresql(session: nox.Session) -> None:
    _setup_env(session)

    session.env['DEBUG'] = '*'
    session.env['PRISMA_PY_DEBUG'] = '1'

    with session.chdir('databases/postgresql'):
        session.run(
            'prisma', 'db', 'push', '--accept-data-loss', '--force-reset'
        )
        session.run(
            'coverage',
            'run',
            '-m',
            'pytest',
            '--confcutdir=.',
            *session.posargs,
        )

        # TODO: ensure this is running in strict mode
        session.run('pyright', '.')


@nox.session
def sqlite(session: nox.Session) -> None:
    _setup_env(session)

    with session.chdir('databases/sqlite'):
        session.run(
            'prisma', 'db', 'push', '--accept-data-loss', '--force-reset'
        )
        session.run(
            'coverage',
            'run',
            '-m',
            'pytest',
            '--confcutdir=.',
            *session.posargs,
        )
        session.run('pyright', '.')
