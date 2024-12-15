import logging

import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseConnection:
    """Context manager for handling database connections."""

    def __init__(self, db_url: str):
        """Initialize the DatabaseConnection with the database URL.

        Args:
            db_url (str): The URL of the database.
        """
        self.db_url = db_url
        self.conn = None

    def __enter__(self):
        """Enter the runtime context related to this object.

        Returns:
            psycopg2.extensions.connection: The database connection.
        """
        try:
            self.conn = psycopg2.connect(
                self.db_url, 
                cursor_factory=RealDictCursor
            )
            logging.info("Connection to database established")
        except Exception as e:
            logging.warning(f"Can't establish connection to database: {e}")
            self.conn = None
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object.

        Args:
            exc_type (type): The exception type.
            exc_value (Exception): The exception instance.
            traceback (traceback): The traceback object.
        """
        try:
            if self.conn is not None:
                self.conn.close()
                logging.info("Database connection closed")
        except Exception as e:
            logging.warning(f"Error closing connection to database: {e}")
        return False


class DatabaseCursor(DatabaseConnection):
    def __init__(self, db_url: str):
        super().__init__(db_url)
        self.curs = None
    
    def __enter__(self):
        
        try:
            self.curs = super().__enter__().cursor()
        
        except Exception as e:
            logging.warning(f"Error in Cursor Class: {e}")
            self.curs = None
        return self.curs
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.curs is not None:
                self.curs.close()
                logging.info("Database connection closed")
        except Exception as e:
            logging.warning(f"Error closing connection to database: {e}")
        return False
