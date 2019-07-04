import os

import praw


class RedditItem:

    def __init__(self, item, subreddit, source):
        self.item = item
        self.id = item.id
        self.type = "submission" if type(item) == praw.models.Submission else "comment" if type(
            item) == praw.models.Comment else "modmail" if type(item) == praw.models.ModmailMessage else "mod action"
        self.subreddit = subreddit
        self.source = source

    def __str__(self):
        return self.subreddit.banhammer.message_builder.get_item_message(self)

    def get_embed(self, embed_color=None):
        return self.subreddit.banhammer.message_builder.get_item_embed(self, embed_color)

    def save(self, path):
        with open(path, "a+") as f:
            f.write("\n" + self.item.id)

    def remove(self, path):
        if os.path.exists(path):
            with open(path) as f:
                ids = [id.strip() for id in f.read().splitlines() if id != ""]
                if self.id in ids:
                    ids.remove(self.id)
                    with open(path, "w+") as f:
                        f.write("\n".join(ids))

    def is_removed(self):
        removed = self.item is None
        try:
            id = self.item.id
        except:
            removed = True
        return removed

    def is_author_removed(self):
        author_removed = self.item.author is None
        try:
            name = self.item.author.name
        except:
            author_removed = True
        return author_removed

    def get_author_name(self):
        if self.is_author_removed():
            return "[deleted]"
        else:
            return self.item.author.name

    def get_reactions(self):
        reactions = self.subreddit.get_reactions(self.item)
        for r in reactions: r.item = self
        return reactions

    async def add_reactions(self, message):
        for r in self.get_reactions():
            try:
                await message.add_reaction(r.emoji)
            except Exception as e:
                print(e)
                continue

    def get_reaction(self, emoji):
        r = self.subreddit.get_reaction(emoji, self.item)
        r.item = self
        return r

    def get_url(self):
        return get_item_url(self.item)


def get_item_url(item):
    if isinstance(item, praw.models.Submission):
        return "https://www.reddit.com/r/{}/comments/{}".format(item.subreddit, item)
    elif isinstance(item, praw.models.Comment):
        return "https://www.reddit.com/r/{}/comments/{}/_/{}".format(item.subreddit, item.submission, item)
    elif isinstance(item, praw.models.ModmailConversation):
        return "https://mod.reddit.com/mail/all/" + item.id
    elif isinstance(item, praw.models.ModmailMessage):
        return "https://mod.reddit.com/mail/all/" + item.conversation.id
    elif isinstance(item, praw.models.Message):
        if item.was_comment:
            return "https://www.reddit.com/r/{}/comments/{}/_/{}".format(item.subreddit, item.submission, item)
        else:
            return "https://www.reddit.com/message/messages/{}".format(item)
    elif isinstance(item, praw.models.Subreddit):
        return "https://www.reddit.com/r/" + item.display_name
    return ""
