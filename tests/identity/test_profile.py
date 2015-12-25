from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app.identity.models import User
from app.identity.routes import sessions


class UserProfileTestCase(TestCase, AuthTestMixin):
    def test_non_logged_in_user_cannot_view(self):
        self.assertUnauthenticatedCannotAccess('identity.me')

    def test_displays_user_profile_information(self):
        user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(user)

        response = self.client.get(url_for('identity.me'))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>My Profile</title>", html)
        self.assertIn("Jonathan Como", html)
        self.assertIn("jcomo", html)
