import urllib

import requests
from flask import request, redirect, url_for, jsonify

from client import app


def _oauth_authorize_url(params):
    root = app.config['OAUTH_BASE_URL'] + '/oauth/authorize'
    return root + '?' + urllib.urlencode(params)


def _oauth_token_url():
    return app.config['OAUTH_BASE_URL'] + '/oauth/token'


@app.route('/')
def index():
    params = {
        'response_type': 'code',
        'client_id': app.config['APP_CLIENT_ID'],
        'scope': 'read_analytics read_public_profile',
    }

    return redirect(_oauth_authorize_url(params))


@app.route('/authorize')
def authorize():
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': app.config['APP_CLIENT_ID'],
        'redirect_uri': request.base_url,
        'code': request.args.get('code'),
    }

    response = requests.post(_oauth_token_url(), data=token_data)

    return jsonify(response.json())
