import configparser

import discord
import apraw
from banhammer import banhammer, subreddit
from discord.ext import commands

from config import config as bh_config

bot = commands.Bot(bh_config["command_prefix"], description="The Banhacker bot built for Discord's Hack-Week based on the Banhammer framework.")
bh = banhammer.Banhammer(apraw.Reddit("TBHB"), bot=bot, change_presence=bh_config["change_presence"], loop_time=2.5*60)

for sub in bh_config["subreddits"]:
    bh.add_subreddits(subreddit.Subreddit(bh, sub))


@bot.event
async def on_command_error(ctx, error):
    print(error)


@bot.event
async def on_ready():
    print(str(bot.user) + ' is running.')
    bh.run()


@bot.command()
async def subreddits(ctx):
    await ctx.send(embed=bh.get_subreddits_embed())


@bot.command()
async def reactions(ctx):
    await ctx.send(embed=bh.get_reactions_embed())


@bh.new()
@bh.comments()
async def handle_new(p):
    msg = await bot.get_channel(bh_config["new_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.mail()
async def handle_mail(p):
    msg = await bot.get_channel(bh_config["mail_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.queue()
async def handle_queue(p):
    msg = await bot.get_channel(bh_config["queue_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.reports()
async def handle_reports(p):
    msg = await bot.get_channel(bh_config["reports_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.mod_actions("Anti-Evil Operations")
async def handle_actions(p):
    msg = await bot.get_channel(bh_config["actions_channel"]).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bot.event
async def on_message(m):
    if m.author.bot:
        return

    if m.channel.category is not None and m.channel.category.id == bh_config["banhammer_category"]:
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

    result = item.get_reaction(e).handle(user=u.nick)
    channel = bot.get_channel(bh_config["approved_channel"] if result.approved else bh_config["removed_channel"])
    await channel.send(result)


config = configparser.ConfigParser()
config.read("discord.ini")
bot.run(config["BH"]["token"])
