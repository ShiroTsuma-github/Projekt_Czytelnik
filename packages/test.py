from packages import app
from flask import render_template
from flask import g
import sqlite3
DATABASE = 'databases/ksiazki.db'

# https://www.geeksforgeeks.org/how-to-build-a-web-app-using-flask-and-sqlite-in-python/

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('databases/ksiazki.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


@app.route('/')
def index():
    cur = get_db().cursor()
    return render_template('base.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
