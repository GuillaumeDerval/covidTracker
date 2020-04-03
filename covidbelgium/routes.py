from flask import render_template, send_from_directory, request, redirect, Response, abort, Blueprint, g, url_for, session, current_app
from flask_babel import gettext

from covidbelgium import get_locale
from covidbelgium.database import db_session
from covidbelgium.models import Answers, Sex, LikelyScale
from datetime import date, datetime, timedelta

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
    return session.get('passwords', [])


def add_password_to_list(password: str):
    """ Takes a response object, and update the cookie for the password with the new password. """
    pwds = get_password_list()
    if password not in pwds:
        pwds = [password] + pwds
    session["passwords"] = pwds


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
    session["cur_pass"] = gen_password(locale)
    resp = redirect(url_for('multilingual.form'), 302)
    return resp


@multilingual.route("/reuse-id", methods=["GET", "POST"])
def reuse_id():
    password = request.form.get("password", "")
    if check_password(password) and Answers.find_last_by_hash(hash_password(password)) is not None:
        add_password_to_list(password)
        session["cur_pass"] = password
        return redirect(url_for('multilingual.form'), 302)
    else:
        return render_template('reuse-id.html', password=password)


@multilingual.route("/form", methods=["GET", "POST"])
def form():
    password = session.get("cur_pass")
    if password is None:
        return redirect(url_for('multilingual.index_error'), 302)

    if request.method == "GET":  # Serve the form
        session["form_opened"] = datetime.utcnow()
        return render_template('form.html', password=password)
    else:  # Save in db and serve next form

        # "session expired"
        if session.get("form_opened") is not None and datetime.utcnow() - session.get("form_opened") > timedelta(hours=1):
            return redirect(url_for('multilingual.index_error'), 302)

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

            # now it's time to check if the remote person was not a robot. If this is the case, we silently ignore
            # its submission.
            is_robot = False
            if request.values.get('c-1', '') != '':
                current_app.logger.info('Robot filled the c-1 variable')
                is_robot = True
            if request.values.get('c-2', '') != password.split("-")[0]:
                current_app.logger.info('Robot filled the c-2 variable incorrectly')
                is_robot = True
            if session.get("form_opened") is None or datetime.utcnow() - session.get("form_opened") < timedelta(seconds=4):
                current_app.logger.info('Robot filled the form a bit too fast %s', str(datetime.utcnow() - session.get("form_opened")))
                is_robot = True
            # TODO IP check

            if not is_robot:
                answer = Answers(hash_password(password), covid_likely, sex, age, municipality, covid_start, covid_end, *symptoms)
                db_session.add(answer)
                db_session.commit()

            # You can submit only once :-)
            session["form_opened"] = None

            return render_template('form_distancing.html', password=password)
        else:
            return render_template('form.html', password=password, errors=errors, current={
                "sex": sex, "age": age, "symptoms": {n:v for n,v in zip(symptom_list, symptoms)},
                "covid_likely": covid_likely, "covid_start": covid_start, "covid_end": covid_end,
                "municipality": municipality
            })


@multilingual.route("/social-distancing-form")
def social_distancing_form():
    password = session.get("cur_pass")
    if password is None:
        return redirect(url_for('multilingual.index_error'), 302)

    return render_template('form_distancing.html', password=password)
