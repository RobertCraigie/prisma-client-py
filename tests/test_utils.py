import asyncio
from typing import Type, NoReturn

import pytest

from prisma.utils import ExcConverter


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('convert_exc', 'raised_exc_type', 'expected_exc_type', 'should_be_converted'),
    [
        pytest.param(ExcConverter({ValueError: ImportError}), ValueError, ImportError, True, id='should convert'),
        pytest.param(
            ExcConverter({ValueError: ImportError}), RuntimeError, RuntimeError, False, id='should not convert'
        ),
    ],
)
async def test_exc_converter(
    convert_exc: ExcConverter,
    raised_exc_type: Type[BaseException],
    expected_exc_type: Type[BaseException],
    should_be_converted: bool,
) -> None:
    """Ensure that `prisma.utils.ExcConverter` works as expected."""

    # Test sync context manager
    with pytest.raises(expected_exc_type) as exc_info_1:
        with convert_exc:
            raise raised_exc_type()

    # Test async context manager
    with pytest.raises(expected_exc_type) as exc_info_2:
        async with convert_exc:
            await asyncio.sleep(0.1)
            raise raised_exc_type()

    # Test sync decorator
    with pytest.raises(expected_exc_type) as exc_info_3:

        @convert_exc
        def help_func() -> NoReturn:
            raise raised_exc_type()

        help_func()

    # Test async decorator
    with pytest.raises(expected_exc_type) as exc_info_4:

        @convert_exc
        async def help_func() -> NoReturn:
            await asyncio.sleep(0.1)
            raise raised_exc_type()

        await help_func()

    # Test exception cause
    if should_be_converted:
        assert all(
            (
                type(exc_info_1.value.__cause__) is raised_exc_type,
                type(exc_info_2.value.__cause__) is raised_exc_type,
                type(exc_info_3.value.__cause__) is raised_exc_type,
                type(exc_info_4.value.__cause__) is raised_exc_type,
            )
        )
