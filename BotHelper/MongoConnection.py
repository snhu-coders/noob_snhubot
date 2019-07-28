from bson import json_util
from bson import SON
from bson.objectid import ObjectId
from pymongo import MongoClient, errors


class MongoConnection:
    """
    Creates a connection to a mongo db instance, sets the database
    and collection to work with, and executes various queries for the API
    """

    def __init__(self, db, collection, hostname='localhost', port=27017):
        """ Init with all data """
        self.client = self.connect_to_host(hostname, port)
        self.db = self.client[db]
        self.collection = self.db[collection]

        # Verify database has connected
        try:
            self.client.server_info()
            self.connected = True
        except errors.ServerSelectionTimeoutError as err:
            print(err)
            self.connected = False

    def connect_to_host(self, hostname, port):
        """ Connects to a MongoDB instance """
        return MongoClient(hostname, port, serverSelectionTimeoutMS=10000)

    def use_db(self, db):
        """ Change database of current client """
        self.db = self.client[db]

    def use_collection(self, collection):
        """ Change collection of current database """
        self.collection = self.db[collection]

    def find_document(self, query):
        """ Find a single document """
        return json_util.loads(json_util.dumps(
            self.collection.find_one(query)))

    def find_documents(self, query, projection=None):
        """ Find many documents """
        if projection:
            result = json_util.loads(json_util.dumps(
                self.collection.find(query, projection)))
        else:
            result = json_util.loads(
                json_util.dumps(self.collection.find(query)))

        return result

    def count_documents(self, query):
        """ Count document results of a query """
        try:
            # Use new method if exists
            return self.collection.count_documents(query)
        except TypeError:
            # Call deprecated method
            result = self.collection.find(query)

            return result.count()

    def insert_document(self, doc):
        """ Insert single document """
        return self.collection.insert_one(doc)

    def insert_documents(self, doc):
        """ Insert many document """
        return self.collection.insert_many(doc)

    def update_document(self, query, update):
        """ Update single document """
        return self.collection.update_one(query, update)

    def update_document_by_oid(self, oid, update):
        """ Updates single document by ObjectId """
        return self.update_document({"_id": ObjectId(oid)}, update)

    def update_documents(self, query, update):
        """ Update many document """
        return self.collection.update_many(query, update)

    def delete_document(self, query):
        """ Delete single document """
        return self.collection.delete_one(query)

    def delete_documents(self, query):
        """ Delete many document """
        return self.collection.delete_many(query)

    def aggregate_documents(self, pipeline):
        """ Performs an aggregation """
        return json_util.loads(json_util.dumps(
            self.collection.aggregate(pipeline)))
