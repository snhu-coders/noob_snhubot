from .MongoConnection import MongoConnection


def context_aware(func):
    def wrapper(*args, **kwargs):
        if "db" in kwargs:
            if args[0].db != kwargs["db"]:
                args[0].use_db(kwargs["db"])

        if "collection" in kwargs:
            if args[0].db != kwargs["collection"]:
                args[0].use_collection(kwargs["collection"])

        return func(*args)

    return wrapper


class MongoConn(MongoConnection):

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.CONFIG = config

    @context_aware
    def insert_document(self, doc):
        return super().insert_document(doc)

    @context_aware
    def update_document_by_oid(self, oid, doc):

        return super().update_document_by_oid(oid, doc)

    @context_aware
    def delete_document(self, doc):

        return super().delete_document(doc)

    @context_aware
    def find_document(self, query):

        return super().find_document(query)

    @context_aware
    def find_documents(self, query):

        return super().find_documents(query)
