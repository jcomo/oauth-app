from flask import url_for

from app.identity.routes import sessions


class AuthTestMixin(object):
    def tearDown(self):
        print 'tearing down'
        sessions.clear()

    def login_as(self, user):
        session_id = sessions.create(user)
        self.client.set_cookie('localhost', 'session_id', session_id)
        return session_id

    def assertUnauthenticatedCannotAccess(self, endpoint, **kwargs):
        self.client.get(url_for('identity.logout'))
        url = url_for(endpoint, **kwargs)
        response = self.client.get(url)
        next_url = url_for(endpoint, _external=True, **kwargs)
        self.assertRedirects(response, url_for('identity.login', next=next_url))
