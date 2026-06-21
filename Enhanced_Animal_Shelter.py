import logging
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from bson.objectid import ObjectId


logging.basicConfig(
    filename="animalshelter.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class AnimalShelter:
    """
    Enhanced CRUD operations for the animals collection in MongoDB.
    """

    def __init__(
        self,
        username=None,
        password=None,
        host="127.0.0.1",
        port=27017,
        db_name="aac",
        collection_name="animals"
    ):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name

        self.client = None
        self.database = None
        self.collection = None

        self.connect()

    def connect(self):
        """Create and validate the MongoDB connection."""
        try:
            if self.username and self.password:
                connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
            else:
                connection_string = f"mongodb://{self.host}:{self.port}/"

            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )

            self.client.admin.command("ping")

            self.database = self.client[self.db_name]
            self.collection = self.database[self.collection_name]

            self.create_indexes()

            print("MongoDB connection successful.")
            return True

        except ServerSelectionTimeoutError as error:
            logging.error(f"MongoDB server connection error: {error}")
            print(f"MongoDB server connection error: {error}")
            self.client = None
            self.database = None
            self.collection = None
            return False

        except PyMongoError as error:
            logging.error(f"Connection error: {error}")
            print(f"Connection error: {error}")
            self.client = None
            self.database = None
            self.collection = None
            return False

    def reconnect(self):
        """Attempt to reconnect to MongoDB."""
        self.close_connection()
        return self.connect()

    def is_connected(self):
        """Check whether the MongoDB collection is available."""
        try:
            if self.client is None or self.collection is None:
                return False

            self.client.admin.command("ping")
            return True

        except PyMongoError:
            return False

    def health_check(self):
        """Return database health status."""
        try:
            if not self.is_connected():
                return {
                    "connected": False,
                    "database": self.db_name,
                    "collection": self.collection_name
                }

            return {
                "connected": True,
                "database": self.database.name,
                "collection": self.collection.name,
                "document_count": self.collection.count_documents({})
            }

        except PyMongoError as error:
            logging.error(f"Health check error: {error}")
            return {
                "connected": False,
                "database": self.db_name,
                "collection": self.collection_name
            }

    def create_indexes(self):
        """Create indexes for dashboard filtering, searching, and reporting."""
        try:
            if self.collection is None:
                return False

            self.collection.create_index([("animal_type", ASCENDING)])
            self.collection.create_index([("breed", ASCENDING)])
            self.collection.create_index([("sex_upon_outcome", ASCENDING)])
            self.collection.create_index([("age_upon_outcome_in_weeks", ASCENDING)])
            self.collection.create_index([("location_lat", ASCENDING)])
            self.collection.create_index([("location_long", ASCENDING)])

            self.collection.create_index([
                ("name", TEXT),
                ("breed", TEXT),
                ("animal_type", TEXT)
            ])

            return True

        except PyMongoError as error:
            logging.error(f"Index creation error: {error}")
            print(f"Index creation error: {error}")
            return False

    def validate_query(self, query):
        """Validate MongoDB query input."""
        if query is None:
            return {}

        if not isinstance(query, dict):
            raise TypeError("Query must be a dictionary.")

        return query

    def validate_data(self, data):
        """Validate insert or update data."""
        if data is None:
            raise ValueError("Data cannot be None.")

        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary.")

        if len(data) == 0:
            raise ValueError("Data dictionary cannot be empty.")

        return data

    def create(self, data):
        """Insert one document into the collection."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return False

            self.validate_data(data)
            result = self.collection.insert_one(data)
            return result.acknowledged

        except (ValueError, TypeError, PyMongoError) as error:
            logging.error(f"Create error: {error}")
            print(f"Create error: {error}")
            return False

    def read(self, query=None, limit=0):
        """Read documents from the collection using a query."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return []

            query = self.validate_query(query)
            result = self.collection.find(query)

            if isinstance(limit, int) and limit > 0:
                result = result.limit(limit)

            return list(result)

        except (TypeError, PyMongoError) as error:
            logging.error(f"Read error: {error}")
            print(f"Read error: {error}")
            return []

    def read_one(self, query=None):
        """Read one document from the collection."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return None

            query = self.validate_query(query)
            return self.collection.find_one(query)

        except (TypeError, PyMongoError) as error:
            logging.error(f"Read one error: {error}")
            print(f"Read one error: {error}")
            return None

    def update(self, query, new_values):
        """Update document(s) that match the query."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return 0

            query = self.validate_query(query)
            self.validate_data(new_values)

            if len(query) == 0:
                raise ValueError("Update query cannot be empty.")

            result = self.collection.update_many(query, {"$set": new_values})
            return result.modified_count

        except (ValueError, TypeError, PyMongoError) as error:
            logging.error(f"Update error: {error}")
            print(f"Update error: {error}")
            return 0

    def update_by_id(self, object_id, new_values):
        """Update one document by MongoDB ObjectId."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return 0

            self.validate_data(new_values)

            if not ObjectId.is_valid(object_id):
                raise ValueError("Invalid ObjectId.")

            result = self.collection.update_one(
                {"_id": ObjectId(object_id)},
                {"$set": new_values}
            )

            return result.modified_count

        except (ValueError, TypeError, PyMongoError) as error:
            logging.error(f"Update by ID error: {error}")
            print(f"Update by ID error: {error}")
            return 0

    def delete(self, query):
        """Delete document(s) that match the query."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return 0

            query = self.validate_query(query)

            if len(query) == 0:
                raise ValueError("Delete query cannot be empty.")

            result = self.collection.delete_many(query)
            return result.deleted_count

        except (ValueError, TypeError, PyMongoError) as error:
            logging.error(f"Delete error: {error}")
            print(f"Delete error: {error}")
            return 0

    def delete_by_id(self, object_id):
        """Delete one document by MongoDB ObjectId."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return 0

            if not ObjectId.is_valid(object_id):
                raise ValueError("Invalid ObjectId.")

            result = self.collection.delete_one({"_id": ObjectId(object_id)})
            return result.deleted_count

        except (ValueError, PyMongoError) as error:
            logging.error(f"Delete by ID error: {error}")
            print(f"Delete by ID error: {error}")
            return 0

    def count_documents(self, query=None):
        """Count documents matching a query."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return 0

            query = self.validate_query(query)
            return self.collection.count_documents(query)

        except (TypeError, PyMongoError) as error:
            logging.error(f"Count error: {error}")
            print(f"Count error: {error}")
            return 0

    def aggregate_by_breed(self, query=None, limit=10):
        """Count and rank breeds using MongoDB aggregation."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return []

            query = self.validate_query(query)

            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$breed",
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": limit},
                {
                    "$project": {
                        "_id": 0,
                        "breed": "$_id",
                        "count": 1
                    }
                }
            ]

            return list(self.collection.aggregate(pipeline))

        except (TypeError, PyMongoError) as error:
            logging.error(f"Breed aggregation error: {error}")
            print(f"Breed aggregation error: {error}")
            return []

    def aggregate_dashboard_summary(self, query=None):
        """Calculate dashboard summary statistics using MongoDB aggregation."""
        empty_summary = {
            "total_animals": 0,
            "unique_breeds": 0,
            "average_age": "N/A"
        }

        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return empty_summary

            query = self.validate_query(query)

            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_animals": {"$sum": 1},
                        "unique_breeds": {"$addToSet": "$breed"},
                        "average_age": {"$avg": "$age_upon_outcome_in_weeks"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_animals": 1,
                        "unique_breeds": {"$size": "$unique_breeds"},
                        "average_age": {"$round": ["$average_age", 2]}
                    }
                }
            ]

            result = list(self.collection.aggregate(pipeline))

            if result:
                return result[0]

            return empty_summary

        except (TypeError, PyMongoError) as error:
            logging.error(f"Summary aggregation error: {error}")
            print(f"Summary aggregation error: {error}")
            return empty_summary

    def text_search(self, search_text, limit=25):
        """Search animal records using MongoDB text search."""
        try:
            if not self.is_connected():
                self.reconnect()

            if not self.is_connected():
                return []

            if not search_text:
                return []

            query = {"$text": {"$search": search_text}}

            result = (
                self.collection
                .find(query, {"score": {"$meta": "textScore"}})
                .sort([("score", {"$meta": "textScore"})])
                .limit(limit)
            )

            return list(result)

        except PyMongoError as error:
            logging.error(f"Text search error: {error}")
            print(f"Text search error: {error}")
            return []

    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.collection = None