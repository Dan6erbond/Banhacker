import os

import praw

from . import yaml


class Reaction:

    def __init__(self, reddit, dict={}, emoji="", type="", flair="", approve=False, mark_nsfw=False, lock=False,
                 reply="", ban=None, min_votes=1):
        self.reddit = reddit

        self.emoji = dict["emoji"] if "emoji" in dict else emoji
        self.emoji = self.emoji.strip()

        self.type = dict["type"] if "type" in dict else type
        self.flair = dict["flair"] if "flair" in dict else flair
        self.approve = dict["approve"] if "approve" in dict else approve
        self.mark_nsfw = dict["mark_nsfw"] if "mark_nsfw" in dict else mark_nsfw
        self.lock = dict["lock"] if "lock" in dict else lock
        self.reply = dict["reply"] if "reply" in dict else reply
        self.ban = dict["ban"] if "ban" in dict else ban
        self.min_votes = dict["min_votes"] if "min_votes" in dict else min_votes

        self.item = None

    def get_dict(self):
        dict = {
            "emoji": self.emoji,
            "type": self.type,
            "flair": self.flair,
            "approve": self.approve,
            "mark_nsfw": self.mark_nsfw,
            "lock": self.lock,
            "reply": self.reply,
            "ban": self.ban,
            "min_votes": self.min_votes
        }

        return dict

    def handle(self, user, item=None):
        if item is None and self.item is not None:
            item = self.item
        else:
            return None  # Exception

        if isinstance(item.item, praw.models.Submission) and not (self.type == "submission" or self.type == ""):
            return None  # Exception
        if isinstance(item.item, praw.models.Comment) and not (self.type == "comment" or self.type == ""):
            return None  # Exception
        if isinstance(item.item, praw.models.ModmailConversation) and self.type != "mail":
            return None  # Exception

        item_type = item.type.title()
        actions = list()

        try:
            test = item.item.id
        except:  # item was removed
            if isinstance(item.item, praw.models.Submission) or isinstance(item.item, praw.models.Comment):
                item.item.mod.remove()
                actions.append("removed")
                if isinstance(item.item, praw.models.Submission):
                    item.item.mod.lock()
                    actions.append("locked")

                action_string = " and ".join(actions)
                return_string = "**{} {} by {}!**\n\n" \
                                "{} by {}:\n\n".format(item_type, action_string, "Banhammer", item_type, "[deleted]")
                return {
                    "type": self.type,
                    "approved": False,
                    "message": return_string
                }

        if isinstance(item.item, praw.models.Submission) or isinstance(item.item, praw.models.Comment):
            if item.item.author is None:
                item.item.mod.remove()
                actions.append("removed")
                if isinstance(item.item, praw.models.Submission):
                    item.item.mod.lock()
                    actions.append("locked")

                action_string = " and ".join(actions)
                return_string = "**{} {} by {}!**\n\n" \
                                "{} by {}:\n\n" \
                                "{}".format(item_type, action_string, "Banhammer", item_type, "[deleted]",
                                            item.get_url())
                return {
                    "type": self.type,
                    "approved": False,
                    "message": return_string
                }

        if self.approve:
            item.item.mod.approve()
            actions.append("approved")
        else:
            item.item.mod.remove()
            actions.append("removed")

        if isinstance(item.item, praw.models.Submission):
            if self.flair != "":
                item.item.mod.flair(text=self.flair)
                actions.append("flaired")

            if self.mark_nsfw:
                item.item.mod.nsfw()
                actions.append("marked NSFW")

            if self.lock or not self.approve:
                item.item.mod.lock()
                actions.append("locked")
            else:
                item.item.mod.unlock()

        if self.reply != "":
            reply = item.item.reply(self.reply)
            reply.mod.distinguish(sticky=True)
            actions.append("replied to")

        if isinstance(self.ban, int):
            if self.ban == 0:
                item.item.subreddit.banned.add(item.item.author.name, ban_reason="Breaking Rules",
                                               ban_message=formatter.format_ban_message(item.item, self.ban),
                                               note="Bot Ban")
                actions.append("/u/" + item.item.author.name + " permanently banned")
            else:
                item.item.subreddit.banned.add(item.item.author.name, ban_reason="Breaking Rules", duration=self.ban,
                                               ban_message=formatter.format_ban_message(item.item, self.ban),
                                               note="Bot Ban")
                actions.append("/u/" + item.item.author.name + " banned for {} day(s)".format(self.ban))

        actions_string = " and ".join(actions)

        return_string = "**{} {} by {}!**\n\n" \
                        "{} by /u/{}:\n\n" \
                        "{}".format(item_type, actions_string, user, item_type, item.item.author.name, item.get_url())

        reports = "files/{}_reports.txt".format(item.subreddit.subreddit.id)
        if os.path.exists(reports): item.remove(reports)
        queue = "files/{}_queue.txt".format(item.subreddit.subreddit.id)
        if os.path.exists(queue): item.remove(queue)

        return {
            "type": self.type,
            "approved": self.approve,
            "message": return_string
        }

    def eligible(self, item):
        if isinstance(item, praw.models.Submission):
            if self.type == "" or self.type == "submission":
                return True
        elif isinstance(item, praw.models.Comment):
            if self.type == "" or self.type == "comment":
                return True
        elif isinstance(item, praw.models.ModmailMessage):
            if self.type == "mail":
                return True
        return False


def get_reactions(reddit, yml):
    result = yaml.get_list(yml)
    ignore = list()
    emojis = set()
    for item in result:
        if "ignore" in item:
            ignore = [i.strip() for i in item["ignore"].split(",")]
            result.remove(item)
            break
    reactions = result
    reactions = [Reaction(reddit, r) for r in result if "emoji" in r]
    return {
        "ignore": ignore,
        "reactions": reactions
    }


def ignore_reactions(reactions, remove):
    emojis = set()

    for item in remove:
        if isinstance(item, Reaction):
            emojis.add(item.emoji)
        elif isinstance(item, str):
            emojis.add(item)

    for react in reactions:
        if react.emoji in emojis:
            reactions.remove(react)

    return reactions
