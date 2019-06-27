# The Banhacker Bot
By [Mariavi](https://dan6erbond.github.io/mariavi)

Banhacker is the very first bot to integrate the [Banhammer Framework](https://github.com/Dan6erbond/Banhammer-Framework) and thus enable a seamless moderation experience for Reddit.

## Functionality
The bot streams different types of items from subreddits that are registered to it such as reported posts, mod actions as well as mod-mail to dedicated channels and allows you to react to some of them with **Reactions**.

After responding to a message by clicking on one of its reactions, this bot will delete the source message and send a new one in either the `#🔨approved-posts` or `#🔨removed-posts` channel once it has performed the actions that the reaction is configured to do. Those actions can be customized by going to the subreddit's wiki page called `banhammer-reactions` which is automatically created if it doesn't exist yet and automatically filled with default reactions if there aren't any configured.

## Personal Use
The bot's code can be downloaded and slightly modified, particularly the channel IDs within each trigger function as well as the subreddit and its settings if you wish to create your own version of this bot though the framework is still a work in progress and documentation as well as updates can be found on the [GitHub page](https://github.com/Dan6erbond/Banhammer-Framework).

If you do want to use this bot's code as a base, make sure you install both [PRAW]() and [Discord.py]() as they are required by the bot. They can be installed with the following commands:
`pip3 install -U discord.py`
`pip3 install -U praw`

## Showcase
This bot was created for the **Discord Hackweek Event** and showcases the functionality of the framework in a very simple fashion on [Mariavi's Banhammer Discord server](https://discordapp.com/invite/9JrGC8f). More examples will be created in the future that allow the user to install the bot on their local machine as well as set it up for their own Discord servers!

**An example of a new post streamed to its dedicated channel:**

![New posts are streamed to a dedicated channel on Discord.](img/Anmerkung%202019-06-27%20184629.jpg)

## The Banhammer Bot and Reddify
In addition to the open-source framework, and this bot as an example for it, a proprietary version of the bot, called [The Banhammer Bot](https://dan6erbond.github.io/mariavi/banhammer.html), is being made by the Mariavi developers that doesn't require any coding knowledge whatsoever and will be hosted on Mariavi's servers. With commands it can be setup to stream certain subreddit's post to channels it will create and using [Reddify](https://dan6erbond.github.io/mariavi/reddify.html) it will ensure that the bot's moderator status on other subreddits isn't abused.
