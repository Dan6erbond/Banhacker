import asyncio
import json
import os

import inspect
import discord

from . import reddithelper
from .subreddit import Subreddit

banhammer_purple = discord.Colour(0).from_rgb(207, 206, 255)


class Banhammer:

    def __init__(self, reddit, loop_time=5 * 60, bot=None, embed_color=banhammer_purple, change_presence=False):
        self.reddit = reddit
        self.subreddits = list()
        self.loop = asyncio.get_event_loop()

        self.item_funcs = list()
        self.action_funcs = list()

        self.loop_time = loop_time
        self.bot = bot
        self.embed_color = embed_color
        self.change_presence = change_presence

        if not os.path.exists("files"):
            os.mkdir("files")

    def add_subreddits(self, *subs):
        for sub in subs:
            if type(sub) != Subreddit:
                sub = Subreddit(self, subreddit=str(sub))
                sub.setup()
            self.subreddits.append(sub)

    def remove_subreddit(self, subreddit):
        for sub in self.subreddits:
            if str(sub).lower() == subreddit.lower():
                self.subreddits.remove(sub)
                return True
        return False

    def new(self, **kwargs):
        def assign(func):
            self.add_new_func(func, **kwargs)
            return func

        return assign

    def add_new_func(self, func, **kwargs):
        self.add_items_func(func, "get_new", **kwargs)

    def comments(self, **kwargs):
        def assign(func):
            self.add_comments_func(func, **kwargs)
            return func

        return assign

    def add_comments_func(self, func, **kwargs):
        self.add_items_func(func, "get_comments", **kwargs)

    def mail(self, **kwargs):
        def assign(func):
            self.add_mail_func(func, **kwargs)
            return func

        return assign

    def add_mail_func(self, func, **kwargs):
        self.add_items_func(func, "get_mail", **kwargs)

    def queue(self, **kwargs):
        def assign(func):
            self.add_queue_func(func, **kwargs)
            return func

        return assign

    def add_queue_func(self, func, **kwargs):
        self.add_items_func(func, "get_queue", **kwargs)

    def reports(self, **kwargs):
        def assign(func):
            self.add_report_func(func, **kwargs)
            return func

        return assign

    def add_report_func(self, func, **kwargs):
        self.add_items_func(func, "get_reports", **kwargs)

    def add_items_func(self, func, sub_func, **kwargs):
        if inspect.iscoroutinefunction(func):
            self.item_funcs.append({
                "func": func,
                "sub": kwargs["subreddit"] if "subreddit" in kwargs else None,
                "sub_func": sub_func
            })

    async def send_items(self):
        while True:
            for func in self.item_funcs:
                subs = list()
                if func["sub"] is not None:
                    for sub in self.subreddits:
                        if str(sub.subreddit).lower() == func["sub"].lower():
                            subs.append(sub)
                            break
                else:
                    subs.extend(self.subreddits)
                for sub in subs:
                    if self.bot is not None and self.change_presence:
                        await self.bot.change_presence(activity=discord.Game("on /r/{}".format(sub)))
                    for post in sub.get_data()[func["sub_func"]]():
                        await func["func"](post)
                    if self.bot is not None and self.change_presence:
                        await self.bot.change_presence(activity=None)

            await asyncio.sleep(self.loop_time)

    def mod_actions(self, *args, **kwargs):
        def assign(func):
            self.add_mod_actions_func(func, *args, **kwargs)
            return func

        return assign

    def add_mod_actions_func(self, func, *args, **kwargs):
        if inspect.iscoroutinefunction(func):
            self.action_funcs.append({
                "func": func,
                "mods": kwargs["mods"] if "mods" in kwargs else list(args),
                "sub": kwargs["subreddit"] if "subreddit" in kwargs else None
            })

    async def send_actions(self):
        while True:
            for func in self.action_funcs:
                subs = list()
                if func["sub"] is not None:
                    for sub in self.subreddits:
                        if str(sub.subreddit).lower() == func["sub"].lower():
                            subs.append(sub)
                            break
                else:
                    subs.extend(self.subreddits)
                for sub in subs:
                    if self.bot is not None and self.change_presence:
                        await self.bot.change_presence(activity=discord.Game("on /r/{}".format(sub)))
                    for action in sub.get_mod_actions(func["mods"]):
                        await func["func"](action)
                    if self.bot is not None and self.change_presence:
                        await self.bot.change_presence(activity=None)

            await asyncio.sleep(self.loop_time)

    def get_item(self, c):
        # Add this to use the embed's URL (if one is present):
        # else c.author.url if c.author != discord.Empty and c.author.url != discord.Embed.Empty
        s = str(c) if type(c) != discord.Embed else json.dumps(c.to_dict())
        return reddithelper.get_item(self.reddit, self.subreddits, s)

    def get_reactions_embed(self):
        embed = discord.Embed(
            colour=self.embed_color
        )
        embed.title = "Configured reactions"
        for sub in self.subreddits: embed.add_field(name="/r/" + str(sub),
                                                    value="\n".join([str(r) for r in sub.reactions]),
                                                    inline=False)
        return embed

    def get_subreddits_embed(self):
        embed = discord.Embed(
            colour=self.embed_color
        )
        embed.title = "Subreddits' statuses"
        embed.description = "\n".join([s.get_status() for s in self.subreddits])
        return embed

    def run(self):
        if len(self.item_funcs) > 0: self.loop.create_task(self.send_items())
        if len(self.action_funcs) > 0: self.loop.create_task(self.send_actions())
        # self.loop.run_forever()
