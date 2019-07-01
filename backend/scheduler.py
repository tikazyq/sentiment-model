import json
import os

import joblib
import requests
from apscheduler.schedulers.background import BackgroundScheduler

import config
from db import db_manager

scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', minutes=5)
def train_model():
    print('training model...')
    r = requests.get(f'http://localhost:{config.FLASK_PORT}/model/train')
    print(f'response: {r.content.decode("utf-8")}')


@scheduler.scheduled_job('interval', minutes=5)
def predict_news():
    print('predicting news...')
    filename = os.path.join(config.MODEL_DIR, f'{config.MODEL_NAME}.pkl')
    clf = joblib.load(filename)
    filename_vec = os.path.join(config.MODEL_DIR, f'vec.pkl')
    vec = joblib.load(filename_vec)

    cls_list = [-1, 0, 1]
    for d in db_manager.list('results_xueqiu', {}, limit=999999):
        text = d.get('text')
        x = vec.transform([text])
        cls = clf.predict(x)[0]
        proba_list = clf.predict_proba(x)[0]
        idx = cls_list.index(cls)
        proba = proba_list[idx] / sum(proba_list)
        db_manager.update_one('results_xueqiu', d['_id'], {
            'class_pred': cls,
            'proba_pred': proba
        })


@scheduler.scheduled_job('interval', hours=1)
def update_stock_list():
    print('updating stock list...')
    r = requests.get(f'http://localhost:{config.FLASK_PORT}/stock/stock_basic')
    data = json.loads(r.content)
    for item in data['items']:
        item['_id'] = item['ts_code']
        db_manager.save(col_name='stocks', item=item)


@scheduler.scheduled_job('interval', hours=1)
def update_stock_index_list():
    print('updating stock index list...')
    market_list = [
        'MSCI',
        'CSI',
        'SSE',
        'SZSE',
        'CICC',
        'SW',
        'OTH',
    ]
    for market in market_list:
        r = requests.get(f'http://localhost:{config.FLASK_PORT}/stock/index_basic?market=' + market)
        data = json.loads(r.content)
        for item in data['items']:
            item['_id'] = item['ts_code']
            db_manager.save(col_name='stock_indexes', item=item)


@scheduler.scheduled_job('interval', minutes=5)
def update_news_stocks():
    print('updating news stocks...')
    stock_list = db_manager.list('stocks', {}, limit=999999)
    for item in db_manager.list('results_xueqiu', {'stocks': {'$exists': False}}, limit=999999):
        stocks = []
        for stock in stock_list:
            if stock['name'] in item['text']:
                stocks.append(stock['_id'])
        db_manager.update_one(col_name='results_xueqiu', id=item['_id'], values={
            'stocks': stocks
        })


scheduler.start()
