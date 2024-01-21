import os
from typing import Iterator

import pytest

from prisma import Prisma, load_env

from .utils import Testdir

ENV_KEY = '_PRISMA_PY_TESTING_DOTENV_DATABSE_URL'
DEFAULT_VALUE = 'file:dev.db'


def make_env_file(testdir: Testdir, name: str = '.env') -> None:
    path = testdir.path.joinpath(name)
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    with path.open('w') as file:
        file.write(f'export {ENV_KEY}="{DEFAULT_VALUE}"')


@pytest.fixture(autouse=True)
def clear_env(testdir: Testdir) -> Iterator[None]:
    os.environ.pop(ENV_KEY, None)

    yield

    paths = [
        testdir.path.joinpath('.env'),
        testdir.path.joinpath('prisma/.env'),
    ]
    for path in paths:
        if path.exists():  # pragma: no branch
            path.unlink()


@pytest.mark.parametrize('name', ['.env', 'prisma/.env'])
def test_client_loads_dotenv(testdir: Testdir, name: str) -> None:
    """Initializing the client overrides os.environ variables"""
    make_env_file(testdir, name=name)

    Prisma(use_dotenv=False)
    assert ENV_KEY not in os.environ

    Prisma()
    assert ENV_KEY in os.environ


def test_load_env_no_files(testdir: Testdir) -> None:
    """Loading dotenv files without any files present does not error"""
    assert len(list(testdir.path.iterdir())) == 0
    load_env()
    assert ENV_KEY not in os.environ


def test_system_env_takes_priority(testdir: Testdir) -> None:
    """When an environment variable is present in both the system env and the .env file,
    the system env should take priority.
    """
    make_env_file(testdir)
    os.environ[ENV_KEY] = 'foo'

    Prisma()
    assert os.environ[ENV_KEY] == 'foo'

    os.environ.pop(ENV_KEY)
    Prisma()
    assert os.environ[ENV_KEY] == DEFAULT_VALUE
