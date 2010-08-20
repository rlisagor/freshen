class User(object):
    
    def __init__(self, name):
        self.name = name
        self.friends = []
    
    def befriend(self, other):
        if other.name not in self.friends:
            self.friends.append(other.name)
        if not other.is_friends_with(self):
            other.befriend(self)
    
    def is_friends_with(self, other):
        return other.name in self.friends


users = {
    'paxton': User('paxton'),
    'adelaide': User('adelaide'),
    'hazel': User('hazel'),
    'duane': User('duane')
}

def find_user(name):
    return users.get(name)

