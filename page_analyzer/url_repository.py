import logging
from typing import Optional

from flask import g
import psycopg2
from psycopg2.extras import RealDictCursor


class UrlRepository:
    """Repository for handling URL-related database operations."""
    def __init__(self, db_url: str):
        """Initialize the UrlRepository with the database URL.

        Args:
            db_url (str): The URL of the database.
        """
        self.db_url = db_url

    def get_connection(self):
        """Get a database connection.

        Returns:
            psycopg2.extensions.connection: The database connection.
        """
        if 'conn' not in g:
            try:
                g.conn = psycopg2.connect(self.db_url)
                logging.info("Connection to database established")
            except Exception as e:
                logging.warning(f"Can't establish connection to database: {e}")
                g.conn = None
        return g.conn

    @staticmethod
    def close_db_connection(exception):
        """Close the database connection."""
        conn = getattr(g, '_database', None)
        if conn is not None:
            conn.close()
            logging.info("Database connection closed")

    def get_content(self):
        """Get the content of the URLs table."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                sql = """
                WITH cte AS (
                    SELECT
                        u.id as id,
                        u.name AS name,
                    TO_CHAR(MAX(ch.created_at), 'YYYY-MM-DD') as last_checked,
                    MAX(ch.id) as last_check_id
                    FROM urls AS u
                        LEFT JOIN url_checks AS ch ON ch.url_id = u.id
                    GROUP BY 1, 2
                    ORDER BY 1 DESC
                ) SELECT
                    cte.id as id,
                    cte.name as name,
                    cte.last_checked as last_checked,
                    cheks.status_code as status_code
                FROM cte
                    LEFT JOIN url_checks AS cheks
                        ON cte.last_check_id = cheks.id;
                """
                cursor.execute(sql)
                return cursor.fetchall()

    def find_id(self, url: str) -> Optional[tuple]:
        """Find the ID of a URL.

        Args:
            url (str): The URL to find the ID for.

        Returns:
            Optional[tuple]: The ID of the URL, or None if not found.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "SELECT id FROM urls WHERE name = %s"
                cursor.execute(sql, (url,))
                return cursor.fetchone()

    def find_url_details(self, id: int) -> Optional[tuple]:
        """Find the details of a URL by ID.

        Args:
            id (int): The ID of the URL to find details for.

        Returns:
            Optional[tuple]: The details of the URL, or None if not found.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "SELECT id, name, created_at FROM urls WHERE id = %s"
                cursor.execute(sql, (id,))
                return cursor.fetchone()

    def find_url(self, id: int) -> Optional[tuple]:
        """Find the URL by ID.

        Args:
            id (int): The ID of the URL to find.

        Returns:
            Optional[tuple]: The URL, or None if not found.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "SELECT name FROM urls WHERE id = %s"
                cursor.execute(sql, (id,))
                return cursor.fetchone()

    def save_url(self, url: str) -> Optional[tuple]:
        """Save a new URL to the database.

        Args:
            url (str): The URL to save.

        Returns:
            Optional[tuple]: The result of the insert , or None if failed.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO urls (name) VALUES (%s)"
                cursor.execute(sql, (url,))
            conn.commit()

    def get_checks(self, id: int) -> Optional[tuple]:
        """Get the checks for a specific URL by ID.

        Args:
            id (int): The ID of the URL to get checks for.

        Returns:
            Optional[tuple]: The checks for the URL, or None if not found.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    id, TO_CHAR(created_at, 'YYYY-MM-DD') as created_at,
                    status_code, h1, title, description
                FROM url_checks
                WHERE url_id = %s AND status_code IS NOT NULL
                ORDER BY id DESC;
                """
                cursor.execute(sql, (id,))
                return cursor.fetchall()

    def save_checks(self, url_data: dict) -> None:
        """Save checks for a specific URL.

        Args:
            url_data (dict): The data of the URL checks to save.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    url_data['url_id'],
                    url_data['status_code'],
                    url_data['h1'],
                    url_data['title'],
                    url_data['description']
                ))
            conn.commit()
