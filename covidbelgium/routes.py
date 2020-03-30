from flask import render_template, send_from_directory, request, redirect, Response

from covidbelgium import app, get_locale
from covidbelgium.database import db_session
from covidbelgium.models import Answers, Sex
import datetime

from covidbelgium.passwords import gen_password, hash_password, check_password


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


@app.route('/')
@app.route('/index')
def index(error=False):
    a = Answers("b67d51c9e670a678ce0e4c1d973d1b05400e174d3207d8ae4e37db9109300bba", True, False, Sex.male, 5, datetime.datetime.utcnow(), datetime.datetime.utcnow())
    db_session.add(a)
    db_session.commit()
    passwords = get_password_list()
    passwords = passwords[:15]  # max 15 profiles listed.
    entries = {pwd: Answers.find_last_by_hash(hash_password(pwd)) for pwd in passwords}
    entries = {pwd: entry for pwd, entry in entries.items() if entry is not None}
    return render_template('index.html', entries=entries)


@app.route('/index-error')
def index_error():
    return index(True)


@app.route("/new-id")
def new_id():
    locale = str(get_locale())
    new_password = gen_password(locale)
    resp = redirect("/form", 302)
    resp.set_cookie('cur_pass', new_password)
    return resp


@app.route("/reuse-id", methods=["GET", "POST"])
def reuse_id():
    password = request.form.get("password", "")
    if check_password(password) and Answers.find_last_by_hash(hash_password(password)) is not None:
        resp = redirect("/form", 302)
        resp.set_cookie('cur_pass', password)
        add_password_to_list(resp, password)
        return resp
    else:
        return render_template('reuse-id.html', password=password)


@app.route("/form")
def form():
    password = request.cookies.get("cur_pass")
    if password is None:
        return redirect("/index-error", 302)
    return render_template('form.html', password=password)

@app.route("/social-distancing-form")
def social_distancing_form():
    password = request.cookies.get("cur_pass")
    if password is None:
        return redirect("/index-error", 302)
    return render_template('form_distancing.html', password=password)

    # let's do this at the end of the form instead.
    # passwords = request.cookies.get('passwords')
    # if passwords is not None:
    #     passwords = passwords.split("/")
    # else:
    #     passwords = []
    # passwords.append(new_password)
