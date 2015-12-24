from flask import Blueprint, jsonify

from app.identity.routes import authorize_session

analytics = Blueprint('analytics', __name__)


@analytics.route('/apps')
@authorize_session
def apps():
    return jsonify({
        'installs': {
            '2015-11-23': 1285,
            '2015-11-22': 988,
            '2015-11-21': 2319,
        }
    })
