# Install

As Prisma Client Python supports synchronous and asynchronous use cases, you must specify the http library that the client will use to communicate with the internal [query engine](https://www.prisma.io/docs/concepts/overview/under-the-hood#prisma-engines).

Currently supported libraries are:

* [aiohttp](https://github.com/aio-libs/aiohttp)
* [requests](https://github.com/psf/requests)

## Install Asynchronous Client

```sh
pip install git+https://github.com/RobertCraigie/prisma-client-py#egg=prisma-client[aiohttp]
```

## Install Synchronous Client

```sh
pip install git+https://github.com/RobertCraigie/prisma-client-py#egg=prisma-client[requests]
```
