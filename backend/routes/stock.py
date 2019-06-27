import tushare as ts
from routes.base import BaseApi


class StockApi(BaseApi):
    pro = ts.pro_api()

    def get(self, action: str = None):
        if hasattr(self.pro, action):
            df = getattr(self.pro, action)()
            return {
                'status': 'ok',
                'items': [df.iloc[i].to_dict() for i in df.index.tolist()]
            }
        return getattr(self, action)()
