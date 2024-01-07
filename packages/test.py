from packages import app
from flask import render_template, request, redirect, url_for
from flask import g
from flask import Flask
import os
import sqlite3
import logging
DATABASE_DIR = 'databases/'
DATABASE_NAME = 'ksiazki.db'
DATABASE_SCHEMA = 'ksiazki.sql'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).replace("packages", "")

# https://www.geeksforgeeks.org/how-to-build-a-web-app-using-flask-and-sqlite-in-python/

# w formie komentarz


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(f'{ROOT_DIR}{DATABASE_DIR}{DATABASE_NAME}')
    return db


def get_cursor():
    return get_db().cursor()


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


@app.route("/add", methods=["GET", "POST"])
def addBook():
    if request.method == 'POST':
        tytul = request.form['tytul']
        autor = request.form['autor']
        okladka = None if request.form['okladka'] == "" else request.form['okladka']
        rozdzialy = int(request.form['total_chapters'])
        przeczytane = int(request.form['actual_chapters'])
        ocena = int(request.form.get('ocena', '0'))
        gatunek = (request.form['wybrane_gatunki']).split(',')
        komentarz = request.form.get('komentarz', None)
        tagi = None if request.form['tagi'] == "" else request.form['tagi']
        cur = get_db().cursor()
        db = get_db()
        cur.execute('SELECT autor_id FROM Autor WHERE autor_nazwa = (?)',
                    (autor,))
        autor_id = cur.fetchall()
        if len(autor_id) == 0:
            cur.execute('INSERT INTO Autor (autor_nazwa) VALUES (?)',
                        (autor,))
            db.commit()
        cur.execute('INSERT INTO Ksiazka (ksiazka_tytul, ksiazka_strony, ksiazka_przeczytane, ksiazka_ocena, ksiazka_okladka, ksiazka_komentarz) VALUES (?, ?, ?, ?, ?, ?)',
                    (tytul, rozdzialy, przeczytane, ocena, okladka, komentarz))
        db.commit()
        cur.execute('SELECT autor_id FROM Autor WHERE autor_nazwa = (?)',
                    (autor,))
        autor_id = cur.fetchall()[0][0]
        cur.execute('SELECT ksiazka_id FROM Ksiazka WHERE ksiazka_tytul = (?)',
                    (tytul,))
        ksiazka_id = cur.fetchall()[0][0]
        cur.execute('INSERT INTO ksiazka_autor (ksiazka_id, autor_id) VALUES (?, ?)',
                    (ksiazka_id, autor_id))
        db.commit()

    return redirect(url_for('index'))


@app.route('/')
def index():
    cur = get_cursor()
    cur.execute('select ks.*, au.* from ksiazka as ks LEFT join ksiazka_autor as ka on ka.ksiazka_id = ks.ksiazka_id left join autor as au on au.autor_id = ka.autor_id') 
    data = cur.fetchall() 
    return render_template("base.html", data=data) 


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



logging.basicConfig(filename='record.log', level=logging.INFO)
app = Flask(__name__)

@app.route('/')
def main():
    app.logger.debug("debug log info")
    app.logger.info("Info log information")
    app.logger.warning("Warning ")
    app.logger.error("Error")
    app.logger.critical("Critical Error")
    return "testing logging levels."
