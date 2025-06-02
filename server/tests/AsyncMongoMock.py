class AsyncMockCollection:
    def __init__(self, collection):
        self._collection = collection

    async def find_one(self, *args, **kwargs):
        return self._collection.find_one(*args, **kwargs)

    async def insert_one(self, *args, **kwargs):
        return self._collection.insert_one(*args, **kwargs)

    # add other async wrappers as needed...

class AsyncMockDB:
    def __init__(self, db):
        self._db = db

    def __getitem__(self, name):
        return AsyncMockCollection(self._db[name])