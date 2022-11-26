import os
import shutil
import webbrowser
from pathlib import Path

import nox
from git.repo import Repo

from lib.utils import maybe_decode
from pipelines.utils import setup_env, CACHE_DIR, TMP_DIR


BADGE_BRANCH = 'static/coverage'


@nox.session(name='push-coverage')
def push_coverage(session: nox.Session) -> None:
    session.env['COVERAGE_FILE'] = str(CACHE_DIR / '.coverage')
    session.install(
        '-r',
        'pipelines/requirements/coverage.txt',
        '-r',
        'pipelines/requirements/deps/coverage-badge.txt',
    )

    svg_path = TMP_DIR / 'coverage.svg'

    with session.chdir(CACHE_DIR):
        session.run(
            'coverage-badge', '-o', str(svg_path), '--cov-ignore-errors'
        )

    repo = Repo(Path.cwd())
    if repo.is_dirty():
        raise ValueError(
            f'Expected repo to not be dirty; Untracked files: {repo.untracked_files}'
        )

    head_summary = maybe_decode(repo.head.commit.summary)

    git = repo.git
    git.fetch('--all')
    git.checkout(f'origin/{BADGE_BRANCH}', b=BADGE_BRANCH)

    if not repo.is_dirty(untracked_files=True):
        print('No changes!')
        return

    if os.environ.get('CI'):
        git.config('user.name', 'github-actions[bot]')
        git.config(
            'user.email',
            '41898282+github-actions[bot]@users.noreply.github.com',
        )

    shutil.copy(svg_path, 'coverage.svg')

    git.add('coverage.svg')
    git.commit(
        m=head_summary,
        env={
            'PRE_COMMIT_ALLOW_NO_CONFIG': '1',
        },
    )
    git.push('origin', BADGE_BRANCH)
    print('Pushed new coverage badge!')


@nox.session
def setup(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/coverage.txt')
    session.run('coverage', 'erase')


def _setup_report(session: nox.Session) -> None:
    # TODO: generate in place for coverage parsing?
    session.env['COVERAGE_FILE'] = str(CACHE_DIR / '.coverage')
    session.install('-r', 'pipelines/requirements/coverage.txt')

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

    # core tests
    session.run(
        'coverage',
        'report',
        '-i',
        '--skip-covered',
        '--include=tests/**',
        # integration tests are broken
        '--omit=tests/integrations/conftest.py',
        '--fail-under=100',
    )

    # database tests
    session.run(
        'coverage',
        'report',
        '-i',
        '--skip-covered',
        '--include=databases/tests/**',
        '--fail-under=100',
    )
