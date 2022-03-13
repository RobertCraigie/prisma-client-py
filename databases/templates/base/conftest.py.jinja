import runpy
from pathlib import Path


# the pytest plugin code will not change between databases and is more general purpose
# code than strictly interfacing with the Client API, as such we just share the plugin
# using a standard python module, a better solution would be to provide a custom installable
# plugin instead.
conftest_path = Path(__file__).parent.parent / 'utils' / '_pytest.py'
globalns = runpy.run_path(str(conftest_path))
globalns.pop('__name__')
globalns.pop('__file__')
globals().update(globalns)
