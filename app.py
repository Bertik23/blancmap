import logging

from flask import Flask, jsonify, render_template, session

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
