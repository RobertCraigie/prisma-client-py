from typing import TYPE_CHECKING

import pytest
from fastapi import FastAPI

from prisma.models import User
from prisma.errors import UnsupportedSubclassWarning


# pyright: reportUnusedClass=false


def test_subclassing_warns() -> None:
    """Subclassing a prisma model without using recursive types should raise a
    warning as it will cause unexpected behaviour when static type checking as
    action methods will be typed to return the base class, not the sub class.
    """
    # For some indiscernible reason, this code causes mypy to crash...
    #
    # The `exclude` option doesn't help us because of the way mypy works it still causes it to crash.
    #
    # I do not have the time nor the willpower to investigate why this happens so we resort to this solution.
    if not TYPE_CHECKING:  # pragma: no branch
        with pytest.warns(UnsupportedSubclassWarning):

            class MyUser(User):
                pass

            class MyUser2(User, warn_subclass=False):
                pass

            # ensure other arguments can be passed to support multiple inheritance
            class MyUser3(User, warn_subclass=False, foo=1):
                pass


# NOTE: we only include a FastAPI test here as it is a small dependency
# if we need to ignore warnings for other packages, we do not need unit tests


def test_subclass_ignores_fastapi_response_model() -> None:
    """FastAPI implicitly creates new types from the model passed to response_model.
    This calls __init_subclass__ which will raise warnings that users cannot do anything about.
    """
    # this test may look like it does not test anything but as we turn
    # warnings into errors when running pytest, this will catch any
    # warnings we raise
    app = FastAPI()

    @app.get('/', response_model=User)
    async def _() -> None:  # pragma: no cover
        ...
