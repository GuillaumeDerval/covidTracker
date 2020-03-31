from flask import Flask, request, g
from flask_babel import Babel
from flask_babel import gettext, ngettext
from covidbelgium.config import Config

app = Flask(__name__, static_url_path='/static',
            static_folder='static')
app.config.from_object(Config)
babel = Babel(app)

@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]
    return request.accept_languages.best_match(translations)


from covidbelgium import routes
from covidbelgium.database import db_session
from covidbelgium import belgium_map


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.before_request
def before_request():
    g.locale = str(get_locale())
