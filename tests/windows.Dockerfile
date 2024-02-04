# NOTE: This dockerfile should only be used for internal testing purposes
# and should not form the basis of an official image pushed out
# to a registry

FROM winamd64/python:3.11

ENV PRISMA_PY_DEBUG=1

WORKDIR /home/prisma/prisma-client-py

# https://github.com/docker-library/python/issues/359
RUN certutil -generateSSTFromWU roots.sst; certutil -addstore -f root roots.sst;  del roots.sst

# Download and install Git
RUN Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.32.0.windows.1/Git-2.32.0-64-bit.exe" -OutFile "git-installer.exe" -UseBasicParsing; \
    Start-Process ./git-installer.exe -ArgumentList '/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS' -NoNewWindow -Wait; \
    Remove-Item git-installer.exe
RUN git --version

COPY . .

RUN pip install . -r pipelines/requirements/dev.txt

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
