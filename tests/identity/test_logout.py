from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app.identity.models import User
from app.identity.routes import sessions


class UserLogoutTestCase(TestCase, AuthTestMixin):
    def test_logging_out_destroys_session(self):
        user = User.register('Jonathan Como', 'jcomo', 'dog')
        session_id = self.login_as(user)

        response = self.client.get(url_for('identity.logout'))

        self.assertRedirects(response, url_for('identity.login'))
        self.assertIsNone(sessions.retrieve(session_id))
        self.assertEqual('', self.get_cookie('session_id'))

    def test_user_is_redirected_when_not_logged_in(self):
        response = self.client.get(url_for('identity.logout'))

        self.assertRedirects(response, url_for('identity.login'))
