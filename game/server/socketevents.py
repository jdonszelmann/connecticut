from flask_socketio import Namespace, emit, send
from flask_jwt_extended import jwt_required
from .util import *
from flask import request

class SocketNamespace(Namespace):

    sockets = {}
    revsockets = {}

    @jwt_required
    def on_connect(self):
        user = get_user()
        self.__class__.sockets[user.id] = request.sid
        self.__class__.revsockets[request.sid] = user.id

    @jwt_required
    def on_get_game(self, message):
        pass

    def on_disconnect(self):
        userid = self.__class__.revsockets[request.sid]
        del self.__class__.sockets[userid]
        del self.__class__.revsockets[request.sid]

    def send_to(self, event, message, user):
        emit(
            'status',
            message,
            room=self.__class__.sockets[user.id]
        )
