import os
import shutil
import webbrowser
from pathlib import Path

import nox

from lib.utils import maybe_decode
from pipelines.utils import TMP_DIR, CACHE_DIR, setup_env

BADGE_BRANCH = 'static/coverage'
TMP_SVG_PATH = TMP_DIR / 'coverage.svg'
TMP_HTMLCOV_PATH = TMP_DIR / 'htmlcov'
TMP_README_PATH = TMP_DIR / 'README.md'


@nox.session(name='push-coverage')
def push_coverage(session: nox.Session) -> None:
    """Push the coverage report to a specific coverage branch. Only for CI"""
    # We have to import `git` here as it will cause an error on machines that don't have
    # git installed. This happens in our docker tests.
    from git.repo import Repo

    session.env['COVERAGE_FILE'] = str(CACHE_DIR / '.coverage')
    session.install(
        '-r',
        'pipelines/requirements/coverage.txt',
        '-r',
        'pipelines/requirements/deps/coverage-badge.txt',
    )

    with session.chdir(CACHE_DIR):
        session.run('coverage-badge', '-o', str(TMP_SVG_PATH), '--cov-ignore-errors')

    shutil.copytree('htmlcov', TMP_HTMLCOV_PATH)

    repo = Repo(Path.cwd())
    if repo.is_dirty():
        raise ValueError(f'Expected repo to not be dirty; Untracked files: {repo.untracked_files}')

    head_summary = maybe_decode(repo.head.commit.summary)

    git = repo.git
    git.fetch('--all')
    git.checkout(f'origin/{BADGE_BRANCH}', b=BADGE_BRANCH)

    shutil.copy('README.md', TMP_README_PATH)

    # ensure only the files relevant to the static branch will be present
    git.rm('-rf', '.')

    shutil.copy(TMP_SVG_PATH, 'coverage.svg')
    shutil.copy(TMP_README_PATH, 'README.md')

    htmlcov = Path.cwd() / 'htmlcov'
    if htmlcov.exists():
        # remove the `htmlcov` directory in case it exists so that we
        # don't include now redundant files.
        shutil.rmtree(htmlcov)

    shutil.copytree(TMP_HTMLCOV_PATH, htmlcov)

    # stage potential changes
    git.add('-f', 'htmlcov/*')
    git.add('coverage.svg')
    git.add('README.md')

    if not repo.is_dirty():
        print('No changes!')
        return

    if os.environ.get('CI'):
        git.config('user.name', 'github-actions[bot]')
        git.config(
            'user.email',
            '41898282+github-actions[bot]@users.noreply.github.com',
        )

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
    """Cleans up the environment to prepare for coverage tracking"""
    setup_env(session)
    session.install('-r', 'pipelines/requirements/coverage.txt')
    session.run('coverage', 'erase')


def _setup_report(session: nox.Session) -> None:
    session.env['COVERAGE_FILE'] = str(CACHE_DIR / '.coverage')
    session.install('-r', 'pipelines/requirements/coverage.txt')

    # generate in place so that coverage can parse the generated files
    session.install('-e', '.')
    session.run('prisma', 'generate', '--schema=tests/data/schema.prisma')

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
    """Generate a test coverage report"""
    _setup_report(session)

    session.run('coverage', 'report', '-i', '--skip-covered')


@nox.session(name='report-strict')
def report_strict(session: nox.Session) -> None:
    """Like `report` but will error if coverage doesn't meet certain requirements"""
    _setup_report(session)

    # core tests
    omit_files = [
        # integration tests are broken
        'tests/integrations/conftest.py',
        # difficult to run under coverage + not valuable to figure out
        'tests/test_generation/exhaustive/partials.py',
    ]
    session.run(
        'coverage',
        'report',
        '-i',
        '--skip-covered',
        '--include=tests/**',
        f'--omit={",".join(omit_files)}',
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

    # output overall coverage
    session.run('coverage', 'report', '-i', '--skip-covered')
