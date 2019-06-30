import configparser

import discord
import praw
from discord.ext import commands

from banhammer import banhammer
from banhammer import subreddit
from config import config

bot = commands.Bot(config["command_prefix"], description="The Banhacker bot built for Discord's Hack-Week based on the Banhammer framework.")
bh = banhammer.Banhammer(praw.Reddit("TBHB"), bot=bot, change_presence=config["change_presence"])

for sub in config["subreddits"]:
    bh.add_subreddits(subreddit.Subreddit(bh, sub))


@bot.event
async def on_command_error(ctx, error):
    print(error)


@bot.event
async def on_ready():
    print(str(bot.user) + ' is running.')
    bh.run()


@bot.command()
async def status(ctx):
    embed = discord.Embed(
        colour=bh.embed_color
    )
    embed.title = "Subreddits' statuses"
    embed.description = "\n".join([s.get_status() for s in bh.subreddits])
    await ctx.send(embed=embed)


@bot.command()
async def reactions(ctx):
    embed = discord.Embed(
        colour=bh.embed_color
    )
    embed.title = "Configured reactions"
    for sub in bh.subreddits: embed.add_field(name="/r/" + str(sub), value="\n".join([str(r) for r in sub.reactions]), inline=False)
    await ctx.send(embed=embed)


@bh.new()
@bh.comments()
async def handle_new(p):
    msg = await bot.get_channel(config["new_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.mail()
async def handle_mail(p):
    msg = await bot.get_channel(config["mail_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.queue()
async def handle_queue(p):
    msg = await bot.get_channel(config["queue_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.reports()
async def handle_reports(p):
    msg = await bot.get_channel(config["reports_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.mod_actions("Anti-Evil Operations")
async def handle_actions(p):
    msg = await bot.get_channel(config["actions_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bot.event
async def on_message(m):
    if m.author.bot:
        return

    if m.channel.category is not None and m.channel.category.id == config["banhammer_category"]:
        item = bh.get_item(m.content)
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

    item = bh.get_item(m.content) if len(m.embeds) == 0 else bh.get_item(m.embeds[0])
    if item is None:
        return

    await m.delete()

    result = item.get_reaction(e).handle(u.nick)
    channel = bot.get_channel(config["approved_channel"] if result["approved"] else config["removed_channel"])
    await channel.send(result["message"])


config = configparser.ConfigParser()
config.read("discord.ini")
bot.run(config["BH"]["token"])
