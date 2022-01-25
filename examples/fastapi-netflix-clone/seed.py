import asyncio
from datetime import datetime
from prisma import Client
from prisma.models import User, Profile, Movie

from app.dependencies.auth import get_password_hash


async def main() -> None:
    client = Client(auto_register=True)
    await client.connect()
    await User.prisma().delete_many()
    await Profile.prisma().delete_many()
    await Movie.prisma().delete_many()

    await User.prisma().create(
        data={
            'username': 'RobertCraigie',
            'first_name': 'Robert',
            'last_name': 'Craigie',
            'email': 'robert@craigie.dev',
            'hashed_password': get_password_hash('password'),
            'profiles': {
                'create': [
                    {
                        'name': 'Robert',
                        'age_limit': 'All',
                    },
                    {
                        'name': 'Tegan',
                        'age_limit': 'All',
                    },
                    {
                        'name': 'Henry',
                        'age_limit': 'Kids',
                    },
                ],
            },
        }
    )
    await Movie.prisma().create(
        data={
            'title': 'Parasite',
            'type': 'Single',
            'age_limit': 'All',
            'created': datetime(2019, 5, 30),
            'thumbnail': 'https://media.newyorker.com/photos/5da4a5c756dcd400082a63ba/master/pass/Brody-Parasite.jpg',
            'description': 'One by one, the crafty members of a destitute family insinuate themselves into the household staff of a wealthy couple living in oblivious privilege.',
        },
    )


if __name__ == '__main__':
    asyncio.run(main())
