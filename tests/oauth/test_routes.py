from flask import url_for

from tests.test_case import TestCase

from oanalytics.oauth.models import OAuthApplication


class OAuthRegistrationTestCase(TestCase):
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

    def test_registration_successful_redirects_to_application_page(self):
        data = {'name': 'OAuth application', 'redirect_uri': 'http://example.com'}
        response = self.client.post(url_for('oauth.register'), data=data)

        application = OAuthApplication.query.first()
        self.assertRedirects(response, url_for('oauth.application', application_id=application.id))


class OAuthApplicationTestCase(TestCase):
    pass
