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
    ]

    def get(self, action: str = None):
        return getattr(self, action)()

    def get_news_stats(self):
        args = self.parser.parse_args()
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        ts_code = args.get('ts_code')
        start_ts = datetime.strptime(start_date, '%Y%m%d')
        end_ts = datetime.strptime(end_date, '%Y%m%d')
        query = {
            'ts': {
                '$gte': start_ts,
                '$lt': end_ts
            }
        }
        if ts_code is not None:
            query['stocks'] = ts_code

        stats = [x for x in db_manager.aggregate('stock_news', [
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

        return {
            'status': 'ok',
            'stats': jsonify(stats)
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
