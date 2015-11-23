from flask import Blueprint, jsonify

analytics = Blueprint('analytics', __name__)


@analytics.route('/apps')
def apps():
    return jsonify({
        'installs': {
            '2015-11-23': 1285,
            '2015-11-22': 988,
            '2015-11-21': 2319,
        }
    })
