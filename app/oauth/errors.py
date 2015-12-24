from flask import jsonify


def view_oauth_error(e):
    response = jsonify({'error': e.reason})
    response.status_code = e.status_code
    return response


class OAuthError(Exception):
    status_code = 400
    reason = None


class InvalidRequest(OAuthError):
    reason = 'invalid_request'


class InvalidClient(OAuthError):
    status_code = 401
    reason = 'invalid_client'


class InvalidScopes(OAuthError):
    reason = 'invalid_scopes'
