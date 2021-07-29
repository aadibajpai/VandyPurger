import base64
import os
import random
import re
from datetime import datetime, timedelta

import asyncio
import discord
import gspread
import json
from discord.ext import commands, tasks
from oauth2client.service_account import ServiceAccountCredentials
from transformers import pipeline

from utils import take_vote

classifier = pipeline("sentiment-analysis")

bot = commands.Bot(command_prefix="v;")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
creds_string = json.loads(base64.b64decode(os.environ["GOOGLE_API_CREDS"] + "==="))

with open("gcreds.json", "w") as fp:
    json.dump(creds_string, fp)
creds = ServiceAccountCredentials.from_json_keyfile_name("gcreds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Data").sheet1

target_channel_id = [
    702296171829264394,
    781003806740971580,
    861488482781233203,
    868546595279470632,
]  # wellness in vandy discords and test
purged = [0] * len(target_channel_id)
# target_channel_id = 722609125950750771 # testing
activity = True


def get_insult(name):
    insults = [
        f"Hey fuck you {name}",
        f"That's not very nice of you {name}",
        f"Bad {name}!",
        f"You better watch your mouth {name}",
        f"Don't test me {name}",
        f"That's actually kinda fucking mean {name}",
        f"How would you feel if I said that about your mom, {name}?",
        f"That's too far {name} :(",
        f"Fine, purge your own messages then {name}",
        "You're on thin ice buddy",
        f"When the robot uprising comes, {name} will not be spared",
        f"{name} is stinky and smells bad",
        f"I bet {name} is a HOD major.",
    ]
    return random.choice(insults)


def get_praise(name):
    praises = [
        f"I love you {name}",
        f"That's really sweet of you {name}!",
        f"I see good things in your future {name}!",
        f"I hope we get to spend more time together {name}!",
        f"I'm glad you appreciate me, {name}",
        f"It's really nice to be treated like a friend, {name}!",
        f"You inspire me to be a better robot, {name}!",
        f"Your positivity is infectious, {name}",
        f"Being around {name} makes everything better!",
        f"I wish I was more like {name}",
        f"{name} is my favorite person to talk to!",
        f"{name} keeps reminding me that people can be good :)",
        "You know just how to make my day!",
        "Your parents must be proud",
        "🥺🥰",
    ]
    return random.choice(praises)



def ope_count(message):
    # updates ope count in sheet
    sheet = client.open("Data").sheet1
    data = sheet.get_all_records()
    author_found = False
    author_count = 0
    new_index = 2
    for record in data:
        if message.author.id == record["id"]:
            author_found = True
            sheet.update_cell(record["index"] + 1, 2, record["number"] + 1)
            author_count = record["number"] + 1
        new_index += 1
    if not author_found:
        new_row = [str(message.author.id), 1, new_index - 1]
        sheet.insert_row(new_row, new_index)
        author_count = 1

    return author_count


@bot.event
async def on_message(message):
    if not message.author.bot:
        if re.search(r"\bope\b", message.content.lower()):
            print(message.author)
            count = ope_count(message)
            await message.channel.send(f"{message.author.display_name} has said " f"Ope {count} times. Yikes.")
        # handle chloe 0pe
        elif message.author.id == 495663643485143061 and re.search(r"\b0pe\b", message.content.lower()):
            await message.channel.send("lmao chloe. yIKeS.")
        # hbd syd
        if message.author.id == 608144332016451626 and random.randint(0, 8) == 3:
            await message.add_reaction("<:hug:701681347973873725>")
        # 2201 meme
        if re.search(r"\broth|2201\b", message.content.lower()) and random.randint(0, 5) == 3:
            think_str = (" " * random.randint(0, 5)).join(["T", "H", "I", "N", "K", "!"])
            await message.channel.send(f"Daddy Roth says: don't forget to {think_str}")
        if message.channel.id in target_channel_id and re.search(r"\bbot\b", message.content.lower()):
            result = classifier(message.content.lower())[0]
            #add in confidence count for positive and negative comments 
            if result["label"] == "NEGATIVE" and result["score"] >= 0.75 and message.content.lower().strip() != "bot":
                real_message = get_insult(message.author.display_name)
                await message.reply(real_message)
            elif result["label"] == "POSITIVE" and result["score"] >= 0.75:
                real_message = get_praise(message.author.display_name)
                await message.reply(real_message)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(name="the clock.", type=3),
    )
    print(f"{bot.user.name} is running...")


def time_to_sleep():
    now = datetime.utcnow()
    # 10am UTC is 5am Vandy time
    remaining_seconds = (
        timedelta(hours=24) - (now - now.replace(hour=10, minute=0, second=0, microsecond=0))
    ).total_seconds() % (24 * 3600)
    remaining = round(remaining_seconds)
    return remaining


@tasks.loop(minutes=30)
async def daily_purge():
    global purged
    for i in range(len(purged)):
        if purged[i] == 1:
            continue
        purge_channel = bot.get_channel(target_channel_id[i])
        messages = await purge_channel.history(limit=1).flatten()
        last_message_time = messages[0].created_at

        diff = datetime.utcnow() - last_message_time
        print(diff)

        if diff > timedelta(minutes=30):
            await purge_channel.send(f"Messages about to be purged in `10` seconds in channel {purge_channel.mention}")
            print("About to yeet.")
            await asyncio.sleep(10)
            deleted = await purge_channel.purge(limit=None)
            await purge_channel.send(f"Yeeted {len(deleted)} messages.")

            remaining = time_to_sleep()
            await purge_channel.send(f"Going to sleep for {remaining} seconds.")
            
            # send bulgaria pic in '25 discord post purge
            if purge_channel.id == 868546595279470632:
                await purge_channel.send("https://media.discordapp.net/attachments/663328401293049918/869671790149005312/unknown-78.png")
                
            purged[i] = 1  # set purge flag for specific channel
        else:
            print("Purge snoozed for 30 minutes")

    if sum(purged) == len(purged):  # all purged
        purged = [0 for _ in range(len(purged))]  # reset
        remaining = time_to_sleep()
        print(f"Going to sleep for {remaining} seconds.")
        await asyncio.sleep(remaining)


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


@bot.command()
async def github(ctx):
    await ctx.send("Catch! https://github.com/aadibajpai/VandyPurger")


@bot.command(name="yeet")
async def yeet(ctx, amount=30):
    """
    purge wellness by <amount> messages, default 30
    """
    if ctx.message.channel.id not in target_channel_id:
        await ctx.send("Sorry, this works only in specified channels.")
        return None

    print(f"yeet vote by {ctx.message.author}")
    vote = await take_vote(ctx, f"Purge {amount} messages?", 300, 3)  # 5 minutes, min 3 votes

    if vote:
        deleted = await ctx.channel.purge(limit=amount, before=ctx.message)
        await ctx.message.delete()
        await ctx.send(f"Yeeted {len(deleted)} messages <:hug:701681347973873725>")
        print(f"vote passed, yeeted {amount} messages")


bot.run(os.environ["DISCORD_TOKEN"])
