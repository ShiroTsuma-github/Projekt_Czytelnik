from packages import app
from flask import render_template
from flask import g
import os
import sqlite3
DATABASE_DIR = 'databases/'
DATABASE_NAME = 'ksiazki.db'
DATABASE_SCHEMA = 'ksiazki.sql'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).replace("packages","")

# https://www.geeksforgeeks.org/how-to-build-a-web-app-using-flask-and-sqlite-in-python/


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(f'{ROOT_DIR}{DATABASE_DIR}{DATABASE_NAME}')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Run this only if database is empty or there were changes to ksiazki.sql
    """
    with app.app_context():
        db = get_db()
        with app.open_resource(f'{ROOT_DIR}{DATABASE_DIR}{DATABASE_SCHEMA}', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


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


# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()
