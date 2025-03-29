from typing import Optional, List

from semantic_kernel.functions import kernel_function
from semantic_kernel_plugins.logger.sk_logger import SKLogger

try:
    from pymongo import MongoClient
except ImportError:
    raise ImportError("pymongo is not installed. Please install it with 'pip install pymongo'.")

class MongoDBPlugin:
    def __init__(self, client: MongoClient):
        self.logger = SKLogger(name="MongoDBPlugin")
        self.logger.info("MONGODB PLUGIN INITIALIZED")
        self.client = client

    @kernel_function(
        description="Create a new database",
        name="create_database",
    )
    def create_database(self, database: str) -> str:
        self.logger.info(f"Creating database: {database}")
        self.client[database]
        return f"Database {database} created successfully"
    
    @kernel_function(
        description="Drop a database",
        name="drop_database",
    )
    def drop_database(self, database: str) -> str:
        self.logger.info(f"Dropping database: {database}")
        self.client.drop_database(database)
        return f"Database {database} dropped successfully"
    
    @kernel_function(
        description="Use a database",
        name="use_database",
    )
    def use_database(self, database: str) -> str:
        self.logger.info(f"Using database: {database}")
        self.client = self.client[database]
        return f"Database {database} used successfully"
    
    @kernel_function(
        description="Create a new collection",
        name="create_collection",
    )
    def create_collection(self, database: str, collection: str) -> str:
        self.logger.info(f"Creating collection: {collection}")
        self.client[database].create_collection(collection)
        return f"Collection {collection} created successfully"
    
    @kernel_function(
        description="Drop a collection",
        name="drop_collection",
    )
    def drop_collection(self, database: str, collection: str) -> str:
        self.logger.info(f"Dropping collection: {collection}")
        self.client[database].drop_collection(collection)
        return f"Collection {collection} dropped successfully"

    @kernel_function(
        description="List all databases",
        name="list_databases",
    )
    def list_databases(self) -> List[str]:
        self.logger.info("Listing all databases")
        result = self.client.list_database_names()
        self.logger.info(f"Databases: {result}")
        return result

    @kernel_function(
        description="List all collections in a database",
        name="list_collections",
    )
    def list_collections(self, database: str) -> List[str]:
        self.logger.info(f"Listing collections in database: {database}")
        db = self.client[database]
        result = db.list_collection_names()
        self.logger.info(f"Collections: {result}")
        return result

    @kernel_function(
        description="Check if database exists",
        name="database_exists",
    )
    def database_exists(self, database: str) -> bool:
        self.logger.info(f"Checking if database exists: {database}")
        result = database in self.client.list_database_names()
        self.logger.info(f"Database exists: {result}")
        return result

    @kernel_function(
        description="Check if collection exists in database",
        name="collection_exists",
    )
    def collection_exists(self, database: str, collection: str) -> bool:
        self.logger.info(f"Checking if collection exists: {collection} in database: {database}")
        if not self.database_exists(database):
            return False
        result = collection in self.client[database].list_collection_names()
        self.logger.info(f"Collection exists: {result}")
        return result

    @kernel_function(
        description="Get database statistics",
        name="get_database_stats",
    )
    def get_database_stats(self, database: str) -> dict:
        self.logger.info(f"Getting database stats: {database}")
        result = self.client[database].command("dbStats")
        self.logger.info(f"Database stats: {result}")
        return result

    @kernel_function(
        description="Get collection statistics",
        name="get_collection_stats",
    )
    def get_collection_stats(self, database: str, collection: str) -> dict:
        self.logger.info(f"Getting collection stats: {collection} in database: {database}")
        result = self.client[database].command("collStats", collection)
        self.logger.info(f"Collection stats: {result}")
        return result
    
    @kernel_function(
        description="Find collection with client",
        name="find_collection",
    )
    def find_collection(self, database: str, collection_name: str) -> bool:
        self.logger.info(f"Finding collection: {collection_name} in database: {database}")
        collections = self.client[database].list_collection_names()
        self.logger.info(f"Collections: {collections}")
        return collection_name in collections

    @kernel_function(
        description="Insert a document into the collection",
        name="insert_document",
    )
    def insert_document(self, document: dict, database: str, collection: str) -> str:
        self.logger.info(f"Inserting document: {document}")
        self.client[database][collection].insert_one(document)
        self.logger.info(f"Document inserted: {document}")
        return "Document inserted successfully"


    @kernel_function(
        description="Find a document in the collection",
        name="find_document",
    )
    def find_document(self, query: dict, database: str, collection: str) -> str:
        self.logger.info(f"Finding document: {query}")
        result = self.client[database][collection].find_one(query)
        self.logger.info(f"Document found: {result}")
        return result
    
    @kernel_function(
        description="Update a document in the collection",
        name="update_document",
    )
    def update_document(self, query: dict, update: dict, database: str, collection: str) -> str:
        self.logger.info(f"Updating document: {query} with {update}")
        result = self.client[database][collection].update_one(query, update)
        self.logger.info(f"Document updated: {result}")
        return result
    
    @kernel_function(
        description="Delete a document from the collection",
        name="delete_document",
    )
    def delete_document(self, query: dict, database: str, collection: str) -> str:
        self.logger.info(f"Deleting document: {query}")
        result = self.client[database][collection].delete_one(query)
        self.logger.info(f"Document deleted: {result}")
        return result
    
    @kernel_function(
        description="Count documents in the collection",
        name="count_documents",
    )
    def count_documents(self, database: str, collection: str) -> int:
        self.logger.info("Counting documents")
        result = self.client[database][collection].count_documents({})
        self.logger.info(f"Document count: {result}")
        return result
    
    @kernel_function(
        description="Get all documents from the collection",
        name="get_all_documents",
    )
    def get_all_documents(self, database: str, collection: str) -> list:
        self.logger.info("Getting all documents")
        result = list(self.client[database][collection].find())
        self.logger.info(f"Documents: {result}")
        return result
    
    @kernel_function(
        description="Get a single document from the collection",
        name="get_single_document",
    )
    def get_single_document(self, query: dict, database: str, collection: str) -> dict:
        self.logger.info(f"Getting single document: {query}")
        result = self.client[database][collection].find_one(query)
        self.logger.info(f"Document: {result}")
        return result
    
    @kernel_function(
        description="Get the first document from the collection",
        name="get_first_document",
    )
    def get_first_document(self, database: str, collection: str) -> dict:
        self.logger.info("Getting first document")
        result = self.client[database][collection].find_one()
        self.logger.info(f"Document: {result}")
        return result
    
    @kernel_function(
        description="Get the last document from the collection",
        name="get_last_document",
    )
    def get_last_document(self, database: str, collection: str) -> dict:
        self.logger.info("Getting last document")
        result = self.client[database][collection].find_one()
        self.logger.info(f"Document: {result}")
        return result
    