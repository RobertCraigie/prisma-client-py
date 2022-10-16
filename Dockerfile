ARG PYTHON_VERSION=3.10
ARG OS_DISTRO=slim-bullseye

FROM python:${PYTHON_VERSION}-${OS_DISTRO}

RUN useradd --create-home --uid 9999 --shell /bin/bash prisma

USER prisma
WORKDIR /home/prisma/prisma-client-py
ENV PATH="/home/prisma/.local/bin:${PATH}"

COPY --chown=prisma:prisma . .

RUN pip install .

# This has the side-effect of downing the prisma binaries
# and will fail if the CLI cannot get run
RUN prisma -v

# Very light-weight test that CLI generation works
RUN prisma generate --schema ./tests/data/schema.prisma
