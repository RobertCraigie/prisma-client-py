# NOTE: This dockerfile should only be used for internal testing purposes
# and should not form the basis of an official image pushed out
# to a registry

FROM winamd64/python:3.10

WORKDIR /home/prisma/prisma-client-py

COPY . .

RUN pip install .[dev]

# TODO: necessary
RUN pip install python-certifi-win32

# This has the side-effect of downing the prisma binaries
# and will fail if the CLI cannot get run
RUN prisma -v

# Very light-weight test that CLI generation works
RUN prisma generate --schema ./tests/data/schema.prisma

# Ensure all combinations of non-global Node resolvers work
RUN nox -s test -p 3.10 -- tests/test_node
