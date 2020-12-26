import asyncio
import discord


# edited https://github.com/turtlebasket/comrade-bot/blob/master/bot_utils.py#L6
async def take_vote(ctx, question: str, vote_time: int, min_voters: int):
    """
    take_vote(ctx, question:str) - Collects votes
    ctx: pass from command function
    question: what to ask
    returns vote passed or not.
    It's up to the context/use case to decide how these should be used.
    """

    thumbs_up = "👍"
    vote = await ctx.send(
        embed=discord.Embed(
            type="rich",
            title=question,
            description=f"Minimum {min_voters + 1} votes required.",  # +1 bc one self vote
            color=16761095,  # gold
        )
    )

    await vote.add_reaction(thumbs_up)

    passed = False
    curr_time = 0
    while curr_time < vote_time:
        all_in_favor = 0
        finished = await vote.channel.fetch_message(vote.id)
        for reaction in finished.reactions:
            if str(reaction.emoji) == thumbs_up:
                all_in_favor += reaction.count - 1  # don't include bot's reaction

        if all_in_favor >= min_voters:
            passed = True
            break

        await asyncio.sleep(5)
        curr_time += 5

    result = "\n**ok vote passed**" if passed else "\n**rip vote failed. Sad!**"

    await vote.edit(
        embed=discord.Embed(
            type="rich", title=question, description=result, color=3066993 if passed else 15158332  # green or red
        )
    )

    return passed
