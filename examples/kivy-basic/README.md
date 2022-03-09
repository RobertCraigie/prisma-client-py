# Basic Kivy Example

This example uses [Kivy](https://kivy.org/) along with [KivyMD](https://kivymd.readthedocs.io/en/latest/) to create a very basic app to store and list names of users.

The code in this example is based off of https://www.youtube.com/watch?v=X2MkC1ru3cQ

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

Run the Kivy app

```sh
python app.py
```
