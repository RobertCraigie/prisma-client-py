from ...utils import Testdir


def test_cleanup_between_tests(testdir: 'Testdir') -> None:
    def tests() -> None:
        import pytest
        from prisma import Client

        @pytest.mark.asyncio
        async def test_1(prisma: Client) -> None:
            assert await prisma.user.count() == 0
            user = await prisma.user.create({'name': 'Robert'})
            assert user.name == 'Robert'

        @pytest.mark.asyncio
        async def test_2(prisma: Client) -> None:
            assert await prisma.user.count() == 0

    testdir.make_from_function(tests)
    testdir.runpytest().assert_outcomes(passed=2)
