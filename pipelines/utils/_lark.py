from pathlib import Path

import nox

ROOT = Path(__file__).parent.parent.parent


def generate_parsers(session: nox.Session, *, check: bool) -> None:
    generate_parser(
        session,
        grammar=ROOT.joinpath('grammars/schema.lark'),
        to=ROOT.joinpath('src/prisma/_vendor/lark_schema_parser.py'),
        check=check,
    )
    generate_parser(
        session,
        grammar=ROOT.joinpath('grammars/schema_scan.lark'),
        to=ROOT.joinpath('src/prisma/_vendor/lark_schema_scan_parser.py'),
        check=check,
    )


def generate_parser(session: nox.Session, *, grammar: Path, to: Path, check: bool) -> None:
    """Generate a standalone lark parser to the given location.

    Optionally check if there is a git diff.
    """
    output = session.run(
        'python',
        '-m',
        'lark.tools.standalone',
        str(grammar),
        silent=True,
        env={'PYTHONHASHSEED': '0'},
    )
    assert isinstance(output, str)
    to.write_text(output)

    if check:
        # Note: we can't check if there is a diff for the standalone parsers
        # because of https://github.com/lark-parser/lark/issues/1194
        # try:
        #     session.run('git', 'diff', '--quiet', str(to.relative_to(ROOT)), silent=True, external=True)
        # except CommandFailed:
        #     print(
        #         f'There is a diff for the generated {to.relative_to(ROOT)} parser; You need to run `nox -r -s lark` & commit the changes'
        #     )
        #     raise
        ...
