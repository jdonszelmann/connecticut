# this file has the normal app.routes that aren't necessarily RESTful
from flask_jwt_extended import get_jwt_identity
from flask import request, jsonify, redirect, render_template
from flask_bcrypt import generate_password_hash, check_password_hash
import flask_jwt_extended
from flask_jwt_extended import jwt_optional, jwt_required
from email.utils import parseaddr
from ..game import Game
from .util import *
from .socketevents import ConnecticutSockets

def routes(app):
    @app.route("/game")
    @jwt_required
    def game():
        user = get_user()
        if user == None:
            return redirect("/login", 302)

        existinggame = Game.get_or_none(Game.player2.is_null())
        if existinggame == None:
            existinggame = Game.create_default(
                player1=user
            )
        else:
            existinggame.player2 = user
            existinggame.save()

        gameid = existinggame.id

        return redirect(f"/game/{gameid}", 302)

    @app.route("/game/<int:game_id>")
    @jwt_required
    def specificgame(game_id):
        user = get_user()
        if user == None:
            return redirect("/login", 302)
        game = Game.get(Game.id == game_id)
        if user != game.player1 and user != game.player2:
            return redirect("/", 302)

        return render_template("game.html", user=user, game=game), 200

    @app.route("/")
    @jwt_optional
    def index():
        user = get_user()
        return render_template("index.html", user=get_user()), 200

    @app.route("/login", methods=["GET"])
    @jwt_optional
    def login():
        return render_template("login.html", user=get_user()), 200

    @app.route("/register", methods=["GET"])
    @jwt_optional
    def register():
        return render_template("register.html", user=get_user()), 200

    @app.route("/logout")
    @jwt_optional
    def logout():
        jwt = flask_jwt_extended.get_raw_jwt()

        if "jti" not in jwt:
            # already unset
            return redirect("/", code=302)

        app.blacklist.add(jwt['jti'])

        response = redirect("/", code=302)

        flask_jwt_extended.unset_access_cookies(response)
        flask_jwt_extended.unset_refresh_cookies(response)

        return response


    @app.route("/register", methods=["POST"])
    def postregister():
        try:
            email = request.json["email"]
            password = request.json["password"]
            username = request.json["username"]

            if parseaddr(email) == ('', ''):
                return jsonify({
                    "status": "Invalid email address"
                })

            if len(password) < 8:
                return jsonify({
                    "status": "Password too short (must be 10 characters or more)"
                })

            if not is_ascii(password):
                return jsonify({
                    "status": "Password must be in the ascii range"
                })

            if not is_ascii(username):
                return jsonify({
                    "status": "Username must be in the ascii range"
                })

            if len(username) < 3:
                return jsonify({
                    "status": "Username must be longer than 3 characters"
                })

            if Player.select().where(Player.email == email).exists():
                return jsonify({
                    "status": "Email address already in use"
                })

            Player.create(email=email, username=username, password_hash=generate_password_hash(password))

            return jsonify({
                "status": "ok"
            })

        except Exception as e:
            raise
            print(f"An error occurred: {e}")
            return jsonify({
                "status": "server error"
            })


    @app.route("/login", methods=["POST"])
    def postlogin():
        try:
            email = request.json["email"]
            password = request.json["password"]

            user = Player.get_or_none(Player.email == email)

            if not user:
                return jsonify({
                    "status": "not found",
                })

            if check_password_hash(user.password_hash, password):
                access_token = flask_jwt_extended.create_access_token(identity=user.id)
                refresh_token = flask_jwt_extended.create_refresh_token(identity=user.id)

                response = jsonify({"status": "ok"})

                flask_jwt_extended.set_access_cookies(response, access_token)
                flask_jwt_extended.set_refresh_cookies(response, refresh_token)

                return response

            return jsonify({
                "status": "password incorrect"
            })

        except Exception as e:
            raise
            print(f"An error occurred: {e}")
            return jsonify({
                "status": "server error"
            })
