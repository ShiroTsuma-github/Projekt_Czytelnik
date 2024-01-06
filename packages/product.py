from packages import app
from flask import render_template, request, redirect, url_for
from flask import g
import os
import sqlite3
from dataclasses import dataclass
DATABASE_DIR = 'databases/'
DATABASE_NAME = 'ksiazki.db'
DATABASE_SCHEMA = 'ksiazki.sql'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).replace("packages", "")

# https://www.geeksforgeeks.org/how-to-build-a-web-app-using-flask-and-sqlite-in-python/

# w formie komentarz


@dataclass
class Ksiazka:
    """
    Represents a book with various attributes.

    Attributes:
        tytul (str): The title of the book.
        autor (str): The author of the book.
        okladka (str): The cover image of the book.
        rozdzialy (int): The total number of chapters in the book.
        przeczytane (int): The number of chapters already read.
        ocena (int, optional): The rating given to the book (default is 0).
        gatunek (List[str], optional): A list of genres associated with the book.
        komentarz (str, optional): Any comments or remarks about the book.
        tagi (List[str], optional): A list of tags associated with the book.

    Usage:
        Use this class to create instances representing individual books.
    """
    tytul: str
    autor: str
    okladka: str
    rozdzialy: int
    przeczytane: int
    ocena: int = 0
    gatunek: list = None
    komentarz: str = None
    tagi: list = None


def get_db() -> sqlite3.Connection:
    """
    Retrieves the SQLite database connection.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.

    Raises:
        sqlite3.Error: If there is an issue connecting to the database.

    Usage:
        Use this function to obtain a connection to the SQLite database for executing queries.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            f'{ROOT_DIR}{DATABASE_DIR}{DATABASE_NAME}')
    return db


def get_cursor() -> sqlite3.Cursor:
    """
    Retrieves a cursor object connected to the database.

    Returns:
        sqlite3.Cursor: A cursor object linked to the database.

    Raises:
        RuntimeError: If the application context is not available.
        sqlite3.Error: If there is an issue connecting to the database or creating a cursor.

    Usage:
        Use this function to obtain a cursor for executing SQL queries on the database.
    """
    return get_db().cursor()


def init_db():
    """
    Initializes the database by running the SQL schema script if the database is empty or if changes were made to ksiazki.sql.

    Note:
        This function should be run only when necessary, such as when the database is empty or when changes have been made to the database schema.

    Raises:
        RuntimeError: If the application context is not available.
        sqlite3.Error: If there is an issue executing the SQL script or committing the changes to the database.

    Usage:
        Call this function to ensure the database is set up with the latest schema.
    """
    with app.app_context():
        db = get_db()
        with app.open_resource(f'{ROOT_DIR}{DATABASE_DIR}{DATABASE_SCHEMA}', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def make_dicts(cursor, row):
    """
    Convert a database row into a dictionary with column names as keys.

    Args:
        cursor (sqlite3.Cursor): The cursor object representing the database connection.
        row (tuple): A database row to be converted into a dictionary.

    Returns:
        dict: A dictionary with column names as keys and corresponding values from the row.

    Usage:
        This function is typically used as the `row_factory` when fetching data from the database to obtain results as dictionaries.
    """
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def parse_request(request) -> Ksiazka:
    """
    Parses a request object and creates a Ksiazka (book) instance.

    Args:
        request (object): A request object containing form data.

    Returns:
        Ksiazka: An instance of the Ksiazka class with the provided information.

    Raises:
        ValueError: If the required form fields are missing or have incorrect values.
    """
    try:
        k = Ksiazka(request.form['tytul'],
                    request.form['autor'],
                    None if request.form['okladka'] == "" else request.form['okladka'],
                    int(request.form['total_chapters']),
                    int(request.form['actual_chapters']),
                    int(request.form.get('ocena', '0')),
                    [str(item).strip()
                    for item in (request.form['wybrane_gatunki']).split(',')],
                    request.form.get('komentarz', None),
                    None if request.form['tagi'] == "" else [
                        item.strip() for item in (request.form['tagi']).split(',')]
                    )
    except ValueError:
        # TODO: Add logging
        # TODO: Add error message
        raise ValueError("Missing or incorrect form fields.")
    return k


def insert_book(k: Ksiazka) -> None:
    """
    Inserts book information into the database.

    Args:
        k (Ksiazka): An instance of the Ksiazka class representing the book to be inserted.

    Raises:
        RuntimeError: If there is an issue executing SQL queries or committing changes to the database.
        sqlite3.Error: If there is an issue with the SQLite database operations.

    Usage:
        Call this function to insert a book into the database with its associated authors, genres, and tags.
    """
    cur = get_db().cursor()
    db = get_db()

    # DODAJ AUTORA ############################## noqa: E266
    # SPRAWDŹ CZY ISTNIEJE AUTOR
    cur.execute('SELECT autor_id FROM Autor WHERE autor_nazwa = (?)',
                (k.autor,))
    autor_id = cur.fetchall()
    # JEŚLI NIE ISTNIEJE TO DODAJ
    if len(autor_id) == 0:
        cur.execute('INSERT INTO Autor (autor_nazwa) VALUES (?)',
                    (k.autor,))
        db.commit()

    # DODAJ KSIĄŻKĘ ############################ noqa: E266
    cur.execute('INSERT INTO Ksiazka (ksiazka_tytul, ksiazka_strony, ksiazka_przeczytane, ksiazka_ocena, ksiazka_okladka, ksiazka_komentarz) VALUES (?, ?, ?, ?, ?, ?)',
                (k.tytul, k.rozdzialy, k.przeczytane, k.ocena, k.okladka, k.komentarz))
    db.commit()

    # DODAJ AUTORA KSIĄŻKI ###################### noqa: E266
    # POBIERZ ID AUTORA
    cur.execute('SELECT autor_id FROM Autor WHERE autor_nazwa = (?)',
                (k.autor,))
    autor_id = cur.fetchall()[0][0]
    # POBIERZ ID KSIĄŻKI
    cur.execute('SELECT ksiazka_id FROM Ksiazka WHERE ksiazka_tytul = (?)',
                (k.tytul,))
    ksiazka_id = cur.fetchall()[0][0]
    # DODAJ AUTORA KSIĄŻKI
    cur.execute('INSERT INTO ksiazka_autor (ksiazka_id, autor_id) VALUES (?, ?)',
                (ksiazka_id, autor_id))

    # DODAJ GATUNKI ########################## noqa: E266
    for gatunek in k.gatunek:
        # SPRAWDŹ CZY ISTNIEJE
        cur.execute('SELECT gatunek_id FROM Gatunek WHERE gatunek_nazwa = (?)',
                    (gatunek,))
        gatunek_id = cur.fetchall()
        # JEŚLI NIE ISTNIEJE TO DODAJ
        if len(gatunek_id) == 0:
            cur.execute('INSERT INTO Gatunek (gatunek_nazwa) VALUES (?)',
                        (gatunek,))
            db.commit()

    # DODAJ GATUNKI DO KSIĄŻKI ##################### noqa: E266
    cur.execute('SELECT ksiazka_id FROM Ksiazka WHERE ksiazka_tytul = (?)',
                (k.tytul,))
    ksiazka_id = cur.fetchall()[0][0]
    for gatunek in k.gatunek:
        cur.execute('SELECT gatunek_id FROM Gatunek WHERE gatunek_nazwa = (?)',
                    (gatunek,))
        gatunek_id = cur.fetchall()[0][0]
        cur.execute('INSERT INTO ksiazka_gatunek (ksiazka_id, gatunek_id) VALUES (?, ?)',
                    (ksiazka_id, gatunek_id))
        db.commit()

    # DODAJ TAGI ############################# noqa: E266
    for tag in k.tagi:
        # SPRAWDŹ CZY ISTNIEJE
        cur.execute('SELECT tag_id FROM Tag WHERE tag_nazwa = (?)',
                    (tag,))
        tag_id = cur.fetchall()
        # JEŚLI NIE ISTNIEJE TO DODAJ
        if len(tag_id) == 0:
            cur.execute('INSERT INTO Tag (tag_nazwa) VALUES (?)',
                        (tag,))
            db.commit()

    # DODAJ TAGI DO KSIĄŻKI ######################## noqa: E266
    cur.execute('SELECT ksiazka_id FROM Ksiazka WHERE ksiazka_tytul = (?)',
                (k.tytul,))
    ksiazka_id = cur.fetchall()[0][0]
    for tag in k.tagi:
        cur.execute('SELECT tag_id FROM Tag WHERE tag_nazwa = (?)',
                    (tag,))
        tag_id = cur.fetchall()[0][0]
        cur.execute('INSERT INTO ksiazka_tag (ksiazka_id, tag_id) VALUES (?, ?)',
                    (ksiazka_id, tag_id))
        db.commit()
    db.commit()


@app.route("/add", methods=["GET", "POST"])
def addBook():
    """
    Handles the 'add' route for adding a new book to the database.

    Methods:
        GET: Renders the page for adding a new book.
        POST: Processes the form submission to add the book to the database.

    Returns:
        redirect: Redirects to the 'index' route after successfully adding the book.

    Usage:
        Access this route to add a new book by submitting the corresponding form.
    """
    if request.method == 'POST':
        k = parse_request(request)
        insert_book(k)

    return redirect(url_for('index'))


@app.route('/')
def index():
    """
    Renders the main page displaying information about books and their authors.

    Returns:
        render_template: Renders the 'base.html' template with the book and author data.

    Usage:
        Access this route to view the main page with information about books and their authors.
    """
    cur = get_cursor()
    cur.execute('select ks.*, au.* from ksiazka as ks LEFT join ksiazka_autor as ka on ka.ksiazka_id = ks.ksiazka_id left join autor as au on au.autor_id = ka.autor_id')
    data = cur.fetchall()
    return render_template("base.html", data=data)


@app.teardown_appcontext
def close_connection(exception):
    """
    Closes the database connection when the application context is torn down.

    Args:
        exception (Exception): An exception that might have occurred during the application context tear down.

    Usage:
        This function is automatically called by Flask when the application context is torn down.
        It ensures that the database connection is properly closed to prevent resource leaks.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
