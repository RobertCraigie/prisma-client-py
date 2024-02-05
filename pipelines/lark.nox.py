import nox

from pipelines.utils import generate_parsers


@nox.session
def lark(session: nox.Session) -> None:
    """Generate our standalone Lark parsers"""
    session.install('-r', 'pipelines/requirements/deps/lark.txt')

    generate_parsers(session, check='--check' in session.posargs)
