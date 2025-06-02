class AsyncMockCursor:
    def __init__(self, sync_cursor):
        self._cursor = iter(sync_cursor)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._cursor)
        except StopIteration:
            raise StopAsyncIteration


# === async wrapper for mongomock collections ===
class AsyncMockCollection:
    def __init__(self, collection):
        self._collection = collection

    async def find_one(self, *args, **kwargs):
        return self._collection.find_one(*args, **kwargs)

    async def insert_one(self, *args, **kwargs):
        return self._collection.insert_one(*args, **kwargs)

    async def delete_one(self, *args, **kwargs):
        return self._collection.delete_one(*args, **kwargs)

    async def update_one(self, *args, **kwargs):
        return self._collection.update_one(*args, **kwargs)

    def find(self, *args, **kwargs):
        # 🔁 Wrap the sync cursor in async-compatible wrapper. Allows for async to be called on iterables
        return AsyncMockCursor(self._collection.find(*args, **kwargs))


class AsyncMockDB:
    def __init__(self, db):
        self._db = db

    def __getitem__(self, name):
        return AsyncMockCollection(self._db[name])
