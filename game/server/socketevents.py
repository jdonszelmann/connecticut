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


    def on_disconnect(self):
        userid = self.__class__.revsockets[request.sid]
        del self.__class__.sockets[userid]
        del self.__class__.revsockets[request.sid]

    @classmethod
    def send_to(cls, event, message, user):
        emit(
            'status',
            message,
            room=cls.sockets[user.id]
        )
