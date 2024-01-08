import inspect

from prisma import Prisma


def test_ensure_batch_and_action_signatures_are_equal(client: Prisma) -> None:
    """Batch method signature is the same as it's corresponding client method

    This is to ensure that if an client method is updated then it's corresponding
    batch method must also be updated.

    I acknowledge that the presence of this test would normally be considered the
    result of an anti-pattern but I could not figure out any good method for
    implementing batching and client methods together while maintaining static
    type safety and without making the templates horrible to maintain. If you
    have found a method that you think is good please make an issue/PR.
    """
    actions = client.user
    for name, meth in inspect.getmembers(client.batch_().user, inspect.ismethod):
        if name.startswith('_'):
            continue

        actual = inspect.signature(meth).replace(return_annotation=inspect.Signature.empty)
        expected = inspect.signature(getattr(actions, name)).replace(return_annotation=inspect.Signature.empty)
        assert actual == expected, f'{name} methods are inconsistent'
