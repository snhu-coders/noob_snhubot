from .MongoConnection import MongoConnection

class MongoConn(MongoConnection):

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.CONFIG = config

    def log_to_collection(self, doc, db, collection):
        if self.db != db:
            self.use_db(db)

        if self.collection != collection:
            self.use_collection(collection)

        return self.insert_document(doc)
