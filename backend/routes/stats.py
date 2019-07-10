import json
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
import numpy as np
from pytz import timezone

import config
from db import db_manager
from routes.base import BaseApi
from utils import jsonify

tz = timezone('Asia/Shanghai')


class StatsApi(BaseApi):
    arguments = [
        ('start_date', str),
        ('end_date', str),
        ('ts_code', str),
        ('market', str),
        ('exchange', str),
        ('industry', str),
    ]

    def get(self, action: str = None):
        return getattr(self, action)()

    def get_stock_list(self):
        args = self.parser.parse_args()
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        market = args.get('market')
        industry = args.get('industry')
        exchange = args.get('exchange') or 'SH'
        start_ts = tz.localize(datetime.strptime(start_date, '%Y%m%d'))
        end_ts = tz.localize(datetime.strptime(end_date, '%Y%m%d')) + timedelta(days=1)
        query = {}
        if market is not None:
            query['market'] = market
        if industry is not None:
            query['industry'] = industry
        query['ts_code'] = {
            '$regex': exchange + '$'
        }

        # 股票列表
        stock_list = sorted(
            [x for x in db_manager.list('stocks', query, limit=999999)],
            key=lambda x: x['ts_code']
        )

        # 股票新闻数据
        query_ = {
            'ts': {
                '$gte': start_ts,
                '$lt': end_ts,
            },
            'source': 'sina',
            'class_final': {
                '$exists': True
            }
        }
        news_stats = [x for x in db_manager.aggregate('stock_news', [
            {'$match': query_},
            {'$unwind': '$stocks'},
            {
                '$project': {
                    'ts_code': '$stocks',
                    'pos': {'$cond': [{'$eq': ['$class_final', 1]}, 1, 0]},
                    'med': {'$cond': [{'$eq': ['$class_final', 0]}, 1, 0]},
                    'neg': {'$cond': [{'$eq': ['$class_final', -1]}, 1, 0]},
                }
            },
            {
                '$group': {
                    '_id': '$ts_code',
                    'total': {'$sum': 1},
                    'pos': {'$sum': '$pos'},
                    'med': {'$sum': '$med'},
                    'neg': {'$sum': '$neg'},
                }
            }
        ])]
        news_stats_dict = {x['_id']: x for x in news_stats}

        # 将股票列表与新闻数据join起来
        for i in range(len(stock_list)):
            s = stock_list[i]
            ts_code = s['ts_code']
            n = news_stats_dict.get(ts_code) or {}
            s['news_total'] = n.get('total') or 0
            s['news_pos'] = n.get('pos') or 0
            s['news_med'] = n.get('med') or 0
            s['news_neg'] = n.get('neg') or 0
            stock_list[i] = s

        # 操作建议数据
        recom_list = [x for x in db_manager.list('stock_stats', {}, limit=999999)]
        recom_dict = {x['_id']: x for x in recom_list}

        # 将操作建议数据与股票数据join起来
        for i in range(len(stock_list)):
            s = stock_list[i]
            ts_code = s['ts_code']
            s['recom_news'] = recom_dict[ts_code]['news'] if recom_dict.get(ts_code) is not None else None
            s['recom_position'] = recom_dict[ts_code]['position'] if recom_dict.get(ts_code) is not None else None
            s['recom_trend'] = recom_dict[ts_code]['trend'] if recom_dict.get(ts_code) is not None else None
            s['recom_overall'] = recom_dict[ts_code]['overall'] if recom_dict.get(ts_code) is not None else None

        return {
            'status': 'ok',
            'stocks': stock_list
        }

    def get_industry_list(self):
        industry_list = [x['_id'] for x in db_manager.aggregate(col_name='stocks', pipelines=[
            {
                '$group': {
                    '_id': '$industry'
                }
            },
            {
                '$sort': {
                    '_id': 1
                }
            }
        ])]
        return {
            'status': 'ok',
            'industries': industry_list
        }

    def get_news_stats(self):
        args = self.parser.parse_args()
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        ts_code = args.get('ts_code')
        start_ts = tz.localize(datetime.strptime(start_date, '%Y%m%d'))
        end_ts = tz.localize(datetime.strptime(end_date, '%Y%m%d')) + timedelta(days=1)
        query = {
            'source': 'sina',
            'ts': {
                '$gte': start_ts,
                '$lt': end_ts
            },
            'class_final': {
                '$in': [-1, 1]
            }
        }
        if ts_code is not None:
            query['stocks'] = ts_code

        # 获取总数据
        stats_list = [x for x in db_manager.aggregate('stock_news', [
            {
                '$match': query
            },
            {
                '$group': {
                    '_id': '$class_final',
                    'count': {'$sum': 1}
                }
            }
        ])]

        # 获取每日数据
        daily = [x for x in db_manager.aggregate('stock_news', [
            {
                '$match': query
            },
            {
                '$project': {
                    'class': '$class_final',
                    'date': {
                        '$dateToString': {
                            'format': '%Y%m%d',
                            'date': '$ts',
                            'timezone': 'Asia/Shanghai',
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'date': '$date',
                        'class': '$class',
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'date': '$_id.date',
                    'class': '$_id.class',
                    'count': '$count',
                    '_id': 0
                }
            },
            {
                '$sort': {
                    'class': 1,
                    'date': 1
                }
            }
        ])]

        daily_dict = {
            -1: defaultdict(dict),
            1: defaultdict(dict),
        }
        for d in daily:
            cls = d['class']
            date = d['date']
            count = d['count']
            daily_dict[cls][date] = count

        daily_stats = {
            -1: [],
            1: [],
        }
        date = start_date
        while date <= end_date:
            dt = datetime.strptime(date, '%Y%m%d')
            if dt.weekday() >= 5:
                date = (dt + timedelta(1)).strftime('%Y%m%d')
                continue

            for cls in [-1, 1]:
                daily_stats[cls].append({
                    'date': date,
                    'count': daily_dict[cls].get(date) or 0,
                })
            date = (dt + timedelta(1)).strftime('%Y%m%d')

        # 新闻列表
        news_list = [x for x in db_manager.list('stock_news', query, limit=999999, sort_key='ts', project={'text': 0})]

        stats = defaultdict(int)
        for cls in [-1, 1]:
            arr = [x for x in filter(lambda x: x['_id'] == cls, stats_list)]
            if len(arr):
                stats[cls] = arr[0]['count']
            else:
                stats[cls] = 0

        # 获取建议
        recom_news = self._get_recom_news(ts_code)  # 舆情建议
        recom_position = self._get_recom_position(ts_code)  # 价位建议
        recom_trend = self._get_recom_trend(ts_code)  # 趋势建议
        recom_overall = self._get_recom_overall(
            recom_news,
            recom_position,
            recom_trend,
        )

        return {
            'status': 'ok',
            'stats': jsonify(stats),
            'daily_stats': jsonify(daily_stats),
            'news': jsonify(news_list),
            'recom': {
                'news': recom_news,
                'position': recom_position,
                'trend': recom_trend,
                'overall': recom_overall,
            }
        }

    @staticmethod
    def _get_stock_daily(ts_code, start_date, end_date) -> DataFrame:
        filter_ = {
            'ts_code': ts_code,
            'trade_date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }
        r = requests.get(f'http://localhost:{config.FLASK_PORT}/stock_daily?filter={json.dumps(filter_)}'
                         f'&page_size=999999')
        data = json.loads(r.content)
        df = DataFrame(data['items'])
        return df

    @staticmethod
    def _get_recom_news(ts_code):
        last_n_days = 14
        start_date = (datetime.now() - timedelta(last_n_days)).strftime('%Y%m%d')
        end_date = (datetime.now() - timedelta(0)).strftime('%Y%m%d')
        start_ts = tz.localize(datetime.strptime(start_date, '%Y%m%d'))
        end_ts = tz.localize(datetime.strptime(end_date, '%Y%m%d')) + timedelta(days=1)

        query = {
            'source': 'sina',
            'stocks': ts_code,
            'ts': {
                '$gte': start_ts,
                '$lt': end_ts
            },
            'class_final': {
                '$in': [-1, 1]
            }
        }
        stats_list = [x for x in db_manager.aggregate('stock_news', [
            {
                '$match': query
            },
            {
                '$group': {
                    '_id': '$class_final',
                    'count': {'$sum': 1}
                }
            }
        ])]
        stats = defaultdict(int)
        for cls in [-1, 1]:
            arr = [x for x in filter(lambda x: x['_id'] == cls, stats_list)]
            if len(arr):
                stats[cls] = arr[0]['count']
            else:
                stats[cls] = 0

        if sum(stats.values()) == 0:
            return 0

        news_threshold = 1 / 3
        neg_news_threshold = 1 / 2
        diff_pct = abs(stats[1] - stats[-1]) / sum(stats.values())
        if diff_pct > news_threshold:
            if stats[1] > stats[-1]:
                recom_news = 1
            else:
                if diff_pct > neg_news_threshold:
                    recom_news = -3
                else:
                    recom_news = -1
        else:
            recom_news = 0
        return recom_news

    def _get_recom_trend(self, ts_code):
        last_n_days = 14

        # 斜率阈值
        trend_threshold = 0.02

        start_date = (datetime.now() - timedelta(last_n_days)).strftime('%Y%m%d')
        end_date = (datetime.now() - timedelta(0)).strftime('%Y%m%d')

        df = self._get_stock_daily(ts_code, start_date, end_date)
        df = df.sort_values('trade_date')

        X = np.arange(0, len(df)).reshape(-1, 1)
        y = df['close']
        reg = LinearRegression()
        reg.fit(X, y)
        if abs(reg.coef_[0]) > trend_threshold:
            if reg.coef_[0] > 0:
                return 1
            else:
                return -1
        else:
            return 0

    def _get_recom_position(self, ts_code):
        last_n_days = 90
        range_cuts = [1 / 4, 3 / 4]

        start_date = (datetime.now() - timedelta(last_n_days)).strftime('%Y%m%d')
        end_date = (datetime.now() - timedelta(0)).strftime('%Y%m%d')

        df = self._get_stock_daily(ts_code, start_date, end_date)
        df = df.sort_values('trade_date')

        # 最近一次收盘价
        current_price = df.iloc[len(df) - 1]['close']
        min_price = df['close'].min()
        max_price = df['close'].max()

        # 根据区间确定价位
        if (current_price - min_price) / (max_price - min_price) > range_cuts[1]:
            return -1
        elif (current_price - min_price) / (max_price - min_price) < range_cuts[0]:
            return 1
        else:
            return 0

    @staticmethod
    def _get_recom_overall(*values):
        value = sum(values)
        if value >= 2:
            return 1
        elif value == 0:
            return 0
        elif value <= -2:
            return -1
        else:
            return 0
