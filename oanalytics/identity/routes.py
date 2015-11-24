from flask import Blueprint, request, render_template, redirect, url_for, g

from oanalytics.app import sessions
from oanalytics.identity.models import User
from oanalytics.identity.forms import UserLoginForm, UserRegistrationForm
from oanalytics.identity.session import SUGGESTED_KEY as SESSION_ID
from oanalytics.identity.decorators import authorize_session, retrieve_session

identity = Blueprint('identity', __name__)


def _login_user(user, redirect_url):
    session_id = sessions.create(user)
    response = redirect(redirect_url)
    response.set_cookie(SESSION_ID, session_id)
    return response


@identity.route('/register', methods=['GET', 'POST'])
@retrieve_session
def register(user):
    if user:
        return redirect(url_for('analytics.apps'))

    form = UserRegistrationForm()
    if form.validate_on_submit():
        name = form.data['name']
        username = form.data['username']
        password = form.data['password']

        new_user = User.register(name, username, password)
        return _login_user(new_user, url_for('analytics.apps'))

    return render_template('identity/register.html', form=form)


@identity.route('/login', methods=['GET', 'POST'])
@retrieve_session
def login(user):
    if user:
        return redirect(url_for('analytics.apps'))

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
    session_id = request.cookies.get(SESSION_ID)
    sessions.remove(session_id)
    response = redirect(url_for('identity.login'))
    response.set_cookie(SESSION_ID, '')
    return response
