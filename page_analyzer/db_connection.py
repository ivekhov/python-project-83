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
        except ConnectionError as e:
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
        except ConnectionError as e:
            logging.warning(f"Error closing connection to database: {e}")
        return False


class DatabaseCursor(DatabaseConnection):
    """Context manager for handling database connections."""

    def __init__(self, db_url: str):
        """Initialize the DatabaseCursor with the database URL.
        Extends DatabaseConnection class.

        Args:
            db_url (str): The URL of the database.
        """
        super().__init__(db_url)
        self.curs = None
    
    def __enter__(self):
        """Enter the runtime context related to this object.

        Returns:
            psycopg2.extensions.connection.cursor: The database cursor.
        """
        try:
            self.curs = super().__enter__().cursor()
        except ConnectionError as e:
            logging.warning(f"Can't create cursor for database connection: {e}")
            self.curs = None
        return self.curs
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object.

        Args:
            exc_type (type): The exception type.
            exc_value (Exception): The exception instance.
            traceback (traceback): The traceback object.
        """
        try:
            if self.curs is not None:
                self.curs.close()
                logging.info("Cursor for atabase connection closed")
        except ConnectionError as e:
            logging.warning(f"Error closing cursor in connection: {e}")
        return False
