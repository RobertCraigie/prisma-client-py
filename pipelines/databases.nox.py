import nox

from databases.main import entrypoint
from pipelines.utils import setup_env


@nox.session
def databases(session: nox.Session) -> None:
    setup_env(session)
    entrypoint(session)
