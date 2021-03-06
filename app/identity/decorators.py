from functools import wraps

from flask import request, redirect, url_for

from app import sessions
from app.identity.models import User
from app.identity.session import SUGGESTED_KEY as SESSION_ID


def _retrieve_user():
    session_id = request.cookies.get(SESSION_ID)
    user_id = sessions.retrieve(session_id)
    if user_id:
        return User.query.get(user_id)


def authorize_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = _retrieve_user()
        if not user:
            return redirect(url_for('identity.login', next=request.url))

        kwargs['user'] = user
        return f(*args, **kwargs)
    return wrapper


def retrieve_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs['user'] = _retrieve_user()
        return f(*args, **kwargs)
    return wrapper
