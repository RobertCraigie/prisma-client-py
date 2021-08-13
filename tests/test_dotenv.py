import os

import pytest
from prisma import Client, load_env

from .utils import Testdir


ENV_KEY = '_PRISMA_PY_TESTING_DOTENV_DATABSE_URL'


def make_env_file(testdir: Testdir, name: str) -> None:
    path = testdir.path.joinpath(name)
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    with path.open('w') as file:
        file.write(f'export {ENV_KEY}="file:dev.db"')


@pytest.fixture(autouse=True)
def clear_env() -> None:
    os.environ.pop(ENV_KEY, None)


@pytest.mark.parametrize('name', ['.env', 'prisma/.env'])
def test_client_loads_dotenv(testdir: Testdir, name: str) -> None:
    """Initializing the client overrides os.environ variables"""
    make_env_file(testdir, name=name)

    Client(use_dotenv=False)
    assert ENV_KEY not in os.environ

    Client()
    assert ENV_KEY in os.environ


def test_load_env_no_files(testdir: Testdir) -> None:
    """Loading dotenv files without any files present does not error"""
    assert len(list(testdir.path.iterdir())) == 0
    load_env()
    assert ENV_KEY not in os.environ
