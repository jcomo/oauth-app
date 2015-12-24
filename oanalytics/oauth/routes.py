from flask import Blueprint, request, render_template, redirect, url_for

from oanalytics.app import db
from oanalytics.identity.routes import authorize_session
from oanalytics.oauth.forms import OAuthApplicationForm, OAuthGrantForm
from oanalytics.oauth.models import OAuthApplication, OAuthGrant, friendly_scopes, scopes_valid

oauth = Blueprint('oauth', __name__)


@oauth.route('/register', methods=['GET', 'POST'])
@authorize_session
def register(user):
    form = OAuthApplicationForm()
    if form.validate_on_submit():
        name = form.data['name']
        redirect_uri = form.data['redirect_uri']
        icon_url = form.data['icon_url']
        website_url = form.data['website_url']

        application = OAuthApplication(user, name, redirect_uri,
                                       icon_url=icon_url, website_url=website_url)

        db.session.add(application)
        db.session.commit()

        return redirect(url_for('oauth.application', application_id=application.id))

    return render_template('oauth/register.html', form=form)


@oauth.route('/applications/<int:application_id>')
@authorize_session
def application(application_id):
    return str(application_id)


@oauth.route('/authorize', methods=['GET', 'POST'])
@authorize_session
def authorize(user):
    if request.method == 'GET':
        return _ask_for_authorization()
    else:
        return _grant_authorization(user)


def _ask_for_authorization():
    application = _retrieve_oauth_application_using(request.args)
    scopes = _retrieve_scopes_using(request.args)

    return render_template('oauth/authorize.html', application=application, scopes=friendly_scopes(scopes))


def _grant_authorization(user):
    form = OAuthGrantForm()
    if form.validate_on_submit():
        application = _retrieve_oauth_application_using(form.data)
        scopes = _retrieve_scopes_using(form.data)

        grant = OAuthGrant(user, application, scopes)
        db.session.add(grant)
        db.session.commit()

        return redirect(application.redirect_uri + '?code=' + grant.code)

    return ""


def _retrieve_oauth_application_using(source):
    client_id = source.get('client_id') or ''
    return OAuthApplication.by_client_id(client_id)


def _retrieve_scopes_using(source):
    scopes = source.get('scopes') or ''
    if scopes:
        return scopes.split(' ')
    else:
        return ['read_public_profile']

