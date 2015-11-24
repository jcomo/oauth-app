from flask import Blueprint, request, render_template, redirect, url_for, g

from oanalytics.identity.models import User
from oanalytics.identity.forms import UserLoginForm, UserRegistrationForm
from oanalytics.identity.session import SessionStore

identity = Blueprint('identity', __name__)

sessions = SessionStore()
_SESSION_ID = 'session_id'


def _login_user(user, redirect_url):
    session_id = sessions.create(user)
    response = redirect(redirect_url)
    response.set_cookie(_SESSION_ID, session_id)
    return response


@identity.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.data['username']
        password = form.data['password']

        user = User.login(username, password)
        if user:
            return _login_user(user, url_for('analytics.apps'))

    return render_template('identity/login.html', form=form)


@identity.route('/logout')
def logout():
    session_id = request.cookies.get(_SESSION_ID)
    sessions.remove(session_id)
    response = redirect(url_for('identity.login'))
    response.set_cookie(_SESSION_ID, '')
    return response


@identity.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        name = form.data['name']
        username = form.data['username']
        password = form.data['password']

        new_user = User.register(name, username, password)
        return _login_user(new_user, url_for('analytics.apps'))

    return render_template('identity/register.html', form=form)
