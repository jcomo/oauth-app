from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app.identity.models import User
from app.identity.routes import sessions


class UserLoginTestCase(TestCase, AuthTestMixin):
    def test_renders_login_form(self):
        response = self.client.get(url_for('identity.login'))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>Login</title>", html)
        self.assertIn("Welcome Back", html)
        self.assertIn("Username", html)
        self.assertIn("Password", html)

    def test_logs_in_when_credentials_match(self):
        User.register('Jonathan Como', 'jcomo', 'dog')
        data = {'username': 'jcomo', 'password': 'dog'}
        response = self.client.post(url_for('identity.login'), data=data)

        self.assertRedirects(response, url_for('analytics.apps'))

        session_id = self.get_cookie('session_id')
        self.assertIsNotNone(sessions.retrieve(session_id))

    def test_redirects_when_next_specified(self):
        User.register('Jonathan Como', 'jcomo', 'dog')
        data = {'username': 'jcomo', 'password': 'dog'}
        params = {'next': url_for('identity.logout')}

        response = self.client.post(url_for('identity.login'), data=data, query_string=params)

        self.assertRedirects(response, url_for('identity.logout'))

    def test_does_not_login_in_when_credentials_dont_match(self):
        User.register('Jonathan Como', 'jcomo', 'dog')
        data = {'username': 'jcomo', 'password': 'cat'}
        response = self.client.post(url_for('identity.login'), data=data)

        self.assertIn("<title>Login</title>", response.data)
        self.assertIsNone(self.get_cookie('session_id'))

    def test_redirects_when_already_registered(self):
        user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(user)

        response = self.client.get(url_for('identity.login'))

        self.assertRedirects(response, url_for('analytics.apps'))

