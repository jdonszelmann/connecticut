from flask_socketio import Namespace, emit
from flask_jwt_extended import jwt_required, jwt_optional
from .util import *
from ..game import Game


class ConnecticutSockets(Namespace):

    @jwt_optional
    def on_connect(self):
        user = get_user()
        if user == None:
            return emit("should_disconnect")

    @jwt_optional
    def on_move(self, data):
        user = get_user()
        if user == None:
            return emit("should_disconnect")

        game = Game.get_by_id(data["gameid"])
        print(data)
        # if user.in_game(game):
        #
        # else:
        #     return

