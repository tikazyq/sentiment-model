import os
import sys

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
import tushare as ts
from pymongo import DESCENDING

from db import db_manager
from routes.model import ModelApi
from routes.news import NewsApi
from routes.stats import StatsApi
from routes.stock import StockApi, StockSimpleApi, StockIndexSimpleApi, StockDailySimpleApi

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

# set tushare token
ts.set_token(config.TUSHARE_TOKEN)

api.add_resource(
    NewsApi,
    '/news',
    '/news/<string:id>'
)
api.add_resource(
    ModelApi,
    '/model',
    '/model/<string:action>'
)
api.add_resource(
    StockApi,
    '/stock',
    '/stock/<string:action>'
)
api.add_resource(
    StockSimpleApi,
    '/stocks',
    '/stocks/<string:id>'
)
api.add_resource(
    StockIndexSimpleApi,
    '/stock_indexes',
    '/stock_indexes/<string:id>'
)
api.add_resource(
    StockDailySimpleApi,
    '/stock_daily'
)
api.add_resource(
    StatsApi,
    '/stats/<string:action>'
)

# create indexes
db_manager.create_index('stock_news', keys=[('ts', DESCENDING)])

if __name__ == '__main__':
    # run app instance
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, threaded=True)
