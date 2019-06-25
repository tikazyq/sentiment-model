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
    r = requests.get(f'http://{config.FLASK_HOST}:{config.FLASK_PORT}/model/train')
    print(f'response: {r.content.decode("utf-8")}')


@scheduler.scheduled_job('interval', minutes=5)
def predict_news():
    filename = os.path.join(config.MODEL_DIR, f'{config.MODEL_NAME}.pkl')
    clf = joblib.load(filename)
    filename_vec = os.path.join(config.MODEL_DIR, f'vec.pkl')
    vec = joblib.load(filename_vec)

    for d in db_manager.list('results_xueqiu', {'class_pred': {'$exists': False}}, limit=999999):
        print(f'predicting {d["_id"]}')
        text = d.get('text')
        x = vec.transform([text])
        db_manager.update_one('results_xueqiu', d['_id'], {
            'class_pred': clf.predict(x)[0],
        })


scheduler.start()
