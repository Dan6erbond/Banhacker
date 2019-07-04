import prawcore

from . import exceptions
from . import reaction
from .item import *


class Subreddit:

    def __init__(self, bh, dict={}, subreddit="", stream_new=True, stream_comments=False, stream_reports=True,
                 stream_mail=True, stream_queue=True, stream_mod_actions=True, custom_emotes=True):
        self.banhammer = bh
        self.reddit = bh.reddit

        self.subreddit = dict["subreddit"] if "subreddit" in dict else subreddit
        if type(self.subreddit) != praw.models.Subreddit: self.subreddit = self.reddit.subreddit(str(self.subreddit))
        if self.reddit.user.me() not in self.subreddit.moderator(): raise exceptions.NotModerator(self.reddit.user.me(),
                                                                                                  self)

        self.name = self.subreddit.display_name.replace("r/", "").replace("/", "")

        self.stream_new = dict["stream_new"] if "stream_new" in dict else stream_new
        self.stream_comments = dict["stream_comments"] if "stream_comments" in dict else stream_comments
        self.stream_reports = dict["stream_reports"] if "stream_reports" in dict else stream_reports
        self.stream_mail = dict["stream_mail"] if "stream_mail" in dict else stream_mail
        self.stream_queue = dict["stream_queue"] if "stream_queue" in dict else stream_queue
        self.stream_mod_actions = dict["stream_mod_actions"] if "stream_mod_actions" in dict else stream_mod_actions

        self.custom_emotes = dict["custom_emotes"] if "custom_emotes" in dict else custom_emotes
        self.reactions = list()
        self.load_reactions()

    def __str__(self):
        return str(self.subreddit)

    def get_status(self):
        str = "/r/" + self.name

        if self.stream_new: str += " | New Posts"
        if self.stream_comments: str += " | Comments"
        if self.stream_reports: str += " | Reports"
        if self.stream_mail: str += " | Mod-Mail"
        if self.stream_queue: str += " | Mod-Queue"

        return str

    def setup(self):
        if self.subreddit.quarantine:
            self.subreddit.quaran.opt_in()

        settings = self.subreddit.mod.settings()
        self.stream_new = False if settings["spam_links"] == "all" or settings["spam_selfposts"] == "all" else True
        self.stream_comments = True if settings["spam_comments"] == "all" else False
        self.stream_queue = True if settings["spam_links"] == "all" or settings["spam_selfposts"] == "all" else False

    def get_dict(self):
        dict = {
            "subreddit": self.name,
            "stream_new": self.stream_new,
            "stream_comments": self.stream_comments,
            "stream_reports": self.stream_reports,
            "stream_mail": self.stream_mail,
            "stream_queue": self.stream_queue,
            "stream_mod_actions": self.stream_mod_actions,
            "custom_emotes": self.custom_emotes
        }

        return dict

    def get_data(self):
        dict = self.get_dict()
        dict["get_new"] = self.get_new
        dict["get_comments"] = self.get_comments
        dict["get_reports"] = self.get_reports
        dict["get_mail"] = self.get_mail
        dict["get_queue"] = self.get_queue
        dict["get_mod_actions"] = self.get_mod_actions
        return dict

    def load_reactions(self):
        if self.custom_emotes:
            try:
                reaction_page = self.subreddit.wiki['banhammer-reactions']
                reacts = reaction.get_reactions(reaction_page.content_md)["reactions"]
                if len(reacts) > 0: self.reactions = reacts
            except prawcore.exceptions.NotFound:
                pass
            except Exception as e:
                print(type(e), e)

        if not len(self.reactions) > 0:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(dir_path + "/reactions.yaml", encoding="utf8") as f:
                content = f.read()
                self.reactions = reaction.get_reactions(content)["reactions"]
                try:
                    self.subreddit.wiki.create("banhammer-reactions", content, reason="Reactions not found")
                except Exception as e:
                    print(e)

    def get_reactions(self, item):
        _r = list()
        for reaction in self.reactions:
            if reaction.eligible(item):
                _r.append(reaction)
        return _r

    def get_reaction(self, emoji, item):
        for reaction in self.get_reactions(item):
            if reaction.emoji == emoji:
                return reaction

    def get_new(self):
        if not self.stream_new:
            return list()
        path = "files/{}_new.txt".format(self.subreddit.id)
        ids = list()
        if os.path.exists(path):
            with open(path) as f:
                ids = f.read().splitlines()
        for submission in self.subreddit.new():
            if submission.id in ids:
                break
            item = RedditItem(submission, self, "new")
            item.save(path)
            yield item

    def get_comments(self):
        if not self.stream_comments:
            return list()
        path = "files/{}_comments.txt".format(self.subreddit.id)
        ids = list()
        if os.path.exists(path):
            with open(path) as f:
                ids = f.read().splitlines()
        for comment in self.subreddit.comments(limit=250):
            if submission.id in ids:
                break
            item = RedditItem(comment, self, "new")
            item.save(path)
            yield item

    def get_reports(self):
        if not self.stream_reports:
            return list()
        path = "files/{}_reports.txt".format(self.subreddit.id)
        ids = list()
        if os.path.exists(path):
            with open(path) as f:
                ids = f.read().splitlines()
        for item in self.subreddit.mod.reports():
            if item.id in ids:
                break
            item = RedditItem(item, self, "reports")
            item.save(path)
            yield item

    def get_mail(self):
        if not self.stream_mail:
            return list()
        path = "files/{}_mail.txt".format(self.subreddit.id)
        ids = list()
        if os.path.exists(path):
            with open(path) as f:
                ids = f.read().splitlines()
        for conversation in self.subreddit.modmail.conversations():
            for message in conversation.messages:
                if message.id in ids:
                    break
                message.conversation = conversation
                item = RedditItem(message, self, "modmail")
                item.save(path)
                yield item

    def get_queue(self):
        if not self.stream_queue:
            return list()
        path = "files/{}_queue.txt".format(self.subreddit.id)
        ids = list()
        if os.path.exists(path):
            with open(path) as f:
                ids = f.read().splitlines()
        for item in self.subreddit.mod.modqueue():
            if item.id in ids:
                break
            item = RedditItem(item, self, "queue")
            item.save(path)
            yield item

    def get_mod_actions(self, mods):
        mods = [m.lower() for m in mods]
        if not self.stream_mod_actions:
            return list()
        path = "files/{}_actions.txt".format(self.subreddit.id)
        ids = list()
        if os.path.exists(path):
            with open(path) as f:
                ids = f.read().splitlines()
        for action in self.subreddit.mod.log(limit=None):
            if action.id in ids:
                break
            if str(action.mod).lower() in mods or len(mods) == 0:
                item = RedditItem(action, self, "log")
                item.save(path)
                yield item
