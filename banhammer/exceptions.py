class BanhammerException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)

class NotModerator(BanhammerException):
    def __init__(self, user, sub):
        super(NotModerator, self).__init__("/u/{} doesn't moderate /r/{}.".format(user, sub))