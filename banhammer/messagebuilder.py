import discord


class MessageBuilder:
    def get_item_message(self, item):
        if item.type in ["submission", "comment"]:
            return "New {} on /r/{} by /u/{}!\n\nhttps://www.reddit.com{}\n\n**Title:** {}\n**Body:**\n{}".format(
                item.type,
                item.item.subreddit,
                item.item.author,
                item.item.permalink,
                item.item.title,
                item.item.selftext)
        elif item.type == "modmail":
            return "New message in modmail conversation '{}' on /r/{} by /u/{}!\n\n{}".format(
                item.item.conversation.subject, item.item.conversation.owner, item.item.author, item.item.body_markdown)
        else:
            return "New action taken by /u/{} on /r/{}: `{}`".format(item.item.mod, item.item.subreddit,
                                                                     item.item.action)

    def get_item_embed(self, item, embed_color=None):
        embed = discord.Embed(
            colour=item.subreddit.banhammer.embed_color if embed_color is None else embed_color
        )

        title = ""
        if item.type in ["submission", "comment"]:
            if item.source == "reports":
                title = "{} reported on /r/{} by /u/{}!".format(item.type.title(), item.item.subreddit,
                                                                item.item.author)
            else:
                title = "New {} on /r/{} by /u/{}!".format(item.type, item.item.subreddit, item.item.author)
        elif item.type == "modmail":
            title = "New message in modmail conversation '{}' on /r/{} by /u/{}!".format(item.item.conversation.subject,
                                                                                         item.item.conversation.owner,
                                                                                         item.item.author)
        else:
            title = "New action taken by /u/{} on /r/{}!".format(item.item.mod, item.item.subreddit)

        url = item.get_url()
        embed.set_author(name=title, url=url if url != "" else discord.Embed.Empty)

        if item.type == "submission":
            embed.add_field(name="Title", value=item.item.title, inline=False)
            if item.item.is_self:
                embed.add_field(name="Body", value=item.item.selftext if item.item.selftext != "" else "Empty",
                                inline=False)
            else:
                embed.add_field(name="URL", value=item.item.url, inline=False)
            if item.source == "reports":
                reports = ["{} {}".format(r[1], r[0]) for r in item.item.user_reports]
                embed.add_field(name="Reports", value="\n".join(reports), inline=False)
        elif item.type == "comment":
            embed.description = item.item.body
        elif item.type == "modmail":
            embed.description = item.item.body_markdown
        elif item.type == "mod action":
            embed.description = "Action: `{}`".format(item.item.action)

        return embed
