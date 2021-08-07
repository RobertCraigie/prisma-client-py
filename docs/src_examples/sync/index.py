from prisma import Client


def main() -> None:
    db = Client()
    db.connect()

    post = db.post.create(
        {
            'title': 'Hello from prisma!',
            'desc': 'Prisma is a database toolkit and makes databases easy.',
            'published': True,
        }
    )
    print(f'created post: {post.json(indent=2, sort_keys=True)}')

    found = db.post.find_unique(where={'id': post.id})
    assert found is not None
    print(f'found post: {found.json(indent=2, sort_keys=True)}')

    db.disconnect()


if __name__ == '__main__':
    main()
