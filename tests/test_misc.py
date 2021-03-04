import pytest
from prisma.models import User


def test_create_partial_raises_outside_generation() -> None:
    with pytest.raises(RuntimeError) as exc:
        User.create_partial('PartialUser', exclude={'name'})
    assert 'outside of client generation' in str(exc.value)
