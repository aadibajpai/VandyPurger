import discord
import asyncio
import os

from datetime import datetime, timedelta
from discord.ext import tasks


class VandyBot(discord.Client):
    target_channels = [722609125950750771]
    last_message = {}
    last_purged = {}

    async def on_ready(self):
        self.purge_channels.start()

    async def on_message(self, message):
        if message.channel.id in self.target_channels:
            self.last_message[message.channel.id] = message.created_at

    @tasks.loop(minutes=5)
    async def purge_channels(self):
        for channel in self.target_channels:
            if channel not in self.last_message or datetime.utcnow() - self.last_message[
                channel
            ] > timedelta(
                minutes=30
            ):
                print("purging channel")
                await self.get_channel(channel).purge()
                self.last_purged[channel] = datetime.utcnow()


vandy = VandyBot()
vandy.run(os.environ["DISCORD_TOKEN"])
