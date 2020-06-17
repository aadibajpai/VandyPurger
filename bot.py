import discord
import asyncio
import os

from datetime import datetime, timedelta
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix='v;')


# target_channel_id = 702296171829264394  # wellness-office in vandy discord
target_channel_id = 722609125950750771  # testing
activity = True


def time_to_sleep():
    now = datetime.utcnow()
    # 10am UTC is 5am Vandy time
    # edited rn for test
    remaining = (timedelta(hours=24) - (now - now.replace(hour=21, minute=30, second=0, microsecond=0))).total_seconds() % (24 * 3600)
    return remaining


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(name="the clock.", type=3))
    print(f'{bot.user.name} is running now')
    remaining = time_to_sleep()
    print(f"Going to sleep for {remaining} seconds.")
    await asyncio.sleep(remaining)

@bot.event
async def on_message(message):
    global activity
    try:
        msg = await bot.wait_for('message', timeout=1790.0)
    except asyncio.TimeoutError:
        print("No message")
        activity = False
    else:
        print("Message")
        activity = True
    await bot.process_commands(message)


@tasks.loop(minutes=30)
async def daily_purge():
    global activity
    if activity:
        print("Purge delayed for 30 mins.")
    else:
        purge_channel = bot.get_channel(target_channel_id)
        await purge_channel.send(f"Messages about to be purged in `10` seconds in channel {purge_channel.mention}")
        await asyncio.sleep(10)
        await purge_channel.purge()
        await purge_channel.send("Yeeted.")

        remaining = time_to_sleep()
        await purge_channel.send(f"Going to sleep for {remaining} seconds.")
        await asyncio.sleep(remaining)


@daily_purge.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")

daily_purge.start()


@bot.command()
async def ping(ctx):
    embed = discord.Embed(
        title="Ping",
        colour=0x2859b8,
        description=f'Pong! `Latency: {round(bot.latency * 1000)} ms`')
    await ctx.send(embed=embed)


bot.run(os.environ["DISCORD_TOKEN"])
