import asyncio
import functools
import json
import os
from datetime import datetime, timedelta
from random import randint
from time import sleep

import joblib
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import DESCENDING, ASCENDING

import config
from db import db_manager

scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', minutes=10)
def train_model():
    print('training model...')
    r = requests.get(f'http://localhost:{config.FLASK_PORT}/model/train')
    print(f'response: {r.content.decode("utf-8")}')


@scheduler.scheduled_job('interval', minutes=1)
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
    r = requests.get(f'http://localhost:{config.FLASK_PORT}/stock/stock_basic')
    data = json.loads(r.content)
    for item in data['items']:
        item['_id'] = item['ts_code']
        db_manager.save(col_name='stocks', item=item)


@scheduler.scheduled_job('interval', hours=6)
def update_stock_daily():
    async def _update(ts_code, semaphore):
        async with semaphore:
            # 获取数据
            r = requests.get(f'http://localhost:{config.FLASK_PORT}/stock/daily?ts_code={ts_code}')
            data = json.loads(r.content)

            # 删除已有数据
            db_manager.remove('stock_daily', {'ts_code': ts_code})

            # 批量插入数据
            items = []
            for d in data['items']:
                d['_id'] = d['ts_code'] + '_' + d['trade_date']
                items.append(d)
            db_manager.insert_many('stock_daily', items)

    print('updating stock daily...')

    # 创建索引
    db_manager.create_index('stock_daily', keys=[('trade_date', DESCENDING)])
    db_manager.create_index('stock_daily', keys=[('ts_code', ASCENDING)])

    # 创建事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    semaphore = asyncio.Semaphore(500)

    # 遍历股票列表
    tasks = []
    for s in db_manager.list('stocks', {}, limit=999999):
        ts_code = s['ts_code']
        tasks.append(_update(ts_code, semaphore))  # 开始更新数据
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


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


@scheduler.scheduled_job('interval', days=1)
def update_stock_stats():
    async def _update(url, ts_code):
        r = await asyncio.get_event_loop().run_in_executor(None, functools.partial(requests.get, url))
        raw_data = json.loads(r.content)
        d = raw_data['recom']
        d['_id'] = ts_code
        sleep(randint(1, 5))
        db_manager.save('stock_stats', d)

    print('updating stock stats...')

    last_n_days = 30
    start_date = (datetime.now() - timedelta(last_n_days)).strftime('%Y%m%d')
    end_date = (datetime.now() - timedelta(0)).strftime('%Y%m%d')

    data = []
    for s in db_manager.list('stocks', {}, limit=999999):
        ts_code = s['ts_code']
        url = f'http://localhost:{config.FLASK_PORT}/stats/get_news_stats?ts_code={ts_code}' + \
              f'&start_date={start_date}&end_date={end_date}'
        data.append({'url': url, 'ts_code': ts_code})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [_update(d['url'], d['ts_code']) for d in data]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


scheduler.start()
