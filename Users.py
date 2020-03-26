class User(object):
    """An object that identifies the user, probably needs a better implementation tbh"""

    def __init__(self, username, pwhash):
        self.username = username
        self.pwhash = pwhash
        self.uid = User.generate_uid(username,pwhash)

    def as_player(self):
        return Player(self.username)

    @classmethod
    def generate_uid(cls, username, pwhash):
        # needs better method
        return hash(username + pwhash)

class Player(object):
    """Internal representation of a player in a game"""

    def __init__(self, username):
        self.username = username
        self.sets = 0
        self.blocked = False

    def to_json(self):
        return {"username" : self.username,
                "sets" : self.sets,
                "blocked" : self.blocked}
