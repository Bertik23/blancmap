from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from passlib.hash import bcrypt_sha256 as bcrypt

from app import app, renderTemplate
from database import connect
from forms import LoginForm, RegistrationForm
from user import getUser


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
