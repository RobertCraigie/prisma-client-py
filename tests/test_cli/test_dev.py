import re
import sys
import time
import signal
import threading
import subprocess
from typing import List

import pytest
from _pytest.monkeypatch import MonkeyPatch

from prisma.http import client
from prisma.utils import temp_env_update
from prisma.cli.commands import dev

from ..utils import Runner, Testdir

PRISMA_MODULE = ['coverage', 'run', '-m', 'prisma']


def test_playground_skip_generate_no_client(runner: Runner, monkeypatch: MonkeyPatch) -> None:
    """Passing --skip-generate with a non-generated client raises an error"""

    def mock_return(mod: str) -> bool:
        return False

    monkeypatch.setattr(dev, 'module_exists', mock_return, raising=True)
    result = runner.invoke(['py', 'dev', 'playground', '--skip-generate'])
    assert result.exit_code == 1
    assert result.output == 'Prisma Client Python has not been generated yet.\n'


@pytest.mark.asyncio
@pytest.mark.skip(
    reason='Test is currently broken and the feature is not intended for users anyway',
)
async def test_playground(testdir: Testdir) -> None:
    """Starts local HTTP server"""

    def output_reader(proc: 'subprocess.Popen[bytes]', lines: List[str]) -> List[str]:
        assert proc.stdout is not None
        for line in iter(proc.stdout.readline, b''):
            lines.append(line.decode('utf-8'))

        return lines

    lines: List[str] = []
    schema = testdir.make_schema()
    args = PRISMA_MODULE + ['py', 'dev', 'playground', f'--schema={schema}']

    # ensure host information is still logged
    # with DEBUG logging disabled
    with temp_env_update({'PRISMA_PY_DEBUG': '0'}):
        process = subprocess.Popen(args=args, stdout=subprocess.PIPE)

    thread = threading.Thread(target=output_reader, args=(process, lines))

    try:
        thread.start()

        # TODO: don't naively sleep, instead check the output every <x> time
        #       until it is what we want or a timeout is reached
        time.sleep(8)

        stdout = ''.join(lines)
        print(stdout)

        assert 'Generated Prisma Client Python' in stdout

        match = re.search(r'Started http server on (?P<url>http://127.0.0.1:\d+)', stdout)
        assert match is not None
        url = match.group('url')

        resp = await client.request('GET', url)
        assert resp.status == 200
        assert '<title>Rust Playground</title>' in await resp.text()
    finally:
        if sys.platform == 'win32':  # pragma: no cover
            sig = signal.CTRL_C_EVENT
        else:
            sig = signal.SIGINT

        process.send_signal(sig)
        thread.join(timeout=5)
