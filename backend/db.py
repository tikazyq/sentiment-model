from bson import ObjectId
from pymongo import MongoClient, DESCENDING
import config


class DbManager(object):
    __doc__ = """
    Database Manager class for handling database CRUD actions.
    """

    def __init__(self):
        self.mongo = MongoClient(host=config.MONGO_HOST,
                                 port=config.MONGO_PORT,
                                 username=config.MONGO_USERNAME,
                                 password=config.MONGO_PASSWORD,
                                 authSource=config.MONGO_AUTH_DB or config.MONGO_DB,
                                 connect=False)
        self.db = self.mongo[config.MONGO_DB]

    def save(self, col_name: str, item: dict, **kwargs) -> None:
        """
        Save the item in the specified collection
        :param col_name: collection name
        :param item: item object
        """
        col = self.db[col_name]

        # in case some fields cannot be saved in MongoDB
        if item.get('stats') is not None:
            item.pop('stats')

        return col.save(item, **kwargs)

    def remove(self, col_name: str, cond: dict, **kwargs) -> None:
        """
        Remove items given specified condition.
        :param col_name: collection name
        :param cond: condition or filter
        """
        col = self.db[col_name]
        col.remove(cond, **kwargs)

    def update(self, col_name: str, cond: dict, values: dict, **kwargs):
        """
        Update items given specified condition.
        :param col_name: collection name
        :param cond: condition or filter
        :param values: values to update
        """
        col = self.db[col_name]
        col.update(cond, {'$set': values}, **kwargs)

    def update_one(self, col_name: str, id: str, values: dict, **kwargs):
        """
        Update an item given specified _id
        :param col_name: collection name
        :param id: _id
        :param values: values to update
        """
        col = self.db[col_name]
        _id = id
        col.find_one_and_update({'_id': _id}, {'$set': values})

    def remove_one(self, col_name: str, id: str, **kwargs):
        """
        Remove an item given specified _id
        :param col_name: collection name
        :param id: _id
        """
        col = self.db[col_name]
        _id = id
        col.remove({'_id': _id})

    def list(self, col_name: str, cond: dict, sort_key=None, sort_direction=DESCENDING, skip: int = 0, limit: int = 100,
             **kwargs) -> list:
        """
        Return a list of items given specified condition, sort_key, sort_direction, skip, and limit.
        :param col_name: collection name
        :param cond: condition or filter
        :param sort_key: key to sort
        :param sort_direction: sort direction
        :param skip: skip number
        :param limit: limit number
        """
        if sort_key is None:
            sort_key = '_i'
        col = self.db[col_name]
        data = []
        for item in col.find(cond).sort(sort_key, sort_direction).skip(skip).limit(limit):
            data.append(item)
        return data

    def _get(self, col_name: str, cond: dict) -> dict:
        """
        Get an item given specified condition.
        :param col_name: collection name
        :param cond: condition or filter
        """
        col = self.db[col_name]
        return col.find_one(cond)

    def get(self, col_name: str, id: (ObjectId, str)) -> dict:
        """
        Get an item given specified _id.
        :param col_name: collection name
        :param id: _id
        """
        return self._get(col_name=col_name, cond={'_id': id})

    def get_one_by_key(self, col_name: str, key, value) -> dict:
        """
        Get an item given key/value condition.
        :param col_name: collection name
        :param key: key
        :param value: value
        """
        return self._get(col_name=col_name, cond={key: value})

    def count(self, col_name: str, cond) -> int:
        """
        Get total count of a collection given specified condition
        :param col_name: collection name
        :param cond: condition or filter
        """
        col = self.db[col_name]
        return col.count(cond)

    def get_latest_version(self, spider_id, node_id):
        """
        @deprecated
        """
        col = self.db['deploys']
        for item in col.find({'spider_id': ObjectId(spider_id), 'node_id': node_id}) \
                .sort('version', DESCENDING):
            return item.get('version')
        return None

    def get_last_deploy(self, spider_id):
        """
        Get latest deploy for a given spider_id
        """
        col = self.db['deploys']
        for item in col.find({'spider_id': ObjectId(spider_id)}) \
                .sort('finish_ts', DESCENDING):
            return item
        return None

    def get_last_task(self, spider_id):
        """
        Get latest deploy for a given spider_id
        """
        col = self.db['tasks']
        for item in col.find({'spider_id': ObjectId(spider_id)}) \
                .sort('create_ts', DESCENDING):
            return item
        return None

    def aggregate(self, col_name: str, pipelines, **kwargs):
        """
        Perform MongoDB col.aggregate action to aggregate stats given collection name and pipelines.
        Reference: https://docs.mongodb.com/manual/reference/command/aggregate/
        :param col_name: collection name
        :param pipelines: pipelines
        """
        col = self.db[col_name]
        return col.aggregate(pipelines, **kwargs)

    def create_index(self, col_name: str, **kwargs):
        col = self.db[col_name]
        col.create_index(**kwargs)

    def distinct(self, col_name: str, key: str, filter: dict):
        col = self.db[col_name]
        return sorted(col.distinct(key, filter))


db_manager = DbManager()
