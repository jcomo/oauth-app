from flask import url_for

from tests.test_case import TestCase

from oanalytics.oauth.models import OAuthApplication
from oanalytics.identity.models import User


class OAuthRegistrationTestCase(TestCase):
    def setUp(self):
        super(OAuthRegistrationTestCase, self).setUp()
        self.user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(self.user)

    def test_non_logged_in_user_cannot_view_registration(self):
        self.client.get(url_for('identity.logout'))
        response = self.client.get(url_for('oauth.register'))
        next_url = url_for('oauth.register', _external=True)
        self.assertRedirects(response, url_for('identity.login', next=next_url))

    def test_non_logged_in_user_cannot_submit_registration(self):
        self.client.get(url_for('identity.logout'))
        response = self.client.post(url_for('oauth.register'))
        next_url = url_for('oauth.register', _external=True)
        self.assertRedirects(response, url_for('identity.login', next=next_url))

    def test_registration_form_display(self):
        response = self.client.get(url_for('oauth.register'))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>Register Application</title>", html)
        self.assertIn("Application Name", html)
        self.assertIn("Redirect URI", html)
        self.assertIn("Icon URL", html)
        self.assertIn("Website URL", html)

    def test_registration_failure_renders_form_display_with_errors(self):
        # TODO do we even care about errors in this POC?
        data = {'name': 'OAuth application'}
        response = self.client.post(url_for('oauth.register'), data=data)

        self.assertIn("<title>Register Application</title>", response.data)
        self.assertEqual(0, OAuthApplication.query.count())

    def test_registration_successful_redirects_to_application_page(self):
        data = {'name': 'OAuth application', 'redirect_uri': 'http://example.com'}
        response = self.client.post(url_for('oauth.register'), data=data)

        application = OAuthApplication.query.first()
        self.assertRedirects(response, url_for('oauth.application', application_id=application.id))


class OAuthApplicationTestCase(TestCase):
    pass
