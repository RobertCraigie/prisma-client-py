# FastAPI Example

This example uses the [FastAPI](https://fastapi.tiangolo.com/) web framework to create a basic HTTP API using Prisma.

## Setup

Create and activate a virtual environment
```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install requirements
```sh
pip install -U -r requirements.txt
```

Setup the database and generate the prisma client
```sh
prisma db push
```

Run the HTTP server
```sh
uvicorn main:app --reload
```

Try out the API by opening `http://127.0.0.1:8000/docs` in your browser!

## Type Checking

If you want to modify the code you should also type check it, you can do so with [pyright](https://github.com/microsoft/pyright).

Install
> For full disclosure it should be noted that I maintain the PyPi package for pyright which is a wrapper over the official version
```sh
pip install -U pyright
```

Run
```sh
pyright
```
