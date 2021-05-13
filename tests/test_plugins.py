import pytest

from prisma import PluginContext, plugins
from prisma._types import FuncType
from prisma.errors import PluginMissingRequiredHookError
from prisma.generator.models import Data

from . import contexts
from .utils import Testdir


@pytest.fixture
def ctx() -> PluginContext:
    return PluginContext(method='generate', data=Data.construct())  # type: ignore[call-arg]


def test_no_hooks_defined(testdir: Testdir, ctx: PluginContext) -> None:
    def plugin() -> None:  # mark: filedef
        from tests import contexts

        contexts.add('loaded')

    with testdir.create_entry_point(plugin):
        assert 'loaded' not in contexts
        ctx.run()
        assert 'loaded' in contexts


def test_wrong_hook_type(testdir: Testdir, ctx: PluginContext) -> None:
    def plugin() -> None:  # mark: filedef
        prisma_generate = 1

    with testdir.create_entry_point(plugin):
        with pytest.raises(TypeError) as exc:
            ctx.run()

    assert (
        'Hook at mod.plugin.prisma_generate is not callable, got <class \'int\'> instead'
        in str(exc)
    )


def test_required_hook_missing(testdir: Testdir, ctx: PluginContext) -> None:
    def plugin_() -> None:  # mark: filedef
        """empty"""

    with testdir.create_entry_point(plugin_, name='plugin'):
        for plugin in plugins.load_plugins(ctx):
            with pytest.raises(PluginMissingRequiredHookError) as exc:
                plugin.run_hook('generate', ctx)

            assert 'Plugin plugin is missing a generate hook.' in str(exc)
