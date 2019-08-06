from game.player import Player
from flask_jwt_extended import get_jwt_identity

def get_user():
    userid = get_jwt_identity()
    if userid is not None:
        return Player.get_or_none(Player.id == userid)
    else:
        return None

def is_ascii(string) :
    for letter in string:
        if ord(letter) >= 128:
            return False
    return True
