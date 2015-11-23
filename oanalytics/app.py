from flask import Flask

from oanalytics.analytics import analytics
from oanalytics.oauth import oauth


app = Flask(__name__)
app.register_blueprint(oauth, url_prefix='/oauth')
app.register_blueprint(analytics, url_prefix='/analytics')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
