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
        self.cursor = None

    def __enter__(self):
        """Enter the runtime context related to this object.

        Returns:
            psycopg2.extensions.connection.cursor: 
                The cursor to database connection.
        """
        try:
            self.conn = psycopg2.connect(
                self.db_url,
                cursor_factory=RealDictCursor
                )
            self.cursor = self.conn.cursor()
            logging.info("Connection to database established")
        except ConnectionRefusedError as e:
            logging.warning(f"Can't establish connection to database: {e}")
        return self.cursor


    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object.

        Args:
            exc_type (type): The exception type.
            exc_value (Exception): The exception instance.
            traceback (traceback): The traceback object.
        """
        try:
            if self.cursor is not None:
                self.cursor.close()
                logging.info("Cursor closed")
            if self.conn is not None:
                self.conn.close()
                logging.info("Database connection closed")
        except Exception as e:
            logging.warning(f"Error closing connection to database: {e}")
        return False
    
    def commit(self):
        try:
            if self.conn is not None:
                self.conn.commit()
                logging.info("Commited successfully")
        except Exception as e:
            self.conn.rollback()
            logging.warning(f"Error commiting to database: {e}")
