from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
@app.route('/higlass')
def higlass():
    return render_template("higlass.html")