import configparser
from datetime import datetime

import apraw
import banhammer
import discord
from banhammer.models import RedditItem, Subreddit
from discord.ext import commands

from config import config as bh_config

bot = commands.Bot(
    bh_config["command_prefix"],
    description="The Banhacker bot built for Discord's Hack-Week based on the Banhammer framework.")

bh = banhammer.Banhammer(apraw.Reddit("TBHB"), bot=bot, change_presence=bh_config["change_presence"])


def get_embed():
    embed = discord.Embed(colour=bh.embed_color)
    embed.set_footer(text=bot.user.name, icon_url=bot.user.avatar_url)
    embed.timestamp = datetime.now()
    return embed


@bot.event
async def on_command_error(ctx, error):
    print(error)


@bot.event
async def on_ready():
    print(str(bot.user) + ' is running.')

    for sub in bh_config["subreddits"]:
        s = Subreddit(bh, **sub)
        await s.load_reactions()
        await bh.add_subreddits(s)

    bh.run()


@bot.command()
async def subreddits(ctx):
    await ctx.send(embed=bh.get_subreddits_embed(embed_template=get_embed()))


@bot.command()
async def reactions(ctx, subreddit: str = ""):
    if subreddit:
        for sub in bh.subreddits:
            if str(sub).lower() == subreddit.lower():
                await ctx.send(embed=await sub.get_reactions_embed(embed_template=get_embed()))
    else:
        await ctx.send(embed=bh.get_reactions_embed(embed_template=get_embed()))


@bh.new()
@bh.comments(subreddit="banhammerdemo")
async def handle_new(p: RedditItem):
    msg = await bot.get_channel(bh_config["new_channel"]).send(embed=await p.get_embed(embed_template=get_embed()))
    await p.add_reactions(msg)


@bh.mail()
async def handle_mail(p: RedditItem):
    msg = await bot.get_channel(bh_config["mail_channel"]).send(embed=await p.get_embed(embed_template=get_embed()))
    await p.add_reactions(msg)


@bh.queue()
async def handle_queue(p: RedditItem):
    msg = await bot.get_channel(bh_config["queue_channel"]).send(embed=await p.get_embed(embed_template=get_embed()))
    await p.add_reactions(msg)


@bh.reports()
async def handle_reports(p: RedditItem):
    msg = await bot.get_channel(bh_config["reports_channel"]).send(embed=await p.get_embed(embed_template=get_embed()))
    await p.add_reactions(msg)


@bh.mod_actions("Anti-Evil Operations")
async def handle_actions(p: RedditItem):
    msg = await bot.get_channel(bh_config["actions_channel"]).send(embed=await p.get_embed(embed_template=get_embed()))
    await p.add_reactions(msg)


@bot.event
async def on_message(m):
    if m.author.bot:
        return

    if m.channel.category is not None and m.channel.category.id == bh_config["banhammer_category"]:
        item = await bh.get_item(m.content)
        if item is not None:
            for react in item.get_reactions():
                try:
                    await m.add_reaction(react.emoji)
                except Exception as e:
                    print(e)

    await bot.process_commands(m)


@bot.event
async def on_raw_reaction_add(p):
    c = bot.get_channel(p.channel_id)

    u = c.guild.get_member(p.user_id)
    if u.bot:
        return

    m = await c.fetch_message(p.message_id)
    e = p.emoji.name if not p.emoji.is_custom_emoji() else "<:{}:{}>".format(p.emoji.name, p.emoji.id)

    item = await bh.get_item(m.content) if not m.embeds else await bh.get_item(m.embeds[0])
    if not item:
        return

    result = await item.get_reaction(e).handle(item, user=u.nick)
    channel = bot.get_channel(bh_config["approved_channel"] if result.approved else bh_config["removed_channel"])
    await channel.send(embed=await result.get_embed(embed_template=get_embed()))

    await m.delete()


config = configparser.ConfigParser()
config.read("discord.ini")
bot.run(config["BH"]["token"])
