from flask import Blueprint, request, render_template, redirect, url_for, abort

from app import db
from app.identity.routes import authorize_session
from app.oauth import errors
from app.oauth.forms import OAuthApplicationForm, OAuthGrantForm
from app.oauth.models import OAuthApplication, OAuthGrant, friendly_scopes, scopes_valid

oauth = Blueprint('oauth', __name__)
oauth.errorhandler(errors.OAuthError)(errors.view_oauth_error)


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
def application(user, application_id):
    application = OAuthApplication.by_id(user, application_id)
    if not application:
        abort(404)

    return render_template('oauth/application.html', application=application)


@oauth.route('/authorize', methods=['GET', 'POST'])
@authorize_session
def authorize(user):
    if request.method == 'GET':
        return _ask_for_authorization()
    else:
        return _grant_authorization(user)


def _ask_for_authorization():
    _validate_response_type_using(request.args)
    application = _retrieve_oauth_application_using(request.args)
    scopes = _retrieve_scopes_using(request.args)
    if not scopes:
        scopes = ['read_public_profile']

    return render_template('oauth/authorize.html', application=application, scopes=friendly_scopes(scopes))


def _grant_authorization(user):
    form = OAuthGrantForm()
    if not form.validate_on_submit():
        raise errors.InvalidRequest

    _validate_response_type_using(form.data)
    application = _retrieve_oauth_application_using(form.data)
    scopes = _retrieve_scopes_using(form.data)

    grant = OAuthGrant(user, application, scopes)
    db.session.add(grant)
    db.session.commit()

    return redirect(application.redirect_uri + '?code=' + grant.code)


def _retrieve_oauth_application_using(source):
    client_id = source.get('client_id') or ''
    application = OAuthApplication.by_client_id(client_id)
    if not application:
        raise errors.InvalidClient

    return application


def _retrieve_scopes_using(source):
    raw_scopes = source.get('scopes') or ''
    scopes = raw_scopes.split(' ')
    if not scopes_valid(scopes):
        raise errors.InvalidScopes

    return scopes


def _validate_response_type_using(source):
    if source.get('response_type') != 'code':
        raise errors.InvalidRequest
