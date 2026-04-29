"""
MongoDB connection with graceful fallback.
If MongoDB is unavailable, uses in-memory storage so the app still runs.
"""

import motor.motor_asyncio
from config import settings

client = None
db = None

# In-memory fallback storage (used when MongoDB is not configured)
_memory_store = {
    "users": [],
    "articles": [],
}


class MemoryCollection:
    """Minimal in-memory MongoDB-like collection for local dev without Atlas."""

    def __init__(self, name: str):
        self.name = name
        if name not in _memory_store:
            _memory_store[name] = []

    @property
    def _data(self):
        return _memory_store[self.name]

    async def find_one(self, query: dict, projection=None):
        from bson import ObjectId
        for doc in self._data:
            match = True
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id", "")) != str(v):
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    async def insert_one(self, doc: dict):
        from bson import ObjectId
        import copy
        new_doc = copy.deepcopy(doc)
        new_doc["_id"] = ObjectId()
        self._data.append(new_doc)

        class Result:
            inserted_id = new_doc["_id"]
        return Result()

    async def update_one(self, query: dict, update: dict, upsert=False):
        from bson import ObjectId
        import copy

        class Result:
            upserted_id = None
            modified_count = 0

        result = Result()
        for doc in self._data:
            match = True
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id", "")) != str(v):
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                if "$set" in update:
                    doc.update(update["$set"])
                result.modified_count = 1
                return result

        if upsert and "$setOnInsert" in update:
            new_doc = copy.deepcopy(update["$setOnInsert"])
            new_doc["_id"] = ObjectId()
            self._data.append(new_doc)
            result.upserted_id = new_doc["_id"]

        return result

    def find(self, query=None, projection=None):
        return MemoryCursor(self._data, query or {}, projection)

    async def create_index(self, keys, **kwargs):
        pass  # no-op for memory store


class MemoryCursor:
    """Chainable cursor for in-memory find operations."""

    def __init__(self, data, query, projection):
        import copy
        self._data = [copy.deepcopy(d) for d in data]
        self._query = query
        self._sort_key = None
        self._sort_dir = -1
        self._skip_n = 0
        self._limit_n = 100

        # Apply query filter
        if query:
            filtered = []
            for doc in self._data:
                match = True
                for k, v in query.items():
                    if k == "$text":
                        # Simple text search
                        search = v.get("$search", "").lower()
                        text = (str(doc.get("title", "")) + " " + str(doc.get("description", ""))).lower()
                        if search not in text:
                            match = False
                            break
                    elif isinstance(v, dict) and "$in" in v:
                        if doc.get(k) not in v["$in"]:
                            match = False
                            break
                    elif doc.get(k) != v:
                        match = False
                        break
                if match:
                    filtered.append(doc)
            self._data = filtered

    def sort(self, key_or_list, direction=None):
        if isinstance(key_or_list, str):
            self._sort_key = key_or_list
            self._sort_dir = direction if direction is not None else -1
        return self

    def skip(self, n):
        self._skip_n = n
        return self

    def limit(self, n):
        self._limit_n = n
        return self

    async def to_list(self, length=None):
        data = self._data
        if self._sort_key:
            reverse = (self._sort_dir == -1)
            data = sorted(data, key=lambda x: x.get(self._sort_key, ""), reverse=reverse)
        data = data[self._skip_n:]
        limit = length or self._limit_n
        data = data[:limit]
        # Remove ObjectId from results
        result = []
        for doc in data:
            d = dict(doc)
            if "_id" in d:
                d["_id"] = str(d["_id"])
            result.append(d)
        return result


class MemoryDB:
    """In-memory database that mimics motor's AsyncIOMotorDatabase interface."""

    def __getattr__(self, name):
        return MemoryCollection(name)

    def __getitem__(self, name):
        return MemoryCollection(name)


async def connect_db():
    global client, db
    mongo_url = settings.MONGODB_URL

    # Check if a real MongoDB URL is configured
    if "username:password" in mongo_url or not mongo_url.startswith("mongodb"):
        print("⚠️  MongoDB not configured — using in-memory storage (data resets on restart)")
        print("   To persist data, set MONGODB_URL in backend/.env")
        db = MemoryDB()
        return

    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            mongo_url, serverSelectionTimeoutMS=5000
        )
        # Test connection
        await client.admin.command("ping")
        db = client[settings.DB_NAME]
        print(f"✅ Connected to MongoDB Atlas: {settings.DB_NAME}")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed ({e})")
        print("   Falling back to in-memory storage")
        db = MemoryDB()


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
