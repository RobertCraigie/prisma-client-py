import webbrowser
from pathlib import Path

import nox

from pipelines.utils import setup_env, CACHE_DIR


@nox.session
def setup(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/coverage.txt')
    session.run('coverage', 'erase')


def _setup_report(session: nox.Session) -> None:
    # TODO: generate in place for coverage parsing?
    session.env['COVERAGE_FILE'] = str(CACHE_DIR / '.coverage')
    session.install('-r', 'pipelines/requirements/coverage.txt')

    print('--- debug ---')
    for p in CACHE_DIR.iterdir():
        print(p)
    print('--- debug ---')

    if '--no-combine' not in session.posargs:
        session.run('coverage', 'combine')

    session.run('coverage', 'html', '-i')
    session.run('coverage', 'xml', '-i')

    if '--open' in session.posargs:
        url = f'file://{Path.cwd() / "htmlcov" / "index.html"}'
        print(f'Opening browser at {url}')
        webbrowser.open(url)


@nox.session
def report(session: nox.Session) -> None:
    _setup_report(session)

    session.run('coverage', 'report', '-i', '--skip-covered')


@nox.session(name='report-strict')
def report_strict(session: nox.Session) -> None:
    """Like `report` but will error if coverage doesn't meet certain requirements"""
    _setup_report(session)

    session.run(
        'coverage',
        'report',
        '-i',
        '--skip-covered',
        '--include=tests/**',
        '--fail-under=100',
    )
