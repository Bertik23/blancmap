from maps import getUserMapsList
from database import connect
from exceptions import UserNotExistent
import json


def getUser(id):
    if id is None:
        return None
    try:
        return User(id)
    except UserNotExistent:
        return None


class User:
    def __init__(self, id):
        con, cur = connect()
        cur.execute(
            "SELECT id, username, email, settings FROM users WHERE id = ?",
            (id, )
        )
        user = cur.fetchone()
        cur.close()
        con.close()
        self.id = user[0]
        self.username = user[1]
        self.email = user[2]
        self.mapsList = getUserMapsList(self.id)
        self.settings = json.loads(user[3]) if user[3] is not None else None
