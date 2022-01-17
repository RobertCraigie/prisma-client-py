from pytest_benchmark.fixture import (  # pyright: reportMissingTypeStubs=false
    BenchmarkFixture,
)
from prisma import Client, get_client
from prisma.models import Book
from prisma.types import BookCreateInput


def test_create_scalars(benchmark: BenchmarkFixture) -> None:
    data: BookCreateInput = {
        'title': 'The Great Gatsby',
        'rating': 10,
    }
    result = benchmark(Book.prisma().create, data=data)
    assert isinstance(result, Book)


def test_create_with_relation(benchmark: BenchmarkFixture) -> None:
    data: BookCreateInput = {
        'title': 'The Great Gatsby',
        'rating': 10,
        'author': {
            'create': {
                'name': 'F. Scott Fitzgerald',
            },
        },
    }
    result = benchmark(Book.prisma().create, data=data)
    assert isinstance(result, Book)


def test_batched_create(benchmark: BenchmarkFixture) -> None:
    def do(client: Client) -> None:
        with client.batch_() as batcher:
            for _ in range(100):
                batcher.book.create(
                    data={
                        'title': 'Holes',
                        'rating': 9,
                    },
                )

    benchmark(do, get_client())
