import asyncio
import json
import os

import discord

from .item import RedditItem
from . import reddithelper
from .subreddit import Subreddit


banhammer_purple = discord.Colour(0).from_rgb(207, 206, 255)

class Banhammer:

    def __init__(self, reddit, loop_time=5 * 60, embed_color=banhammer_purple):
        self.reddit = reddit
        self.subreddits = list()
        self.loop = asyncio.get_event_loop()

        self.item_funcs = list()
        self.action_funcs = list()

        self.loop_time = loop_time
        self.embed_color = embed_color

        if not os.path.exists("files"):
            os.mkdir("files")

    def add_subreddits(self, *subs):
        for sub in subs:
            if type(sub) != Subreddit:
                sub = Subreddit(self, subreddit=str(sub))
                sub.setup()
            self.subreddits.append(sub)

    def new(self, **kwargs):
        def assign(func):
            self.add_new_func(func, subreddit=kwargs["subreddit"] if "subreddit" in kwargs else None)
            return func

        return assign

    def add_new_func(self, func, **kwargs):
        self.item_funcs.append({
            "func": func,
            "sub": kwargs["subreddit"] if "subreddit" in kwargs else None,
            "sub_func": "get_new"
        })

    def comments(self, **kwargs):
        def assign(func):
            self.add_comments_func(func, subreddit=kwargs["subreddit"] if "subreddit" in kwargs else None)
            return func

        return assign

    def add_comments_func(self, func, **kwargs):
        self.item_funcs.append({
            "func": func,
            "sub": kwargs["subreddit"] if "subreddit" in kwargs else None,
            "sub_func": "get_comments"
        })

    def mail(self, **kwargs):
        def assign(func):
            self.add_mail_func(func, subreddit=kwargs["subreddit"] if "subreddit" in kwargs else None)
            return func

        return assign

    def add_mail_func(self, func, **kwargs):
        self.item_funcs.append({
            "func": func,
            "sub": kwargs["subreddit"] if "subreddit" in kwargs else None,
            "sub_func": "get_mail"
        })

    def queue(self, **kwargs):
        def assign(func):
            self.add_queue_func(func, subreddit=kwargs["subreddit"] if "subreddit" in kwargs else None)
            return func

        return assign

    def add_queue_func(self, func, **kwargs):
        self.item_funcs.append({
            "func": func,
            "sub": kwargs["subreddit"] if "subreddit" in kwargs else None,
            "sub_func": "get_queue"
        })

    def reports(self, **kwargs):
        def assign(func):
            self.add_report_func(func, subreddit=kwargs["subreddit"] if "subreddit" in kwargs else None)
            return func

        return assign

    def add_report_func(self, func, **kwargs):
        self.item_funcs.append({
            "func": func,
            "sub": kwargs["subreddit"] if "subreddit" in kwargs else None,
            "sub_func": "get_reports"
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
                    for post in sub.get_data()[func["sub_func"]]():
                        await func["func"](post)

            await asyncio.sleep(self.loop_time)

    def mod_actions(self, *args, **kwargs):
        def assign(func):
            self.add_mod_actions_func(func, mods=list(args),
                                      subreddit=kwargs["subreddit"] if "subreddit" in kwargs else None)
            return func

        return assign

    def add_mod_actions_func(self, func, *args, **kwargs):
        data = {
            "func": func,
            "mods": kwargs["mods"] if "mods" in kwargs else list(args),
            "sub": kwargs["subreddit"] if "subreddit" in kwargs else None
        }
        self.action_funcs.append(data)

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
                    for action in sub.get_mod_actions(func["mods"]):
                        await func["func"](action)

            await asyncio.sleep(self.loop_time)

    def get_item(self, c):
        # Add this to use the embed's URL (if one is present):
        # else c.author.url if c.author != discord.Empty and c.author.url != discord.Embed.Empty
        s = str(c) if type(c) != discord.Embed else json.dumps(c.to_dict())
        return reddithelper.get_item(self.reddit, self.subreddits, s)

    def run(self):
        if len(self.item_funcs) > 0: self.loop.create_task(self.send_items())
        if len(self.action_funcs) > 0: self.loop.create_task(self.send_actions())
        # self.loop.run_forever()
