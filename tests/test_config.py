import warnings
from typing import cast
from pathlib import Path
from textwrap import dedent

from mock import MagicMock
from pytest_mock import MockerFixture

from prisma.utils import temp_env_update
from prisma._compat import model_fields, _get_field_env_var
from prisma._config import Config, LazyConfigProxy

from .utils import Testdir


def test_lazy_proxy(mocker: MockerFixture) -> None:
    """Laxy proxy only instantiates Config once"""
    proxy = cast(Config, LazyConfigProxy())

    # ignore deprecation warnings as the mocker implicitly accesses deprecated properties
    mocked = cast(MagicMock, None)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        mocked = mocker.patch.object(Config, 'load', spec=Config)

    print(proxy.binary_cache_dir)  # implicitly load the config
    mocked.assert_called_once()

    for _ in range(10):
        print(proxy.expected_engine_version)

    mocked.assert_called_once()


def test_no_file(testdir: Testdir) -> None:
    """Config loading works with no pyproject.toml present"""
    path = Path('pyproject.toml')
    assert not path.exists()

    config = Config.load(path)
    assert isinstance(config.prisma_version, str)


def test_loading(testdir: Testdir) -> None:
    """Config loading overrides defaults"""
    testdir.makefile(
        '.toml',
        pyproject=dedent(
            """
            [tool.prisma]
            prisma_version = '0.1.2.3'
            """
        ),
    )
    config = Config.load()
    assert config.prisma_version == '0.1.2.3'

    # updated options are used in computed options
    assert '0.1.2.3' in str(config.binary_cache_dir)


def test_allows_extra_keys(testdir: Testdir) -> None:
    """Config loading allows unknown options to be present in the config file"""
    testdir.makefile(
        '.toml',
        pyproject=dedent(
            """
            [tool.prisma]
            foo = 'bar'
            prisma_version = '0.3'
            """
        ),
    )
    config = Config.load()
    assert config.prisma_version == '0.3'
    assert not hasattr(config, 'foo')


def test_env_var_takes_priority(testdir: Testdir) -> None:
    """Any env variable present should be used instead of the given option"""
    testdir.makefile(
        '.toml',
        pyproject=dedent(
            """
            [tool.prisma]
            prisma_version = '0.3'
            """
        ),
    )
    config = Config.load()
    assert config.prisma_version == '0.3'

    with temp_env_update({'PRISMA_VERSION': '1.5'}):
        config = Config.load()
        assert config.prisma_version == '1.5'


def test_every_option_loads_from_the_environment() -> None:
    """Every config option must explicitly specify an  environment variable to load from
    to ensure that it can be easily set dynamically
    """
    for name, field in model_fields(Config).items():
        assert (
            _get_field_env_var(field, name=name) is not None
        ), f'The {name} option does not specify an environment variable to load from'
