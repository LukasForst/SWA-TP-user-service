import logging
import sys
from importlib import util as importing

from flask import Flask
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from api.StatusApi import status_api
from api.VersionApi import version_api
from common.Config import get_config
from common.Db import db

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

# Create app
app = Flask(__name__)
# fix for https swagger - see https://github.com/python-restx/flask-restx/issues/58
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_port=1, x_for=1, x_host=1, x_prefix=1)

# Set up Swagger and API
authorizations = {
    'bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(app, authorizations=authorizations)

# Register namespaces

api.add_namespace(version_api, path='/')
api.add_namespace(status_api, path='/')

# Load configuration
config_file = 'config'
if importing.find_spec(config_file):
    app.config.from_object(config_file)

# connect to the database
with app.app_context():
    config = get_config()

app.config['SQLALCHEMY_DATABASE_URI'] \
    = f'postgresql+psycopg2://{config.postgres_user}:{config.postgres_password}@{config.postgres_url}/' \
      f'{config.postgres_db}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# App startup
if __name__ == '__main__':
    logger.info('Starting the application.')
    app.run(host="localhost", port=8080)
