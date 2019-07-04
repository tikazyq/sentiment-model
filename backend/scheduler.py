import json
import os

import joblib
import requests
from apscheduler.schedulers.background import BackgroundScheduler

import config
from db import db_manager

scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', minutes=10)
def train_model():
    print('training model...')
    r = requests.get(f'http://{config.FLASK_HOST}:{config.FLASK_PORT}/model/train')
    print(f'response: {r.content.decode("utf-8")}')


@scheduler.scheduled_job('interval', seconds=10)
def predict_news():
    print('predicting news...')
    filename = os.path.join(config.MODEL_DIR, f'{config.MODEL_NAME}.pkl')
    clf = joblib.load(filename)
    filename_vec = os.path.join(config.MODEL_DIR, f'vec.pkl')
    vec = joblib.load(filename_vec)

    col = db_manager.db['stock_news']
    query = {'class': {'$exists': False}, 'class_pred': {'$exists': False}}
    count = col.count(query)

    if count == 0:
        return

    batch_size = 1000

    txt = []
    news_list = []
    for i, d in enumerate(col.find(query).limit(batch_size)):
        if (i % 100 == 0 and i > 0) or i - 1 == batch_size:
            print(f'{i}/{batch_size}')
        text = d.get('text')
        txt.append(text)
        news_list.append(d)

    X = vec.transform(txt)
    cls_list = clf.predict(X)
    # proba = clf.predict_proba(X)
    # idx = cls_list.index(cls)
    # proba = proba / proba.sum(axis=1)
    i = 0
    for d, cls in zip(news_list, cls_list):
        if (i % 100 == 0 and i > 0) or i - 1 == batch_size:
            print(f'{i}/{1000}')
        db_manager.update_one('stock_news', d['_id'], {
            'class_pred': cls
            # 'proba_list': p
        })
        i += 1
    print('predicting news complete')


@scheduler.scheduled_job('interval', hours=1)
def update_stock_list():
    print('updating stock list...')
    r = requests.get(f'http://{config.FLASK_HOST}:{config.FLASK_PORT}/stock/stock_basic')
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
        r = requests.get(f'http://{config.FLASK_HOST}:{config.FLASK_PORT}/stock/index_basic?market=' + market)
        data = json.loads(r.content)
        for item in data['items']:
            item['_id'] = item['ts_code']
            db_manager.save(col_name='stock_indexes', item=item)


@scheduler.scheduled_job('interval', minutes=5)
def update_news_stocks():
    print('updating news stocks...')
    # 只更新雪球网
    stock_list = db_manager.list('stocks', {}, limit=999999)
    for item in db_manager.list('stock_news', {'stocks': {'$exists': False}}, limit=999999):
        stocks = []
        for stock in stock_list:
            if stock['name'] in item['text']:
                stocks.append(stock['_id'])
        db_manager.update_one(col_name='stock_news', id=item['_id'], values={
            'stocks': stocks
        })


@scheduler.scheduled_job('interval', minutes=10)
def update_news_class():
    print('updating news class...')
    col = db_manager.db['stock_news']
    cls_list = [-1, 0, 1]
    for cls in cls_list:
        col.update_many(
            {'class': cls},
            {'$set': {'class_final': cls}}
        )
        col.update_many(
            {'class': {'$exists': False}, 'class_pred': cls},
            {'$set': {'class_final': cls}}
        )

    print('updating news class complete')


scheduler.start()
