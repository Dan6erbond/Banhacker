import configparser
from datetime import datetime

import apraw
import banhammer
import discord
from banhammer import Banhammer
from banhammer.models import EventHandler, ItemAttribute, RedditItem, Subreddit
from discord.ext import commands
from discord.ext.commands import Bot

from config import config as bh_config

reddit = apraw.Reddit("TBHB")


class Banhacker(Bot, Banhammer):

    def __init__(self, **options):
        super().__init__(
            bh_config["command_prefix"],
            description="The Banhacker bot built for Discord's Hack-Week based on the Banhammer framework.",
            **options)
        Banhammer.__init__(self, reddit, bot=self, change_presence=bh_config["change_presence"])

    @property
    def embed(self):
        embed = discord.Embed(colour=self.embed_color)
        embed.set_footer(text=self.user.name, icon_url=self.user.avatar_url)
        embed.timestamp = datetime.now()
        return embed

    async def on_command_error(self, ctx: commands.Context, error):
        print(error)

    async def on_ready(self):
        print(str(self.user) + ' is running.')

        for sub in bh_config["subreddits"]:
            s = Subreddit(self, **sub)
            await s.load_reactions()
            await self.add_subreddits(s)

        Banhammer.start(self)

    @commands.command()
    async def subreddits(self, ctx: commands.Context):
        await ctx.send(embed=self.get_subreddits_embed(embed_template=self.embed))

    @commands.command()
    async def reactions(self, ctx: commands.Context, subreddit: str = ""):
        if subreddit:
            for sub in self.subreddits:
                if str(sub).lower() == subreddit.lower():
                    await ctx.send(embed=await sub.get_reactions_embed(embed_template=self.embed))
        else:
            await ctx.send(embed=self.get_reactions_embed(embed_template=self.embed))

    async def on_message(self, m: discord.Message):
        if m.author.bot:
            return

        if m.channel.category is not None and m.channel.category.id == bh_config["banhammer_category"]:
            item = await self.get_item(m.content)
            if item is not None:
                for react in item.get_reactions():
                    try:
                        await m.add_reaction(react.emoji)
                    except Exception as e:
                        print(e)

        await self.process_commands(m)

    async def on_raw_reaction_add(self, p: discord.RawReactionActionEvent):
        c = self.get_channel(p.channel_id)

        u = c.guild.get_member(p.user_id)
        if u.bot:
            return

        m = await c.fetch_message(p.message_id)
        e = p.emoji.name if not p.emoji.is_custom_emoji() else "<:{}:{}>".format(p.emoji.name, p.emoji.id)

        item = await self.get_item(m.content) if not m.embeds else await self.get_item(m.embeds[0])
        if not item:
            return

        result = await item.get_reaction(e).handle(item, user=u.nick)
        channel = self.get_channel(bh_config["approved_channel"] if result.approved else bh_config["removed_channel"])
        await channel.send(embed=await result.get_embed(embed_template=self.embed))

        await m.delete()

    @EventHandler.new()
    @EventHandler.comments()
    async def handle_new(self, p: RedditItem):
        msg = await self.get_channel(bh_config["new_channel"]).send(embed=await p.get_embed(embed_template=self.embed))
        await p.add_reactions(msg)

    @EventHandler.mail()
    async def handle_mail(self, p: RedditItem):
        msg = await self.get_channel(bh_config["mail_channel"]).send(embed=await p.get_embed(embed_template=self.embed))
        await p.add_reactions(msg)

    @EventHandler.queue()
    async def handle_queue(self, p: RedditItem):
        msg = await self.get_channel(bh_config["queue_channel"]).send(embed=await p.get_embed(embed_template=self.embed))
        await p.add_reactions(msg)

    @EventHandler.reports()
    async def handle_reports(self, p: RedditItem):
        msg = await self.get_channel(bh_config["reports_channel"]).send(embed=await p.get_embed(embed_template=self.embed))
        await p.add_reactions(msg)

    @EventHandler.mod_actions()
    @EventHandler.filter(ItemAttribute.MOD, "Anti-Evil Operations", "Dan6erbond")
    async def handle_actions(self, p: RedditItem):
        msg = await self.get_channel(bh_config["actions_channel"]).send(embed=await p.get_embed(embed_template=self.embed))
        await p.add_reactions(msg)


if __name__ == "__main__":
    bot = Banhacker()
    config = configparser.ConfigParser()
    config.read("discord.ini")
    bot.run(config["BH"]["token"])
