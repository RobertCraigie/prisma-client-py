# Discord Message Counter Example

This example uses the [discord.py](https://discordpy.readthedocs.io/en/latest/) library to create a [discord](https://discord.com/) bot that counts how many messages have been sent in a channel using Prisma.

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

Follow along with the [discord.py tutorial](https://discordpy.readthedocs.io/en/latest/discord.html) for creating a bot account and inviting it to a server you have control over.

Replace `<my bot token>` with the token you copied from the tutorial above.

```sh
export BOT_TOKEN='<my bot token>'
```

Run the bot
```sh
python launcher.py
```

Navigate to the server you added the bot to, send a couple of messages and then invoke the `total` command by sending a message like the following:

```
@My Bot total
```

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
