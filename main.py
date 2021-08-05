from maps import getCurrentMap, updateCurrentMap, getMap, updateMap, deleteMap
import loadEnv

import logging
import os

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for, jsonify)
from passlib.hash import bcrypt_sha256 as bcrypt

from database import connect
from forms import LoginForm, RegistrationForm
from user import getUser

logger = logging.Logger("main", logging.INFO)

app = Flask("Blancmap")
app.secret_key = b"_randomThingo"


def NOT_LOGGED_IN():
    return jsonify(
        {
            "status": "failed",
            "message": "Not logged in or corrupted user id"
        }
    ), 422


def renderTemplate(template, **kwargs):
    return render_template(
        template,
        user=getUser(session.get("userId", None)),
        **kwargs
    )


@app.route("/")
def site_index():
    return renderTemplate("index.html")


@app.route("/register", methods=["GET", "POST"])
def site_register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        con, cur = connect()
        cur.execute(
            "SELECT username FROM users WHERE username = ?",
            (form.username.data,)
        )
        if len(cur.fetchall()) != 0:
            flash(
                (
                    "Username already taken. | "
                    f"{form.username.data} is already taken."
                    " Please use anotherone."
                ),
                category="error"
            )
            return renderTemplate("register.html", form=form)
        cur.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (
                form.username.data,
                bcrypt.hash(form.password.data),
                form.email.data)
            )
        con.commit()
        cur.close()
        con.close()
        flash(
            "Successfuly registered. | You are now logged in.",
            category="success"
        )
        return redirect(url_for('site_index'))
    return renderTemplate("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def site_login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        print("POST")
        con, cur = connect()
        cur.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (form.username.data,)
        )
        out = cur.fetchone()
        cur.close()
        con.close()
        if bcrypt.verify(form.password.data, out[2]):
            flash(
                "Successfuly logged in. | You are now logged in.",
                category="success"
            )
            session["userId"] = out[0]
            return redirect(request.args.get("next", url_for('site_index')))

    return renderTemplate("login.html", form=form)


@app.route("/user/<uid>")
def site_user(uid):
    user = getUser(uid)
    return renderTemplate("user_profile.html", dUser=user)


@app.route("/api/logout")
def api_logout():
    uId = session.get("userId", None)
    if uId is None:
        pass
    else:
        session["userId"] = None
    flash("Logged out | You were logged out.", category="success")
    return jsonify(
        {
            "status": "success",
            "message": "Successfully loged out."
        }
    )


@app.route("/api/updateCurrentMap", methods=["POST", "DELETE"])
def api_updateCurrentMap():
    user = getUser(session.get("userId"))
    if user is None:
        return NOT_LOGGED_IN()
    if request.method == "POST":
        data = request.get_json()
        id_ = data["id"]
        object = data["object"]
        mapData = getCurrentMap(user.id)
        mapData[id_] = object
        updateCurrentMap(user.id, mapData)
        return jsonify(
            {
                "status": "success",
                "message": (
                    f"Object with id = {id_} "
                    "successfully added."
                )
            }
        )
    elif request.method == "DELETE":
        id_ = request.args["id"]
        if id_ == "all":
            mapData = getCurrentMap(user.id)
            mapData.pop(id_, None)
        mapData = {}
        updateCurrentMap(user.id, mapData)
        return jsonify(
            {
                "status": "success",
                "message": (
                    f"Object with id = {request.args['id']} "
                    "successfully removed."
                )
            }
        )


@app.route("/api/getMap")
def api_getMap():
    user = getUser(request.args.get("userId", session.get("userId")))
    name = request.args.get("name", None)
    if user is None:
        return NOT_LOGGED_IN()
    if name is None:
        return jsonify(
            {
                "status": "failed",
                "message": "No name supplied"
            }
        ), 400
    return jsonify(
        {
            "status": "success",
            "message": "Here is your map.",
            "data": getMap(user.id, name)
        }
    )


@app.route("/api/saveMap", methods=["POST"])
def api_saveMap():
    user = getUser(session.get("userId"))
    if user is None:
        return NOT_LOGGED_IN()
    data = request.get_json()
    name = data["name"]
    mapData = data["map"]

    updateMap(user.id, name, mapData)
    return jsonify(
        {
            "status": "success",
            "message": (
                f"Map with {name = } "
                "successfully saved."
            )
        }
    )


@app.route("/api/deleteMap", methods=["DELETE"])
def api_deleteMap():
    user = getUser(session.get("userId", None))
    if user is None:
        return NOT_LOGGED_IN()
    deleteMap(user.id, request.args.get("name", None))
    return jsonify(
        {
            "status": "success",
            "message": f"Map was successfully deleted."
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
