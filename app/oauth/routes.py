from flask import Blueprint, request, render_template, redirect, url_for, abort, jsonify

from app import db
from app.identity.routes import authorize_session
from app.oauth import errors
from app.oauth.forms import OAuthApplicationForm, OAuthGrantForm
from app.oauth.models import OAuthApplication, OAuthGrant, OAuthToken, friendly_scopes, scopes_valid

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

    form = OAuthGrantForm(client_id=application.client_id, scope=' '.join(scopes))
    return render_template('oauth/authorize.html', application=application, form=form, scopes=friendly_scopes(scopes))


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


@oauth.route('/token', methods=['POST'])
def token():
    _validate_grant_type_using(request.form)
    _retrieve_oauth_application_using(request.form)

    grant = _retrieve_grant_using(request.form)
    if grant.redirect_uri != request.form.get('redirect_uri'):
        raise errors.InvalidClient

    token = OAuthToken(grant)

    db.session.add(token)
    db.session.commit()

    return jsonify({
        'access_token': token.access_token,
        'refresh_token': token.refresh_token,
        'expires_at': None,
        'scope': token.scopes,
    })


def _retrieve_oauth_application_using(source):
    client_id = source.get('client_id') or ''
    application = OAuthApplication.by_client_id(client_id)
    if not application:
        raise errors.InvalidClient

    return application


def _retrieve_grant_using(source):
    grant_code = source.get('code') or ''
    grant = OAuthGrant.by_code(grant_code)
    if not grant:
        raise errors.InvalidGrant

    return grant


def _retrieve_scopes_using(source):
    raw_scopes = source.get('scope') or ''
    scopes = raw_scopes.split(' ')
    if not scopes_valid(scopes):
        raise errors.InvalidScope

    return scopes


def _validate_response_type_using(source):
    if source.get('response_type') != 'code':
        raise errors.InvalidRequest


def _validate_grant_type_using(source):
    if source.get('grant_type') != 'authorization_code':
        raise errors.InvalidRequest
