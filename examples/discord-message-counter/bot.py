from typing import Optional, TYPE_CHECKING

import discord
from discord.ext import commands  # pyright: reportMissingTypeStubs=false
from prisma import Client


# commands.Bot is only a Generic Type while type checking
# thats why we have to do this little dance around it
if TYPE_CHECKING:
    BotBase = commands.Bot['Context']
else:
    BotBase = commands.Bot


class Context(commands.Context):
    bot: 'Bot'


class Bot(BotBase):

    # NOTE: we have a pyright disable comment here due to issues with TypeVars.
    # as we know we're right, there's no reason to fight pyright on this
    # so disabling the error is fine, if you can fix this however, I will
    # happily accept a PR

    def __init__(self) -> None:  # pyright: reportGeneralTypeIssues=false
        super().__init__(command_prefix=commands.when_mentioned_or('>'))
        self.prisma = Client()

    async def on_message(self, message: discord.Message) -> None:
        await self.prisma.channel.upsert(
            where={
                'id': str(message.channel.id),
            },
            data={
                'create': {
                    'id': str(message.channel.id),
                    'total': 1,
                },
                'update': {
                    'total': {
                        'increment': 1,
                    },
                },
            },
        )
        await super().on_message(message)


bot = Bot()


@bot.command()
async def total(ctx: Context, channel: Optional[discord.TextChannel] = None) -> None:
    if channel is None and isinstance(ctx.channel, discord.TextChannel):
        channel = ctx.channel
    else:
        await ctx.send('Could not resolve channel, TODO')
        return

    record = await ctx.bot.prisma.channel.find_unique(
        where={
            'id': str(channel.id),
        },
    )
    if record is None:
        await ctx.send(
            f'No messages have been sent in {channel.mention} since I\'ve been here!'
        )
    else:
        await ctx.send(
            f'{record.total} messages have been sent in {channel.mention} since I\'ve been here!'
        )
