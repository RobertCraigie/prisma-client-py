# NOTE: This dockerfile should only be used for internal testing purposes
# and should not form the basis of an official image pushed out
# to a registry
ARG PYTHON_VERSION=3.10
ARG OS_DISTRO=slim-bullseye

FROM python:${PYTHON_VERSION}-${OS_DISTRO}

# These are are own build args recorded as env variables
ARG OS_DISTRO
ENV OS_DISTRO=${OS_DISTRO}
ENV PRISMA_USER_ID=9999

# These are provided by Docker
ARG BUILDPLATFORM
ARG BUILDOS
ARG BUILDARCH
ARG BUILDVARIANT
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH

ENV DOCKER_BUILDPLATFORM=${BUILDPLATFORM}
ENV DOCKER_BUILDOS=${BUILDOS}
ENV DOCKER_BUILDARCH=${BUILDARCH}
ENV DOCKER_BUILDVARIANT=${BUILDVARIANT}
ENV DOCKER_TARGETPLATFORM=${TARGETPLATFORM}
ENV DOCKER_TARGETOS=${TARGETOS}
ENV DOCKER_TARGETARCH=${TARGETARCH}

# TODO: Using the slim variant is a bit hackier. Better to
# cat and grep /etc/*release*. Also, the [[ ]] command
# is a bash thing so that's why we subshell for the test
RUN \
    if [[ $OS_DISTRO =~ alpine ]]; then \
      adduser -u ${PRISMA_USER_ID} -D prisma; \
      apk add gcc musl-dev yaml-dev yaml libffi-dev git; \
    elif bash -c "[[ ${OS_DISTRO} =~ slim ]]"; then \
      useradd --create-home --uid ${PRISMA_USER_ID} --shell /bin/bash prisma; \
      apt-get update; \
      apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        apt-transport-https; \
      # Cleanup to reduce image size
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
    else \
      echo "Unrecognized distro $OS_DISTRO"; \
      exit 99; \
    fi

USER prisma
WORKDIR /home/prisma/prisma-client-py
ENV PATH="/home/prisma/.local/bin:${PATH}"

COPY --chown=prisma:prisma . .

RUN pip install --upgrade pip && \
    pip install . && \
    pip install -U -r pipelines/requirements/dev.txt

# This has the side-effect of downing the prisma binaries
# and will fail if the CLI cannot get run
RUN prisma -v

# Very light-weight test that CLI generation works
RUN prisma generate --schema ./tests/data/schema.prisma

# Ensure all combinations of non-global Node resolvers work
RUN nox -s test -p 3.10 -- tests/test_node

# Ensure database access using SQLite works
ENV SQLITE_URL="file:sqlite.db"

# We don't run linters here because pyright-python is currently broken in certain docker images
# TODO: lint when fixed
RUN nox -s databases -- test --databases=sqlite --no-lint
