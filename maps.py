import json

from exceptions import ToManyMaps
from database import connect, close


def getMap(userId, name):
    con, cur = connect()

    cur.execute(
        "SELECT data FROM maps WHERE userId = ? AND name = ?",
        (userId, name)
    )
    maps = cur.fetchall()
    close(con, cur)
    if len(maps) > 1:
        raise ToManyMaps
    elif len(maps) == 0:
        return {}
    return json.loads(maps[0][0])


def getCurrentMap(userId):
    return getMap(userId, "Current")


def updateMap(userId, name, data):
    con, cur = connect()

    cur.execute(
        "SELECT id FROM maps WHERE userId = ? AND name = ?",
        (userId, name)
    )
    if len(cur.fetchall()) == 0:
        cur.execute(
            "INSERT INTO maps (userId, name, data) VALUES (?, ?, ?)",
            (userId, name, json.dumps(data))
        )
    else:
        cur.execute(
            "UPDATE maps SET data = ? WHERE userId = ? AND name = ?",
            (json.dumps(data), userId, name)
        )
    con.commit()
    close(con, cur)


def updateCurrentMap(userId, data):
    updateMap(userId, "Current", data)


def getUserMapsList(userId):
    con, cur = connect()

    cur.execute("SELECT name FROM maps WHERE userId = ?", (userId, ))

    out = [i[0] for i in cur.fetchall()]

    close(con, cur)

    return out
