from flask import Blueprint

oauth = Blueprint('oauth', __name__, template_folder='templates')


@oauth.route('/register', methods=['GET', 'POST'])
def oauth_register():
    return "Registered"


@oauth.route('/applications/<int:application_id>')
def oauth_application(application_id):
    print application_id
    return str(application_id)
