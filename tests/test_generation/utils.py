import os
import sys
import inspect
import textwrap
import subprocess
from typing import Optional, Union, Any

import py
from _pytest.pytester import RunResult, Testdir as PytestTestdir
from prisma._types import FuncType


# as we are generating new modules we need to clear them from
# the module cache so that python actually picks them up
# when we import them again, however we also have to ignore
# any prisma.generator modules as we rely on the import caching
# mechanism for loading partial model types
IMPORT_RELOADER = '''
import sys
for name in sys.modules.copy():
    if 'prisma' in name and 'generator' not in name:
        sys.modules.pop(name, None)
'''


class Testdir:
    __test__ = False

    def __init__(self, testdir: PytestTestdir) -> None:
        self.testdir = testdir

    def make_from_function(
        self,
        function: FuncType,
        ext: str = '.py',
        name: Optional[str] = None,
        **env: Any,
    ) -> None:
        source = get_source_from_function(function, **env)

        if name:
            self.makefile(ext, **{name: source})
        else:
            self.makefile(ext, source)

    def generate(self, schema: str, options: str = '') -> None:
        path = self.tmpdir.join('schema.prisma')
        path.write(schema.format(output=self.tmpdir.join('prisma'), options=options))
        args = [sys.executable, '-m', 'prisma', 'generate', f'--schema={path}']
        proc = subprocess.run(  # pylint: disable=subprocess-run-check
            args,
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(str(proc.stdout, 'utf-8'), file=sys.stdout)
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode, args, proc.stdout, proc.stderr
            )

    def makefile(self, ext: str, *args: str, **kwargs: str) -> None:
        self.testdir.makefile(ext, *args, **kwargs)

    def runpytest(
        self, *args: Union[str, 'os.PathLike[str]'], **kwargs: Any
    ) -> RunResult:
        return self.testdir.runpytest(*args, **kwargs)

    @property
    def tmpdir(self) -> py.path.local:
        return self.testdir.tmpdir

    def __repr__(self) -> str:  # pragma: no cover
        return str(self)

    def __str__(self) -> str:  # pragma: no cover
        return f'<Testdir {self.tmpdir} >'


def get_source_from_function(function: FuncType, **env: Any) -> str:
    lines = inspect.getsource(function).splitlines()[1:]

    # setup env after imports
    for index, line in enumerate(lines):
        if not line.lstrip(' ').startswith(('import', 'from')):
            start = index
            break
    else:
        start = 0

    lines = textwrap.dedent('\n'.join(lines)).splitlines()
    for name, value in env.items():
        if isinstance(value, str):
            value = f'\'{value}\''

        lines.insert(start, f'{name} = {value}')

    return IMPORT_RELOADER + '\n'.join(lines)
