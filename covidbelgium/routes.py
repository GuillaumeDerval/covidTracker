from flask import render_template

from covidbelgium import app
from covidbelgium.database import db_session
from covidbelgium.models import Answers
import datetime

@app.route('/')
@app.route('/index')
def index():
    a = Answers("test", True, False, datetime.datetime.utcnow(), datetime.datetime.utcnow())
    db_session.add(a)
    db_session.commit()
    return render_template('form.html', text="test")