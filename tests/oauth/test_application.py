from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app import db
from app.oauth.models import OAuthApplication
from app.identity.models import User


class OAuthApplicationTestCase(TestCase, AuthTestMixin):
    def setUp(self):
        super(OAuthApplicationTestCase, self).setUp()
        developer = User.register('Joe Dev', 'jdev', 'cat')
        self.application = OAuthApplication(developer, 'Test App', 'http://example.com')
        db.session.add(self.application)
        db.session.commit()

        self.login_as(developer)

    def test_non_logged_in_user_cannot_view_application(self):
        self.assertUnauthenticatedCannotAccess('oauth.application', application_id=self.application.id)

    def test_only_owner_can_view_application(self):
        user = User.register('Someone', 'someone', 'dog')
        self.login_as(user)

        response = self.client.get(url_for('oauth.application', application_id=self.application.id))
        self.assert404(response)

    def test_not_found_when_no_application_exists(self):
        response = self.client.get(url_for('oauth.application', application_id=123))
        self.assert404(response)

    def test_renders_view_with_application_information(self):
        response = self.client.get(url_for('oauth.application', application_id=self.application.id))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>Test App</title>", html)
        self.assertIn("<h1>Test App</h1>", html)
        self.assertIn(self.application.client_id, html)
        self.assertIn(self.application.redirect_uri, html)
