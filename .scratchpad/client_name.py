from contextlib import suppress


# with suppress(Exception):
#     from prisma import Client

with suppress(Exception):
    from prisma import Prisma

with suppress(Exception):
    Prisma = Client


def main():
    db = Prisma()
    print(db)
    print("Hello Worldssssss!")


if __name__ == "__main__":
    main()
