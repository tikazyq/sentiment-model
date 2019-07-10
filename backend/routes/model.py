import os
import re

import joblib
from pandas import *
import jieba
import jieba.posseg
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from lime.lime_text import LimeTextExplainer

import config
from db import db_manager
from routes.base import BaseApi
from utils import jsonify


def cut(doc):
    pos_tags_banned = [
        # 连词
        'c',
        # 副词
        'd',
        # 助词
        'u',
        # 标点符号
        'w'
    ]
    for x in jieba.posseg.cut(doc):
        # 过滤禁用词性单词
        flag = True
        for pos in pos_tags_banned:
            if x.flag.startswith(pos):
                flag = False
                break
        if not flag:
            continue

        # 去除单个字的词
        if len(x.word) < 2:
            continue

        # 去除数字
        if re.search(r'\d+', x.word) is not None:
            continue

        yield x.word


def evaluate(y, y_pred):
    print('accuracy: %s' % accuracy_score(y, y_pred))
    print('precision: %s' % precision_score(y, y_pred, average='weighted'))
    print('recall: %s' % recall_score(y, y_pred, average='weighted'))
    print('f1: %s' % f1_score(y, y_pred, average='weighted'))


def get_clf(name):
    if name == 'lg':
        return LogisticRegression(penalty='l1', C=1)
    elif name == 'svm':
        return SVC()
    elif name == 'nb':
        return MultinomialNB(alpha=1)
    elif name == 'rf':
        return RandomForestClassifier()
    elif name == 'mlp':
        return MLPClassifier()


class ModelApi(BaseApi):
    col_name = 'models'

    arguments = [
        ('text', str),
        ('class', int),
    ]

    # 分类器名称
    clf_name = config.MODEL_NAME

    def post(self, action: str = None):
        if not hasattr(self, action):
            return {
                       'status': 'ok',
                       'code': 400,
                       'error': 'action "%s" invalid' % action
                   }, 400

        return getattr(self, action)()

    def train(self):
        query = {
            'class': {
                '$exists': True
            }
        }
        data = [d for d in db_manager.list('stock_news', query, limit=9999999)]
        df = DataFrame(data)
        df.index = range(len(df))

        # 文本
        txt = df.title.fillna('') + df.text

        # 目标向量
        y = df['class']

        # 向量转换器
        vec = CountVectorizer(tokenizer=cut)

        # 词向量
        X = vec.fit_transform(txt)

        # 分类器
        clf = get_clf(self.clf_name)

        # 分割训练测试数据
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

        # 训练模型
        clf.fit(x_train, y_train)

        if not os.path.exists(config.MODEL_DIR):
            os.mkdir(config.MODEL_DIR)
        filename = os.path.join(config.MODEL_DIR, f'{self.clf_name}.pkl')
        joblib.dump(clf, filename)

        filename_vec = os.path.join(config.MODEL_DIR, f'vec.pkl')
        joblib.dump(vec, filename_vec)

        acc_train = accuracy_score(y_train, clf.predict(x_train))
        acc_test = accuracy_score(y_test, clf.predict(x_test))

        model_id = db_manager.save(self.col_name, {
            '_id': self.clf_name,
            'acc_train': acc_train,
            'size_train': len(y_train),
            'acc_test': acc_test,
            'size_test': len(y_test),
            'ts': datetime.now()
        })

        return jsonify(db_manager.get(self.col_name, model_id))

    def predict(self):
        args = self.parser.parse_args()
        text = args.get('text')

        filename = os.path.join(config.MODEL_DIR, f'{self.clf_name}.pkl')
        clf = joblib.load(filename)
        filename_vec = os.path.join(config.MODEL_DIR, f'vec.pkl')
        vec = joblib.load(filename_vec)

        x = vec.transform([text])

        return {
            'status': 'ok',
            'class': int(clf.predict(x)[0]),
        }

    def explain(self):
        args = self.parser.parse_args()
        text = args.get('text')
        cls = args.get('class')

        filename = os.path.join(config.MODEL_DIR, f'{self.clf_name}.pkl')
        clf = joblib.load(filename)
        filename_vec = os.path.join(config.MODEL_DIR, f'vec.pkl')
        vec = joblib.load(filename_vec)

        c = make_pipeline(vec, clf)

        class_names = [-1, 0, 1]
        cls_idx = class_names.index(cls)

        # 转换后的文本
        text_converted = ' '.join([x for x in cut(text)])

        explainer = LimeTextExplainer(class_names=class_names)
        exp = explainer.explain_instance(
            text_converted,
            c.predict_proba,
            labels=(cls,),
            num_features=20,
            num_samples=100,
        )

        proba = c.predict_proba([text_converted])
        score = proba[0][cls_idx]

        return {
            'status': 'ok',
            'class': cls,
            'score': score,
            'proba': proba.tolist(),
            'items': [{'word': x[0], 'weight': x[1]} for x in exp.as_list(cls)]
        }
