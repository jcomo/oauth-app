from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app import db
from app.oauth.models import OAuthApplication
from app.identity.models import User


class OAuthRegistrationTestCase(TestCase, AuthTestMixin):
    def setUp(self):
        super(OAuthRegistrationTestCase, self).setUp()
        self.user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(self.user)

    def test_non_logged_in_user_cannot_view_registration(self):
        self.assertUnauthenticatedCannotAccess('oauth.register')

    def test_non_logged_in_user_cannot_submit_registration(self):
        self.assertUnauthenticatedCannotAccess('oauth.register')

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


class OAuthGrantTestCase(TestCase, AuthTestMixin):
    def setUp(self):
        super(OAuthGrantTestCase, self).setUp()
        developer = User.register('Joe Dev', 'jdev', 'cat')
        self.application = OAuthApplication(developer, 'Test App', 'http://example.com')

        self.user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(self.user)

    def test_redirects_to_application_redirect_uri_when_scopes_accepted(self):
        grant_data = {'client_id': self.application.client_id, 'response_type': 'code', 'scopes': 'read_analytics'}
        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        grant = self.application.grants.first()
        self.assertIsNotNone(grant)
        self.assertEqual(grant.user, self.user)

        redirect_uri = 'http://example.com?code=' + grant.code
        self.assertIn(response.status_code, (301, 302))
        self.assertEqual(response.location, redirect_uri)

    def test_responds_with_error_when_no_application_for_client_id(self):
        grant_data = {'client_id': 'abc', 'response_type': 'code', 'scopes': 'read_public_profile'}
        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        self.assert401(response)
        self.assertEqual(response.json, {'error': 'invalid_client'})

    def test_responds_with_error_when_specified_scopes_are_invalid(self):
        grant_data = {
            'response_type': 'code',
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile|malicious_scope'
        }

        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_scopes'})

    def test_responds_with_error_when_missing_required_parameters(self):
        grant_data = {
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile'
        }

        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_request'})


class OAuthAuthorizationTestCase(TestCase, AuthTestMixin):
    def setUp(self):
        super(OAuthAuthorizationTestCase, self).setUp()
        self.developer = User.register('Joe Dev', 'jdev', 'cat')
        self.application = OAuthApplication(self.developer, 'Test App', 'http://example.com')

        user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(user)

    def test_redirects_resource_owner_to_login_when_not_logged_in(self):
        self.client.get(url_for('identity.logout'))
        query = {'client_id': 'abc', 'response_type': 'code'}
        response = self.client.get(url_for('oauth.authorize'), query_string=query)

        auth_url = url_for('oauth.authorize', client_id='abc', response_type='code', _external=True)
        self.assertRedirects(response, url_for('identity.login', next=auth_url))

    def test_prompts_resource_owner_for_scopes(self):
        auth_query = {'client_id': self.application.client_id, 'response_type': 'code', 'scopes': 'read_analytics'}
        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)
        self.assert200(response)

        html = response.data
        title = "<title>Authorize %s</title>" % self.application.name
        self.assertIn(title, html)
        self.assertIn("Read analytics data", html)

    def test_responds_with_error_when_no_application_for_client_id(self):
        auth_query = {'client_id': 'abc', 'response_type': 'code'}
        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)

        self.assert401(response)
        self.assertEqual(response.json, {'error': 'invalid_client'})

    def test_responds_with_error_when_specified_scopes_are_invalid(self):
        auth_query = {
            'response_type': 'code',
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile|malicious_scope'
        }

        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_scopes'})

    def test_responds_with_error_when_missing_required_parameters(self):
        auth_query = {
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile'
        }

        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_request'})


class OAuthTokenTestCase(TestCase, AuthTestMixin):
    from unittest import skip

    @skip('Make this correct')
    def test_responds_with_error_when_scopes_on_auth_do_not_match_grant_request(self):
        grant = OAuthGrant(self.user, self.application.client_id, 'read_public_profile')
        grant_data = {
            'response_type': 'code',
            'client_id': self.application.client_id,
            'scopes': 'read_analytics_data',
        }

        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_scopes'})
