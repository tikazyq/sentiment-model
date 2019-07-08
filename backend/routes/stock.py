import tushare as ts
from flask import request

import config
from db import db_manager
from routes.base import BaseApi


class StockApi(BaseApi):
    pro = ts.pro_api(config.TUSHARE_TOKEN)

    def get(self, action: str = None):
        if hasattr(self.pro, action):
            df = getattr(self.pro, action)(**{k: request.args[k] for k in request.args})
            return {
                'status': 'ok',
                'items': [df.iloc[i].to_dict() for i in df.index.tolist()]
            }
        return getattr(self, action)()


class StockSimpleApi(BaseApi):
    col_name = 'stocks'


class StockIndexSimpleApi(BaseApi):
    col_name = 'stock_indexes'
