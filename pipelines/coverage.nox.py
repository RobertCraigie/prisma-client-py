import nox

from pipelines.utils import setup_env


@nox.session
def setup(session: nox.Session) -> None:
    setup_env(session)
    session.install('coverage==5.3.1')
    session.run('coverage', 'erase')


@nox.session
def report(session: nox.Session) -> None:
    setup_env(session)
    session.install('coverage==5.3.1')
    session.run('coverage', 'combine')
    session.run('coverage', 'html', '-i')
    session.run('coverage', 'xml', '-i')
    session.run('coverage', 'report', '-i', '--skip-covered')
