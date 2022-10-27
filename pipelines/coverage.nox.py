from nox_poetry import session
from nox import Session

from pipelines.utils import setup_env


@session(reuse_venv=True)
def setup(session: Session) -> None:
    setup_env(session)
    session.install('coverage')


@session(reuse_venv=True)
def report(session: Session) -> None:
    setup_env(session)
    session.install('coverage')
    session.run('coverage', 'combine')
    session.run('coverage', 'html', '-i')
    session.run('coverage', 'xml', '-i')
    session.run('coverage', 'report', '-i', '--skip-covered')
