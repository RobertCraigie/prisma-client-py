# NOTE: This dockerfile should only be used for internal testing purposes
# and should not form the basis of an official image pushed out
# to a registry

FROM winamd64/python:3.10

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

# Imports the cert into the "local" trust store, whatever that means (user specific?)
RUN Set-PSDebug -Trace 2; \
    $CERTIFI_LOCATION = python -c \"import certifi; print(certifi.where())\"; \
    Import-Certificate \
    -FilePath $CERTIFI_LOCATION;

COPY . .

RUN pip install .[dev]

# This has the side-effect of downing the prisma binaries
# and will fail if the CLI cannot get run
RUN prisma -v

# Very light-weight test that CLI generation works
RUN prisma generate --schema ./tests/data/schema.prisma
