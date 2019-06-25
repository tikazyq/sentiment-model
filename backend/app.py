import os
import sys

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from routes.model import ModelApi
from routes.news import NewsApi

file_dir = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(file_dir, '.'))
sys.path.append(root_path)

import config
import scheduler

# flask app instance
app = Flask(__name__)
app.config.from_object('config')

# init flask api instance
api = Api(app)

# cors support
CORS(app, supports_credentials=True)

api.add_resource(
    NewsApi,
    '/news',
    '/news/<int:id>'
)
api.add_resource(
    ModelApi,
    '/model',
    '/model/<string:action>'
)

if __name__ == '__main__':
    # run app instance
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, threaded=True)
