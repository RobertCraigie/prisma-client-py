import nox

from databases.main import entrypoint


@nox.session
def databases(session: nox.Session) -> None:
    entrypoint(session)
