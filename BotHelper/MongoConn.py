from .MongoConnection import MongoConnection


class MongoConn(MongoConnection):

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.CONFIG = config

    def ensure_correct_docs(self, db, collection):
        if self.db != db:
            self.use_db(db)

        if self.collection != collection:
            self.use_collection(collection)

    def collection_log_remove_find(self, doc, db, collection, func):
        self.ensure_correct_docs(db, collection)

        return func(doc)

    def collection_update(self, doc_id, doc, db, collection, func):
        self.ensure_correct_docs(db, collection)

        return func(doc_id, doc)
