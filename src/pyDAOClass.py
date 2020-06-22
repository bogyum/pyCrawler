import pymongo, json
from bson.json_util import dumps

class DAO:

    def setClient(self, host, port, id, pw):
        self.client = pymongo.MongoClient("mongodb://%s:%s@%s:%s" % (id, pw, host, port))

    def setDB(self, dbName):
        self.db = self.client[dbName]
        return None

    def setCollection(self, collectionName):
        self.collection = self.db[collectionName]
        return None

    def setClose(self):
        self.client.close()

    # 신규 데이터 삽입
    def insert(self, query):
        self.collection.insert_one(query)

    # 데이터 조회
    def select(self, query, fieldCondition):
        result = self.collection.find_one(query, fieldCondition)
        return result

    def selectMany(self, query, fieldCondition):
        result = self.collection.find(query, fieldCondition)
        return list(result)

    # 데이터 삭제
    def delete(self, query):
        self.collection.delete(query)

    # 데이터 갱신
    def update(self, query, condition):
        self.collection.update(query, condition, upsert=True)



