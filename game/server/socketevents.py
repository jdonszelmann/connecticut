from flask_socketio import Namespace, emit
from flask_jwt_extended import jwt_required, jwt_optional
from .util import *
from flask import request

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

        if user.game.
        print(data)
