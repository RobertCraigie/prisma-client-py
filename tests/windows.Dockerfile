# NOTE: This dockerfile should only be used for internal testing purposes
# and should not form the basis of an official image pushed out
# to a registry

FROM python:3.10

ENV PRISMA_PY_DEBUG=1

WORKDIR /home/prisma/prisma-client-py

RUN pip install certifi

# Santity check of powershell invocation
RUN python -c \"import certifi; certifi.where()\"

# https://learn.microsoft.com/en-us/powershell/module/pki/import-certificate?view=windowsserver2022-ps
# Import to the system root -- this should be enough?
RUN Set-PSDebug -Trace 2; \
    $CERTIFI_LOCATION = python -c \"import certifi; print(certifi.where())\"; \
    Import-Certificate \
    -FilePath $CERTIFI_LOCATION \
    -CertStoreLocation Cert:\LocalMachine\Root\;

# Use the host system certificates
# https://gitlab.com/alelec/pip-system-certs
RUN pip install pip_system_certs

COPY . .

RUN pip install .[dev]

# This has the side-effect of downing the prisma binaries
# and will fail if the CLI cannot get run
RUN prisma -v

# Very light-weight test that CLI generation works
RUN prisma generate --schema ./tests/data/schema.prisma

# Ensure all combinations of non-global Node resolvers work
RUN nox -s test -p 3.10 -- tests/test_node
