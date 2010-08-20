from freshen import *
from friends import find_user
from itertools import combinations

@Transform(r'^user (\w+)$')
def transform_user(username):
    return find_user(username)

@NamedTransform( '{user list}', r'([\w, ]+)' )
def transform_user_list( user_list ):
    return [ find_user( name.strip() ) for name in user_list.split( ',' ) ]

@When(r'^(user \w+) befriends (user \w+)$')
def befriend(user, friend):
    user.befriend(friend)

@Then(r'^(user \w+) should be friends with (user \w+)$')
def check_friends(user, friend):
    assert user.is_friends_with(friend)

@Then(r'these users should be friends: {user list}' )
def check_all_friends( user_list ):
    for user1, user2 in combinations( user_list, 2 ):
        assert user1.is_friends_with( user2 )
    

