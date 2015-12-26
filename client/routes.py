import urllib

# import requests
from flask import request, redirect, url_for

from client import app


def _oauth_authorize_url(params):
    root = app.config['OAUTH_BASE_URL'] + '/oauth/authorize'
    return root + '?' + urllib.urlencode(params)


@app.route('/')
def index():
    params = {
        'response_type': 'code',
        'client_id': app.config['APP_CLIENT_ID'],
        'redirect_uri': url_for('authorize', _external=True),
        'scopes': 'read_analytics read_public_profile',
    }

    return redirect(_oauth_authorize_url(params))


@app.route('/authorize')
def authorize():
    return request.data
