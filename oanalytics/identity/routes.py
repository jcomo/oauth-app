from flask import Blueprint, render_template, redirect, url_for

from oanalytics.identity.models import User

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo


class UserRegistrationForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])


identity = Blueprint('identity', __name__)


@identity.route('/login')
def login():
    return ""


@identity.route('/logout')
def logout():
    return ""


@identity.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        name = form.data['name']
        username = form.data['username']
        password = form.data['password'].encode('utf-8')

        User.register(name, username, password)

        return redirect(url_for('analytics.apps'))

    return render_template('identity/register.html', form=form)
