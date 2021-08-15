# Flask URL Shortener Example

This example uses the [Flask](https://flask.palletsprojects.com/) micro framework to create a basic URL shortener using Prisma.

The code in this example has been modified from: [https://www.digitalocean.com/community/tutorials/how-to-make-a-url-shortener-with-flask-and-sqlite](https://www.digitalocean.com/community/tutorials/how-to-make-a-url-shortener-with-flask-and-sqlite)

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

Run the Flask HTTP server
```sh
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

Try out the URL Shortener by opening `http://127.0.0.1:5000` in your browser!

## Type Checking

If you want to modify the code you should also type check it, you can do so with [pyright](https://github.com/microsoft/pyright).

Install
> For full disclosure it should be noted that I maintain the PyPi package for pyright which is a wrapper over the official version
```sh
pip install -U -r types.txt pyright
```

Run
```sh
pyright
```
