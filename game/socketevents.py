from flask_socketio import Namespace, emit
from flask_jwt_extended import jwt_required, jwt_optional
from flask import request
from .util import *
from game.game import Game


class ConnecticutSockets(Namespace):

    users = {}

    @jwt_optional
    def on_connect(self):
        user = get_user()
        if user == None:
            return emit("should_disconnect")

    @jwt_optional
    def on_startup(self, data):
        user = get_user()
        if user == None:
            return emit("should_disconnect")

        if "gameid" in data:
            game = Game.get_by_id(data["gameid"])
            if user.in_game(game):
                self.__class__.users[(user.id, data["gameid"])] = request.sid
            else:
                return emit("invalid_packet")
        else:
            return emit("invalid_packet")

    @jwt_optional
    def on_move(self, data):
        print("hi")
        user = get_user()
        if user == None:
            return emit("should_disconnect")

        if 'x' in data and 'y' in data and 'gameid' in data:
            game = Game.get_by_id(data["gameid"])
            if user.in_game(game):
                piece = game.place_piece(data['x'], data['y'])
                if piece == None:
                    return emit("invalid_move")

                print(f"placed piece at ({piece.x}, {piece.y})")

                emit("new_piece", data={
                    "x": piece.x,
                    "y": piece.y,
                }, room=self.__class__.users[
                    (game.other_player(user).id, data["gameid"])
                ])

            else:
                return emit("invalid_packet")
        else:
            return emit("invalid_packet")

