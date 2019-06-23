from routes.base import BaseApi


class NewsApi(BaseApi):
    col_name = 'results_xueqiu'

    arguments = [
        # increase: 1 / neutral: 0 / decrease: -1
        ('class', int)
    ]
