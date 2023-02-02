from typing import TYPE_CHECKING

import pytest

from prisma.models import User


# pyright: reportUnusedClass=false


def test_subclass_warn_subclass_argument_deprecated() -> None:
    """The class argument `wan_subclass` is deprecated"""
    with pytest.warns(
        DeprecationWarning, match='The `warn_subclass` argument is deprecated'
    ):

        class MyUser(User, warn_subclass=False):
            pass

    with pytest.warns(
        DeprecationWarning, match='The `warn_subclass` argument is deprecated'
    ):

        class MyUser2(User, warn_subclass=True):
            pass
