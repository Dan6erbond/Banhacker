# The Banhacker Bot
By Mariavi

Banhacker is the very first bot to integrate the [Banhammer Framework](https://github.com/Dan6erbond/Banhammer-Framework) and thus enable a seamless moderation experience for Reddit. It streams different types of items such as reported posts, mod actions as well as mod-mail to dedicated channels and allows you to react to some of them with **Reactions**.

After responding to a message by clicking on one of its reactions, this bot will delete the source message and send a new one in either the `#🔨approved-posts` or `#🔨removed-posts` channel once it has performed the actions that the reaction is configured to do. Those actions can be customized by going to the subreddit's wiki page called `banhammer-reactions` which is automatically created if it doesn't exist yet and automatically filled with reactions if there aren't any configured.

The bot's code can be downloaded and slightly modified, particularly the channel IDs within each trigger function as well as the subreddit and its settings if you wish to create your own version of this bot though the framework is still a work in progress and documentation as well as updates can be found on the [GitHub page](https://github.com/Dan6erbond/Banhammer-Framework).

This bot was created for the **Discord Hackweek Event** and showcases the functionality of the framework in a very simple fashion on [Mariavi's Banhammer Discord server](https://discordapp.com/invite/9JrGC8f). More examples will be created in the future that allow the user to install the bot on their local machine as well as set it up for their own Discord servers!

**An example of a new post streamed to its dedicated channel:**

![New posts are streamed to a dedicated channel on Discord.](img/Anmerkung%202019-06-27%20184629.jpg)
