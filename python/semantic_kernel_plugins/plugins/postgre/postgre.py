from typing import Optional

from semantic_kernel.functions import kernel_function
from semantic_kernel_plugins.logger.sk_logger import SKLogger

try:
    from psycopg2 import connect # type: ignore
except ImportError:
    raise ImportError("psycopg2 is not installed. Please install it with 'pip install psycopg2'.")

class PostgrePlugin:
    def __init__(self, dbConnection: connect):
        self.dbConnection = dbConnection
        self.logger = SKLogger(name="PostgrePlugin")
        self.logger.info("POSTGRE PLUGIN INITIALIZED")
        
    def _execute_query(self, query: str):
        cursor = self.dbConnection.cursor()
        cursor.execute(query)
        try:
            results = cursor.fetchall()
            self.dbConnection.commit()
            return results
        except:
            return cursor.statusmessage
        finally:
            cursor.close()
    
    @kernel_function(
        description="Execute a query on the database",
        name="execute_query",
    )
    def execute_query(self, query: str) -> str:
        self.logger.info(f"Executing query: {query}")
        return self._execute_query(query)
    
    @kernel_function(
        description="Fetch table names from the database",
        name="fetch_table_names",
    )
    def fetch_table_names(self) -> list:
        self.logger.info("Fetching table names")
        return self._execute_query("SELECT table_name FROM information_schema.tables")
    
    @kernel_function(
        description="Fetch table schema from the database",
        name="fetch_table_schema",
    )
    def fetch_table_schema(self, table_name: str) -> list:
        self.logger.info(f"Fetching schema for table: {table_name}")
        return self._execute_query(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
    
    @kernel_function(
        description="Fetch table data from the database",
        name="fetch_table_data",
    )
    def fetch_table_data(self, table_name: str) -> list:
        self.logger.info(f"Fetching data for table: {table_name}")
        return self._execute_query(f"SELECT * FROM {table_name}")
    
    @kernel_function(
        description="Insert data into a table",
        name="insert_data",
    )
    def insert_data(self, table_name: str, data: dict) -> str:
        self.logger.info(f"Inserting data into table: {table_name}")
        return self._execute_query(f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join([f"'{str(v)}'" for v in data.values()])})")
    
    @kernel_function(
        description="Update data in a table",
        name="update_data",
    )
    def update_data(self, table_name: str, data: dict) -> str:
        self.logger.info(f"Updating data in table: {table_name}")
        return self._execute_query(f"UPDATE {table_name} SET {', '.join([f"{k} = '{str(v)}'" for k, v in data.items()])}")
    
    @kernel_function(
        description="Delete data from a table",
        name="delete_data",
    )
    def delete_data(self, table_name: str, data: dict) -> str:
        self.logger.info(f"Deleting data from table: {table_name}")
        return self._execute_query(f"DELETE FROM {table_name} WHERE {', '.join([f"{k} = '{str(v)}'" for k, v in data.items()])}")
    
    @kernel_function(
        description="Create a new table",
        name="create_table",
    )
    def create_table(self, table_name: str, schema: dict) -> str:
        self.logger.info(f"Creating table: {table_name}")
        return self._execute_query(f"CREATE TABLE {table_name} ({', '.join([f"{k} {v}" for k, v in schema.items()])})")
    
    @kernel_function(
        description="Drop a table",
        name="drop_table",
    )
    def drop_table(self, table_name: str) -> str:
        self.logger.info(f"Dropping table: {table_name}")
        return self._execute_query(f"DROP TABLE {table_name}")    
    
    @kernel_function(
        description="Get the last inserted ID",
        name="get_last_inserted_id",
    )
    def get_last_inserted_id(self) -> int:
        self.logger.info("Getting last inserted ID")
        return self._execute_query("SELECT LASTVAL()")
    
    @kernel_function(
        description="Get the number of rows affected by the last operation",
        name="get_rows_affected",
    )
    def get_rows_affected(self) -> int:
        self.logger.info("Getting number of rows affected")
        return self._execute_query("SELECT ROW_COUNT()")
