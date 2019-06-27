import configparser

import praw
from discord.ext import commands

from banhammer import banhammer
from banhammer import subreddit

# new-posts: 593765461540339712
# approved-posts: 593765550153400320
# removed-posts: 593765576325857282
# mod-mail: 593765594969669633
# report-queue: 593765660061073440
# mod-queue: 593765690167525397
# mod-actions: 593818334357618705

bot = commands.Bot("!", description="The Banhacker bot built for Discord's Hack-Week based on the Banhammer framework.")
bh = banhammer.Banhammer(praw.Reddit("TBHB"))

bh.add_subreddits(subreddit.Subreddit(bh, subreddit="banhammerdemo"))


@bot.event
async def on_command_error(ctx, error):
    print(error)


@bot.event
async def on_ready():
    print(str(bot.user) + ' is running.')
    bh.run()


@bh.new()
@bh.comments()
async def handle_new(p):
    msg = await bot.get_channel(593765461540339712).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.mail()
async def handle_mail(p):
    msg = await bot.get_channel(593765594969669633).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.queue()
async def handle_queue(p):
    msg = await bot.get_channel(593765690167525397).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.reports()
async def handle_reports(p):
    msg = await bot.get_channel(593765660061073440).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bh.mod_actions()
async def handle_actions(p):
    msg = await bot.get_channel(593818334357618705).send(embed=p.get_embed())
    for react in p.get_reactions():
        try:
            await msg.add_reaction(react.emoji)
        except:
            continue


@bot.event
async def on_message(m):
    if m.author.bot:
        return

    if m.channel.category.id == 593765403554086946:
        item = bh.get_item(m.content)
        if item is not None:
            for react in item.get_reactions():
                try:
                    await msg.add_reaction(react.emoji)
                except:
                    continue

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
    channel = bot.get_channel(593765550153400320 if result["approved"] else 593765576325857282)
    await channel.send(result["message"])


config = configparser.ConfigParser()
config.read("discord.ini")
bot.run(config["BH"]["token"])
