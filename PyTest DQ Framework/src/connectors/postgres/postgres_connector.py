import psycopg2
import pandas as pd

class PostgresConnectorContextManager:
    """
    Context manager for connecting to PostgreSQL.
    Used with 'with' to automatically close the connection.
    """

    def __init__(self, db_user, db_password, db_host, db_name, db_port):
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_name = db_name
        self.db_port = db_port
        self.conn = None

    def __enter__(self):
        self.conn = psycopg2.connect(
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def get_data_sql(self, sql_query: str) -> pd.DataFrame:
        """
        Executes an SQL query and returns the result as a pandas DataFrame
        """
        return pd.read_sql_query(sql_query, self.conn)

