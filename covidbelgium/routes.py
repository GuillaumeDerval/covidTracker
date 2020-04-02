from flask import render_template, send_from_directory, request, redirect, Response, abort, Blueprint, g, url_for
from flask_babel import gettext

from covidbelgium import get_locale
from covidbelgium.database import db_session
from covidbelgium.models import Answers, Sex, LikelyScale
from datetime import date, datetime

from covidbelgium.passwords import gen_password, hash_password, check_password

multilingual = Blueprint('multilingual', __name__, template_folder='templates', url_prefix='/<lang>')


@multilingual.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang', g.locale)


@multilingual.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.locale = values.pop('lang')


@multilingual.before_request
def before_request():
    get_locale()
    if g.locale not in ["fr", "en", "nl", "de"]:
        abort(404)


def get_password_list():
    """ List previously-used passwords from the cookie """
    pwds = request.cookies.get('passwords', None)
    if pwds is None:
        return []
    return pwds.split("/")


def add_password_to_list(response: Response, password: str):
    """ Takes a response object, and update the cookie for the password with the new password. """
    pwds = get_password_list()
    if password not in pwds:
        pwds = [password] + pwds
    response.set_cookie('passwords', "/".join(pwds))


def parse_date(string):
    """ Parses a date, in multiple possible formats %d/%m/%Y and %Y-%m-%d. """
    try:
        return datetime.strptime(string, '%d/%m/%Y').date()
    except:
        return datetime.strptime(string, '%Y-%m-%d').date()


@multilingual.route('/')
@multilingual.route('/index')
def index(error=False):
    passwords = get_password_list()
    passwords = passwords[:15]  # max 15 profiles listed.
    entries = {pwd: Answers.find_last_by_hash(hash_password(pwd)) for pwd in passwords}
    entries = {pwd: entry for pwd, entry in entries.items() if entry is not None}
    return render_template('index.html', entries=entries)


@multilingual.route('/index-error')
def index_error():
    return index(True)


@multilingual.route("/new-id")
def new_id():
    locale = str(get_locale())
    new_password = gen_password(locale)
    resp = redirect(url_for('multilingual.form'), 302)
    resp.set_cookie('cur_pass', new_password)
    return resp


@multilingual.route("/reuse-id", methods=["GET", "POST"])
def reuse_id():
    password = request.form.get("password", "")
    if check_password(password) and Answers.find_last_by_hash(hash_password(password)) is not None:
        resp = redirect(url_for('multilingual.form'), 302)
        resp.set_cookie('cur_pass', password)
        add_password_to_list(resp, password)
        return resp
    else:
        return render_template('reuse-id.html', password=password)


@multilingual.route("/form", methods=["GET", "POST"])
def form():
    password = request.cookies.get("cur_pass")
    if password is None:
        return redirect(url_for('multilingual.index_error'), 302)
    if request.method == "GET":  # Serve the form
        return render_template('form.html', password=password)
    else:  # Save in db and serve next form
        errors = []

        def check_form(f, error_msg, additional_check=lambda x: True):
            try:
                v = f()
                if not additional_check(v):
                    raise Exception()
                return v
            except:
                errors.append(error_msg)
                return None

        sex = check_form(lambda: Sex[request.values['sex']], gettext("Please fill in your sex"))
        age = check_form(lambda: int(request.values['age']), gettext("Please fill in your age"), lambda x: x % 5 == 0 and x <= 120)
        municipality = check_form(lambda: int(request.values['municipality']), gettext("Please fill in your municipality"))

        symptom_list = ["vomit", "nose", "fever", "smell", "breathing", "tiredness", "caugh", "shivers",
                        "headache", "muscle", "throat", "diarrhea"]  # order is important
        symptoms = [request.values.get(f'symptoms_{x}') is not None for x in symptom_list]

        covid_likely = check_form(lambda: LikelyScale[request.values['status']], gettext("Please select your status w.r.t Covid-19."))
        if covid_likely != LikelyScale.extremely_unlikely:
            covid_start = check_form(lambda: parse_date(request.values.get("timing_from")), gettext("Invalid date format. Please enter it as dd/mm/yyyy, like 20/03/2019."))
            covid_end = check_form(lambda: parse_date(request.values.get("timing_to")), gettext("Invalid date format. Please enter it as dd/mm/yyyy, like 20/03/2019."))

            if covid_start is not None and covid_end is not None and covid_start > covid_end:
                errors.append(gettext('Invalid dates, you should fall ill before being cared.'))
            if covid_start is not None and (covid_start < date(2019, 12, 1) or covid_start > date.today()):
                errors.append(gettext('Invalid start of symptoms date.'))
            if not any(symptoms):
                errors.append(gettext('If you think you are/were ill, please select the symptoms you faced. If you did not experience any of them, it is extremely unlikely you had covid-19.'))
        else:
            covid_start = covid_end = None
            if any(symptoms):
                errors.append(gettext("If you had some symptoms, it is not extremely unlikely that you had Covid-19."))

        if len(errors) == 0:
            if covid_end is not None and covid_end > date.today():
                covid_end = date(2030, 1, 1)  # far in the future, but every entry has the same date.

            answer = Answers(hash_password(password), covid_likely, sex, age, municipality, covid_start, covid_end, *symptoms)
            db_session.add(answer)
            db_session.commit()
            return render_template('form_distancing.html', password=password)
        else:
            return render_template('form.html', password=password, errors=errors, current={
                "sex": sex, "age": age, "symptoms": {n:v for n,v in zip(symptom_list, symptoms)},
                "covid_likely": covid_likely, "covid_start": covid_start, "covid_end": covid_end
            })


@multilingual.route("/social-distancing-form")
def social_distancing_form():
    password = request.cookies.get("cur_pass")
    if password is None:
        return redirect(url_for('multilingual.index_error'), 302)
    return render_template('form_distancing.html', password=password)

    # let's do this at the end of the form instead.
    # passwords = request.cookies.get('passwords')
    # if passwords is not None:
    #     passwords = passwords.split("/")
    # else:
    #     passwords = []
    # passwords.append(new_password)
