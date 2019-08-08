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
        user = get_user()
        if user == None:
            return emit("should_disconnect")

        # check packet validity
        if not ('x' in data and 'y' in data and 'gameid' in data):
            return emit("invalid_packet")

        # check if the game in the packet is actually
        # a game the user is in
        game = Game.get_by_id(data["gameid"])
        if not user.in_game(game):
            return emit("invalid_packet")

        if not (game.player1 and game.player2):
            return emit("no_opponent")

        # check if the user can actually move.
        if user.id != game.who.id:
            return emit("not_your_turn")

        piece = game.place_piece(data['x'], data['y'])
        if piece is None:
            # when a created piece is None it
            # is in an invalid position
            return emit("invalid_move")

        try:
            # try sending to your opponent
            emit("new_piece", {
                "x": piece.x,
                "y": piece.y,
                "owned": piece.player == user.id,
            }, room=self.__class__.users[
                (game.other_player(user).id, data["gameid"])
            ])
        except KeyError:
            # if he doesn't answer, notify sender
            emit("opponent_offline")

        return emit("new_piece", {
            "x": piece.x,
            "y": piece.y,
            "owned": piece.player == user.id
        })


