import nox

from pipelines.utils import setup_env, CACHE_DIR


@nox.session
def setup(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/coverage.txt')
    session.run('coverage', 'erase')


@nox.session
def report(session: nox.Session) -> None:
    session.env['COVERAGE_FILE'] = str(CACHE_DIR / '.coverage')
    session.install('-r', 'pipelines/requirements/coverage.txt')
    session.run('coverage', 'combine')
    session.run('coverage', 'html', '-i')
    session.run('coverage', 'xml', '-i')
    session.run('coverage', 'report', '-i', '--skip-covered')
