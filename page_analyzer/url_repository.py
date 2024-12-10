import logging
from datetime import datetime
from typing import Optional

from page_analyzer.db_connection import DatabaseConnection


class UrlRepository:
    """Repository for handling URL-related database operations."""

    def __init__(self, db_url: str):
        """Initialize the UrlRepository with the database URL.

        Args:
            db_url (str): The URL of the database.
        """
        self.db_url = db_url

    def close_connection(self, exception: Optional[Exception] = None):
        """Close the database connection.

        Args:
            exception (Optional[Exception]): 
            The exception that caused the teardown, if any.
        """
        with DatabaseConnection(self.db_url) as conn:
            try:
                conn.close()
                logging.info("Database connection closed")
            except Exception as e:
                logging.warning(f"Error closing connection to database: {e}")

    def get_content(self):
        """Get the content of the URLs table."""
        with DatabaseConnection(self.db_url) as db_curs:
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
            db_curs.execute(sql)
            return db_curs.fetchall()

    def find_id(self, url: str) -> Optional[tuple]:
        """Find the ID of a URL.

        Args:
            url (str): The URL to find the ID for.

        Returns:
            Optional[tuple]: The ID of the URL, or None if not found.
        """
        with DatabaseConnection(self.db_url) as db_curs:
            sql = "SELECT id FROM urls WHERE name = %s"
            db_curs.execute(sql, (url,))
            return db_curs.fetchone()

    def find_url_details(self, id: int) -> Optional[tuple]:
        """Find the details of a URL by ID.

        Args:
            id (int): The ID of the URL to find details for.

        Returns:
            Optional[tuple]: The details of the URL, or None if not found.
        """
        with DatabaseConnection(self.db_url) as db_curs:
            sql = "SELECT id, name, created_at FROM urls WHERE id = %s"
            db_curs.execute(sql, (id,))
            url = db_curs.fetchone()
            url = {
                'id': url.get('id'),
                'name': url.get('name'),
                'created_at': datetime.strftime(
                    url.get('created_at'), '%Y-%m-%d'
                    )
            }
            return url

    def find_url(self, id: int) -> Optional[tuple]:
        """Find the URL by ID.

        Args:
            id (int): The ID of the URL to find.

        Returns:
            Optional[tuple]: The URL, or None if not found.
        """
        with DatabaseConnection(self.db_url) as db_curs:
            sql = "SELECT name FROM urls WHERE id = %s"
            db_curs.execute(sql, (id,))
            return db_curs.fetchone()

    def save_url(self, url: str) -> Optional[tuple]:
        """Save a new URL to the database.

        Args:
            url (str): The URL to save.

        Returns:
            Optional[tuple]: The result of the insert , or None if failed.
        """
        with DatabaseConnection(self.db_url) as db_curs:
            sql = "INSERT INTO urls (name) VALUES (%s) RETURNING id"
            db_curs.execute(sql, (url,))
            db_curs.commit()

    def get_checks(self, id: int) -> Optional[tuple]:
        """Get the checks for a specific URL by ID.

        Args:
            id (int): The ID of the URL to get checks for.

        Returns:
            Optional[tuple]: The checks for the URL, or None if not found.
        """
        with DatabaseConnection(self.db_url) as db_curs:
            sql = """
            SELECT
                id, TO_CHAR(created_at, 'YYYY-MM-DD') as created_at,
                status_code, h1, title, description
            FROM url_checks
            WHERE url_id = %s AND status_code IS NOT NULL
            ORDER BY id DESC;
            """
            db_curs.execute(sql, (id,))
            urls_raw = db_curs.fetchall()
            urls_checks = []
            for check in urls_raw:
                urls_checks.append(
                    {
                        'id': check.get('id'),
                        'url_id': id,
                        'created_at': check.get('created_at'),
                        'status_code': check.get('status_code'),
                        'h1': check.get('h1'),
                        'title': check.get('title'),
                        'description': check.get('description')
                    }
                )
            return urls_checks

    def save_checks(self, url_data: dict) -> None:
        """Save checks for a specific URL.

        Args:
            url_data (dict): The data of the URL checks to save.
        """
        with DatabaseConnection(self.db_url) as db_curs:
            sql = """
            INSERT INTO url_checks
                (url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s)
            """
            db_curs.execute(sql, (
                url_data['url_id'],
                url_data['status_code'],
                url_data['h1'],
                url_data['title'],
                url_data['description']
            ))
            db_curs.commit()
