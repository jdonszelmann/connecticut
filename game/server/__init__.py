import threading
from ..config import Config
import os
from flask_jwt_extended import JWTManager
from .routes import *
from flask import redirect
import secrets
import flask
from flask_socketio import SocketIO, emit
from .socketevents import socketevents

path = os.path.dirname(os.path.realpath(__file__))


class Server(flask.Flask):
    def __init__(self):
        super().__init__(
            "Connecticut",
            root_path=path
        )

        self.blacklist = set()

        self.config["SECRET_KEY"] = secrets.token_urlsafe(40)
        self.config["SECRET_KEY"] = "test"
        self.config["JWT_TOKEN_LOCATION"] = "cookies"
        self.config['JWT_BLACKLIST_ENABLED'] = True
        self.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
        self.jwt = JWTManager(self)

        self.socketio = SocketIO(self)

        @self.jwt.invalid_token_loader
        def on_invalid_token():
            response = redirect("/", code=302)
            flask_jwt_extended.unset_access_cookies(response)
            flask_jwt_extended.unset_refresh_cookies(response)
            return response

        @self.jwt.revoked_token_loader
        def on_revoked_token():
            response = redirect("/", code=302)
            flask_jwt_extended.unset_access_cookies(response)
            flask_jwt_extended.unset_refresh_cookies(response)
            return response

        @self.jwt.expired_token_loader
        def on_expired_token():
            response = redirect("/", code=302)
            flask_jwt_extended.unset_access_cookies(response)
            flask_jwt_extended.unset_refresh_cookies(response)
            return response

        @self.jwt.token_in_blacklist_loader
        def check_if_token_in_blacklist(decrypted_token):
            jti = decrypted_token['jti']
            return jti in self.blacklist

        @self.errorhandler(404)
        def handle_404(error):
            return flask.render_template("404.html"), 404

        socketevents(self, self.socketio)
        routes(self)



    def run_in_thread(self, *args, **kwargs):

        threading.Thread(
            target=self.socketio.run,
            args=(
                self,
                Config.get_config_option("address"),
                int(Config.get_config_option("port")),
            ),
            kwargs={
                "log_output": True
            }
        ).start()

