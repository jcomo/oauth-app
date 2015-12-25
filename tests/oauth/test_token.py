from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app.oauth.models import OAuthApplication, OAuthGrant, OAuthToken
from app.identity.models import User


class OAuthTokenTestCase(TestCase, AuthTestMixin):
    def setUp(self):
        super(OAuthTokenTestCase, self).setUp()
        developer = User.register('Joe Dev', 'jdev', 'cat')
        self.application = OAuthApplication(developer, 'Test App', 'http://example.com')

        self.user = User.register('Jonathan Como', 'jcomo', 'dog')

    def test_creates_access_token_with_valid_grant(self):
        grant = OAuthGrant(self.user, self.application, ['read_public_profile'])
        grant_data = {
            'grant_type': 'authorization_code',
            'client_id': self.application.client_id,
            'redirect_uri': grant.redirect_uri,
            'code': grant.code,
        }

        response = self.client.post(url_for('oauth.token'), data=grant_data)
        self.assert200(response)

        token_data = response.json
        token = OAuthToken.by_access_token(token_data['access_token'])
        self.assertIsNotNone(token)

        self.assertEqual(token_data['access_token'], token.access_token)
        self.assertEqual(token_data['refresh_token'], token.refresh_token)
        self.assertEqual(token_data['scopes'], 'read_public_profile')

    def test_responds_with_error_when_code_does_not_exist(self):
        pass

    def test_responds_with_error_when_no_application_for_client_id(self):
        pass

    def test_responds_with_error_when_redirect_uri_does_not_match_grant(self):
        pass

    def test_responds_with_error_when_invalid_parameters(self):
        pass
