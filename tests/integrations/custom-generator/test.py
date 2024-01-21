from pathlib import Path
from textwrap import dedent

ROOTDIR = Path(__file__).parent


def clean(string: str) -> str:
    return dedent(string).lstrip('\n').rstrip('\n')


def test_first() -> None:
    """Default generation"""
    first = ROOTDIR.joinpath('generated.md')
    assert first.read_text() == clean(
        """
        # My Prisma Models

        - User
        - Post
        - Profile
        """
    )


def test_second() -> None:
    """Custom config option and output location"""
    second = ROOTDIR.joinpath('2.md')
    assert second.read_text() == clean(
        """
        # Hello, World!

        - User
        - Post
        - Profile
        """
    )
