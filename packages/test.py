from packages import app
from flask import render_template


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/about')
def about():
    return render_template('about.html')
