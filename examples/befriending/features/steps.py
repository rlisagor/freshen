from freshen import *
from friends import find_user

@Transform(r'^user (\w+)$')
def transform_user(username):
    return find_user(username)

@When(r'^(user \w+) befriends (user \w+)$')
def befriend(user, friend):
    user.befriend(friend)

@Then(r'^(user \w+) should be friends with (user \w+)$')
def check_friends(user, friend):
    assert user.is_friends_with(friend)

