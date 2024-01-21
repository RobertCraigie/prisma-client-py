from typing import TYPE_CHECKING

import pytest

from prisma.models import User

# pyright: reportUnusedClass=false


def test_subclass_warn_subclass_argument_deprecated() -> None:
    """The class argument `wan_subclass` is deprecated"""
    # For some indiscernible reason, this code causes mypy to crash...
    #
    # The `exclude` option doesn't help us because of the way mypy works it still causes it to crash.
    #
    # I do not have the time nor the willpower to investigate why this happens so we resort to this solution.
    if not TYPE_CHECKING:
        with pytest.warns(
            DeprecationWarning,
            match='The `warn_subclass` argument is deprecated',
        ):

            class MyUser(User, warn_subclass=False):
                pass

        with pytest.warns(
            DeprecationWarning,
            match='The `warn_subclass` argument is deprecated',
        ):

            class MyUser2(User, warn_subclass=True):
                pass
