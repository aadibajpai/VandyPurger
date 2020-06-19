import asyncio
import discord
import os
from datetime import datetime, timedelta

from discord.ext import commands, tasks

bot = commands.Bot(command_prefix='v;')

target_channel_id = 702296171829264394  # wellness-office in vandy discord
# target_channel_id = 722609125950750771  # testing
activity = True


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(name="the clock.", type=3))
    print(f'{bot.user.name} is running...')


def time_to_sleep():
    now = datetime.utcnow()
    # 10am UTC is 5am Vandy time
    remaining = (timedelta(hours=24) - (now - now.replace(hour=10,
                                                          minute=0,
                                                          second=0,
                                                          microsecond=0))).total_seconds() % (24 * 3600)
    return remaining


@tasks.loop(minutes=30)
async def daily_purge():
    purge_channel = bot.get_channel(target_channel_id)
    messages = await purge_channel.history(limit=1).flatten()
    last_message_time = messages[0].created_at
    print(f"{datetime.utcnow() - last_message_time}")

    if datetime.utcnow() - last_message_time >= timedelta(minutes=30):
        await purge_channel.send(f"Messages about to be purged in `10` seconds in channel {purge_channel.mention}")
        print('About to be yeeted.')
        await asyncio.sleep(10)
        deleted = await purge_channel.purge(limit=500)
        await purge_channel.send(f"Yeeted {len(deleted)} messages.")
        remaining = time_to_sleep()
        await purge_channel.send(f"Going to sleep for {remaining} seconds.")
        print(f"Going to sleep for {remaining} seconds.")
        await asyncio.sleep(remaining)
    else:
        print("Purge snoozed for 30 minutes")


@daily_purge.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")
    remaining = time_to_sleep()
    print(f"Going to sleep for {remaining} seconds.")
    await asyncio.sleep(remaining)


daily_purge.start()


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {bot.latency * 1000:.03f}ms")


bot.run(os.environ["DISCORD_TOKEN"])
