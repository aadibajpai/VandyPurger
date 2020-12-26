import asyncio
import discord


# edited https://github.com/turtlebasket/comrade-bot/blob/master/bot_utils.py#L6
async def take_vote(ctx, question: str, vote_time, min_voters):
    """
    take_vote(ctx, question:str) - Collects votes
    ctx: pass from command function
    question: what to ask
    returns [<all who want>, <all who don't want>].
    It's up to the context/use case to decide how these should be used.
    """

    thumbs_up = "👍"
    embed_title = "NEW VOTE"
    vote = await ctx.send(
        embed=discord.Embed(
            type="rich",
            title=embed_title,
            description=f"{question}\n\n Minimum {min_voters} votes required."
        )
    )

    await vote.add_reaction(thumbs_up)

    passed = False
    curr_time = 0
    while curr_time < vote_time:
        await asyncio.sleep(5)
        all_in_favor = 0
        finished = await vote.channel.fetch_message(vote.id)
        for reaction in finished.reactions:
            if str(reaction.emoji) == thumbs_up:
                all_in_favor += reaction.count-1  # don't include bot's reaction

        if all_in_favor >= min_voters:
            passed = True
            break

        await asyncio.sleep(5)
        curr_time += 5

    question += "\n**ok vote passed!**" if passed else "\n**rip vote failed. Sad!**"

    await vote.edit(embed=discord.Embed(
        type="rich",
        title=embed_title,
        description=question
    ))

    return passed
