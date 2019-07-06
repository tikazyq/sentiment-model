from collections import defaultdict
from datetime import datetime, timedelta

from db import db_manager
from routes.base import BaseApi
from utils import jsonify


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
        start_ts = datetime.strptime(start_date, '%Y%m%d')
        end_ts = datetime.strptime(end_date, '%Y%m%d')
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
        print(news_stats_dict)

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
        start_ts = datetime.strptime(start_date, '%Y%m%d')
        end_ts = datetime.strptime(end_date, '%Y%m%d')
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
                            'date': '$ts'
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

        return {
            'status': 'ok',
            'stats': jsonify(stats),
            'daily_stats': jsonify(daily_stats),
            'news': jsonify(news_list),
        }

        # items = db_manager.list('stock_news', query, limit=999999)
        # data = defaultdict(int)
        # daily = {
        #     -1: defaultdict(int),
        #     0: defaultdict(int),
        #     1: defaultdict(int)
        # }
        # for item in items:
        #     cls = item.get('class')
        #     if cls is None:
        #         cls = item.get('class_pred')
        #     if cls is not None:
        #         data[cls] += 1
        #
        #     date = item['ts'].strftime('%Y%m%d')
        #     daily[cls][date] += 1
        #
        # daily_data = {
        #     -1: [],
        #     0: [],
        #     1: [],
        # }
        # dt = start_date
        # while dt <= end_date:
        #     for cls in daily_data.keys():
        #         daily_data[cls].append({
        #             'date': dt,
        #             'value': daily[cls].get(dt) or 0
        #         })
        #     dt = (datetime.strptime(dt, '%Y%m%d') + timedelta(1)).strftime('%Y%m%d')
        #
        # return {
        #     'status': 'ok',
        #     'data': data,
        #     'daily': daily_data
        # }
