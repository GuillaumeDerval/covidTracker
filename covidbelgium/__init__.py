from flask import Flask, request
from flask_babel import Babel
from flask_babel import gettext, ngettext
from covidbelgium.config import Config

app = Flask(__name__)
app.config.from_object(Config)
babel = Babel(app)

@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]
    return request.accept_languages.best_match(translations)


from covidbelgium import routes
from covidbelgium.database import db_session


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

