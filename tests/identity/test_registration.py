from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app.identity.models import User
from app.identity.routes import sessions


class UserRegistrationTestCase(TestCase, AuthTestMixin):
    def test_renders_registration_form(self):
        response = self.client.get(url_for('identity.register'))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>Register</title>", html)
        self.assertIn("New User", html)
        self.assertIn("Name", html)
        self.assertIn("Username", html)
        self.assertIn("Password", html)
        self.assertIn("Confirm Password", html)

    def test_user_successfully_registers(self):
        data = {
            'name': 'Jonathan Como',
            'username': 'jcomo',
            'password': 'dog',
            'confirm': 'dog'
        }
        response = self.client.post(url_for('identity.register'), data=data)

        self.assertRedirects(response, url_for('analytics.apps'))

        user = User.by_username('jcomo')
        self.assertIsNotNone(user)

        session_id = self.get_cookie('session_id')
        self.assertIsNotNone(sessions.retrieve(session_id))

    def test_when_user_fails_to_register_does_not_redirect(self):
        data = {
            'name': 'Jonathan Como',
            'username': 'jcomo',
            'password': 'dog',
            'confirm': 'cat'
        }
        response = self.client.post(url_for('identity.register'), data=data)

        self.assertIn("<title>Register</title>", response.data)
        self.assertEqual(0, User.query.count())
        self.assertIsNone(self.get_cookie('session_id'))

    def test_redirects_when_already_registered(self):
        user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(user)

        response = self.client.get(url_for('identity.register'))

        self.assertRedirects(response, url_for('analytics.apps'))
