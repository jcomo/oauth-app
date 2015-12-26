from flask_wtf import Form
from flask_wtf.html5 import URLField
from wtforms import StringField
from wtforms.validators import DataRequired


class OAuthApplicationForm(Form):
    name = StringField('Application Name', validators=[DataRequired()])
    redirect_uri = URLField('Redirect URI', validators=[DataRequired()])
    icon_url = URLField('Icon URL')
    website_url = URLField('Website URL')


class OAuthGrantForm(Form):
    response_type = StringField('Response Type', validators=[DataRequired()])
    client_id = StringField('Client ID', validators=[DataRequired()])
    scope = StringField('Scope', validators=[DataRequired()])
