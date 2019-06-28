import discord
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
        if self.type in ["submission", "comment"]:
            return "New {} on /r/{} by /u/{}!\n\nhttps://www.reddit.com{}\n\n**Title:** {}\n**Body:**\n{}".format(
                self.type,
                self.item.subreddit,
                self.item.author,
                self.item.permalink,
                self.item.title,
                self.item.selftext)
        elif self.type == "modmail":
            return "New message in modmail conversation '{}' on /r/{} by /u/{}!\n\n{}".format(
                self.item.conversation.subject, self.item.conversation.owner, self.item.author, self.item.body_markdown)
        else:
            return "New action taken by /u/{} on /r/{}: `{}`".format(self.item.mod, self.item.subreddit,
                                                                     self.item.action)

    def get_embed(self, embed_color=None):
        embed = discord.Embed(
            colour=self.subreddit.bh.embed_color if embed_color is None else embed_color
        )

        title = ""
        if self.type in ["submission", "comment"]:
            if self.source == "reports":
                title = "{} reported on /r/{} by /u/{}!".format(self.type.title(), self.item.subreddit, self.item.author)
            else:
                title = "New {} on /r/{} by /u/{}!".format(self.type, self.item.subreddit, self.item.author)
        elif self.type == "modmail":
            title = "New message in modmail conversation '{}' on /r/{} by /u/{}!".format(self.item.conversation.subject,
                                                                                         self.item.conversation.owner,
                                                                                         self.item.author)
        else:
            title = "New action taken by /u/{} on /r/{}!".format(self.item.mod, self.item.subreddit)

        url = discord.Embed.Empty if self.type not in ["submission", "comment"] else "https://www.reddit.com{}".format(
            self.item.permalink)

        embed.set_author(name=title, url=url)

        if self.type == "submission":
            embed.add_field(name="Title", value=self.item.title, inline=False)
            if self.item.is_self:
                embed.add_field(name="Body", value=self.item.selftext if self.item.selftext != "" else "Empty",
                                inline=False)
            else:
                embed.add_field(name="URL", value=self.item.url, inline=False)
            if self.source == "reports":
                reports = ["{} {}".format(r[1], r[0]) for r in self.item.user_reports]
                embed.add_field(name="Reports", value="\n".join(reports), inline=False)
        elif self.type == "comment":
            embed.description = self.item.body
        elif self.type == "modmail":
            embed.description = self.item.body_markdown
        elif self.type == "mod action":
            embed.description = "Action: `{}`".format(self.item.action)

        return embed

    def save(self, path):
        with open(path, "a+") as f:
            f.write("\n" + self.item.id)

    def remove(self, path):
        with open(path) as f:
            ids = [id.strip() for id in f.read().splitlines() if id != ""]
            if self.id in ids:
                ids.remove(self.id)
                with open(path, "w+") as f:
                    f.write("\n".join(ids))

    def get_reactions(self):
        return self.subreddit.get_reactions(self.item)

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
    elif isinstance(item, praw.models.Message):
        if item.was_comment:
            return "https://www.reddit.com/r/{}/comments/{}/_/{}".format(item.subreddit, item.submission, item)
        else:
            return "https://www.reddit.com/message/messages/{}".format(item)
    elif isinstance(item, praw.models.Subreddit):
        return "https://www.reddit.com/r/" + item.display_name
