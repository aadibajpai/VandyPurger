import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands, tasks

bot = commands.Bot(".")


target_channel_id = 722609125950750771
activity = True


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(name="the clock!!!", type=3))
    print(f'{bot.user.name} is running....')


@bot.event
async def on_message(message):
    global activity
    try:
        msg = await bot.wait_for('message', timeout=10.0)
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
        print("Purge delayed for 10 seconds")
    else:
        purge_channel = bot.get_channel(target_channel_id)
        print(f"Messages about to purge in `10` seconds in channel {purge_channel.mention}")
        await asyncio.sleep(10)
        await purge_channel.purge()
        print("Cleared")
        now = datetime.utcnow()
        remaining = (timedelta(hours=24) - (now - now.replace(hour=10,
                                                              minute=00,
                                                              second=0,
                                                              microsecond=0))).total_seconds() % (24 * 3600)
        print(f"Going to sleep for {remaining} seconds")
        await asyncio.sleep(remaining)


@daily_purge.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")

daily_purge.start()


@bot.command()
async def channel(ctx):
    global target_channel_id
    target_channel_id = ctx.channel.id
    await ctx.send(f"Channel set to {target_channel_id.mention}")


bot.run("Token")
