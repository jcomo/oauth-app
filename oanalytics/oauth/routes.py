from flask import Blueprint, render_template, redirect, url_for

from oanalytics.app import db
from oanalytics.oauth.forms import OAuthApplicationForm
from oanalytics.oauth.models import OAuthApplication

oauth = Blueprint('oauth', __name__)


@oauth.route('/register', methods=['GET', 'POST'])
def register():
    form = OAuthApplicationForm()
    if form.validate_on_submit():
        name = form.data['name']
        redirect_uri = form.data['redirect_uri']
        icon_url = form.data['icon_url']
        website_url = form.data['website_url']

        application = OAuthApplication(name, redirect_uri,
                                       icon_url=icon_url, website_url=website_url)

        db.session.add(application)
        db.session.commit()

        return redirect(url_for('oauth.application', application_id=application.id))

    return render_template('oauth/register.html', form=form)


@oauth.route('/applications/<int:application_id>')
def application(application_id):
    return str(application_id)
