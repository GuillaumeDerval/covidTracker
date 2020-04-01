from flask import Flask, request, g, Blueprint, abort, redirect, url_for
from flask_babel import Babel
from flask_babel import gettext, ngettext
from covidbelgium.config import Config


app = Flask(__name__, static_url_path='/static',
            static_folder='static')
app.config.from_object(Config)
babel = Babel(app)

@babel.localeselector
def get_locale():
    if not g.get('locale', None):
        translations = [str(translation) for translation in babel.list_translations()]
        g.locale = request.accept_languages.best_match(translations)
    return g.locale


from covidbelgium import routes
from covidbelgium.routes import multilingual
from covidbelgium.database import db_session
from covidbelgium import belgium_map

app.register_blueprint(multilingual)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.before_request
def before_request():
    get_locale()


@app.route('/')
def home():
    return redirect(url_for('multilingual.index'))


