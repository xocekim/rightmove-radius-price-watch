import sqlite3

from flask import Flask, render_template, g


app = Flask(__name__)

DATABASE = "rightmove.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    con = get_db()
    properties = con.execute("SELECT * FROM property ORDER BY first_seen DESC LIMIT 10")
    return render_template("index.html", properties=properties)


@app.route("/changes")
def changes():
    con = get_db()
    properties = con.execute("SELECT * FROM v_price_history")
    return render_template("changes.html", properties=properties)
