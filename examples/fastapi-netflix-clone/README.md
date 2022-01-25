# FastAPI Netflix Clone

NOTE: this example is still a work in progress.

This example is adapted from freeCodeCamp's tutorial for [creating a Netflix clone using Django and Tailwind CSS](https://www.freecodecamp.org/news/create-a-netflix-clone-with-django-and-tailwind-css/) to use [FastAPI](https://fastapi.tiangolo.com/) and Prisma Client Python.

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

Seed the database with some data
```sh
python seed.py
```

Run the HTTP server
```sh
uvicorn app.main:app --reload
```

Try out the Netflix Clone by opening `http://127.0.0.1:8000` in your browser!

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
