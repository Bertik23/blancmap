from flask import flash, jsonify, request, session

from app import NOT_LOGGED_IN, app
from database import connect
from forms import LoginForm, RegistrationForm
from maps import deleteMap, getCurrentMap, getMap, updateCurrentMap, updateMap
from user import getUser


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
