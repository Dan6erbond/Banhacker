import re
from urllib.parse import urlparse

from .item import RedditItem


def get_item(reddit, subreddits, str):
    reg = "((https:\/\/)?((www|old|np|mod)\.)?(reddit|redd){1}(\.com|\.it){1}([a-zA-Z0-9\/_]+))"
    for u in re.findall(reg, str):
        if is_url(u[0]):
            item = get_item_from_url(reddit, subreddits, u[0])
            if item is not None:
                return item
            else:
                continue
    return None


def get_item_from_url(reddit, subreddits, url):
    if url.startswith("https://mod.reddit.com/mail/all/"):
        id = url.split("/")[-1] if url.split("/")[-1] != "" else url.split("/")[-2]

        for subreddit in subreddits:
            try:
                modmail = subreddit.subreddit.modmail(id)
                if hasattr(modmail, "subject"):
                    return {
                        "item": modmail,
                        "subreddit": subreddit
                    }
            except Exception as e:
                print("{}: {}".format(type(e), e))

        return None

    item = None
    try:
        item = reddit.comment(url=url)
    except:
        try:
            item = reddit.submission(url=url)
        except:
            print("Invalid URL!")
            return None

    try:
        if not hasattr(item, "subreddit"):  # truly verify if it's a reddit comment or submission
            return None
    except:
        return None

    sub = None
    for sub in subreddits:
        if sub.subreddit.id == item.subreddit.id:
            subreddit = sub
            break

    if subreddit is None:
        return None

    return RedditItem(item, sub, "url")


def is_url(url):
    check = urlparse(url)
    if check.scheme != "" and check.netloc != "":
        return True
    else:
        return False
