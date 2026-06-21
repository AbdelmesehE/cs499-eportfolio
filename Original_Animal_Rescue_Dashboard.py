from pymongo import MongoClient
from pymongo.errors import PyMongoError


class AnimalShelter:
    """CRUD operations for the animals collection in MongoDB."""

    def __init__(
        self,
        username,
        password,
        host="127.0.0.1",
        port=27017,
        db_name="aac",
        collection_name="animals"
    ):
        """Initialize the MongoDB client and collection."""
        try:
            self.client = MongoClient(f"mongodb://{host}:{port}/")
                
            self.database = self.client[db_name]
            self.collection = self.database[collection_name]
        except PyMongoError as error:
            print(f"Connection error: {error}")
            self.client = None
            self.database = None
            self.collection = None

    def create(self, data):
        """Insert one document into the collection."""
        try:
            if data is not None and isinstance(data, dict) and len(data) > 0:
                self.collection.insert_one(data)
                return True
            return False
        except PyMongoError as error:
            print(f"Create error: {error}")
            return False

    def read(self, query):
        """Read documents from the collection using find()."""
        try:
            if query is not None and isinstance(query, dict):
                result = self.collection.find(query)
                return list(result)
            return []
        except PyMongoError as error:
            print(f"Read error: {error}")
            return []

    def update(self, query, new_values):
        """Update document(s) that match the query."""
        try:
            if (
                query is not None
                and isinstance(query, dict)
                and new_values is not None
                and isinstance(new_values, dict)
                and len(new_values) > 0
            ):
                result = self.collection.update_many(query, {"$set": new_values})
                return result.modified_count
            return 0
        except PyMongoError as error:
            print(f"Update error: {error}")
            return 0

    def delete(self, query):
        """Delete document(s) that match the query."""
        try:
            if query is not None and isinstance(query, dict):
                result = self.collection.delete_many(query)
                return result.deleted_count
            return 0
        except PyMongoError as error:
            print(f"Delete error: {error}")
            return 0