import functools
import logging
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor


def with_cursor(func):
    """Decorator to initialize a database cursor 
        and pass it to the wrapped function."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = psycopg2.connect(self.db_url)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as db_curs:
                result = func(self, db_curs, *args, **kwargs)
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            logging.error(f"Database operation failed: {e}")
            raise
        finally:
            conn.close()
            logging.info("Database connection closed")
    return wrapper


class UrlRepository:
    """Repository for handling URL-related database operations."""

    def __init__(self, db_url: str):
        """Initialize the UrlRepository with the database URL.

        Args:
            db_url (str): The URL of the database.
        """
        self.db_url = db_url

    @with_cursor
    def get_urls(self, db_curs):
        """Get the content of the URLs table."""
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
            cte.id as url_id,
            cte.name as name,
            cte.last_checked as last_checked,
            cheks.status_code as status_code
        FROM cte
            LEFT JOIN url_checks AS cheks
                ON cte.last_check_id = cheks.id;
        """
        db_curs.execute(sql)
        return db_curs.fetchall()

    @with_cursor
    def find_id(self, db_curs, url: str) -> Optional[tuple]:
        """Find the ID of a URL.

        Args:
            url (str): The URL to find the ID for.

        Returns:
            Optional[tuple]: The ID of the URL, or None if not found.
        """
        sql = "SELECT id FROM urls WHERE name = %s"
        db_curs.execute(sql, (url,))
        return db_curs.fetchone()

    @with_cursor
    def find_url_details(self, db_curs, url_id: int) -> Optional[tuple]:
        """Find the details of a URL by ID.

        Args:
            url_id (int): The ID of the URL to find details for.

        Returns:
            Optional[tuple]: The details of the URL, or None if not found.
        """
        sql = "SELECT id, name, created_at FROM urls WHERE id = %s"
        db_curs.execute(sql, (url_id,))
        url = db_curs.fetchone()
        url = {
            'url_id': url.get('id'),
            'name': url.get('name'),
            'created_at': datetime.strftime(
                url.get('created_at'), '%Y-%m-%d'
            )
        }
        return url

    @with_cursor
    def find_url(self, db_curs, url_id: int) -> Optional[tuple]:
        """Find the URL by ID.

        Args:
            url_id (int): The ID of the URL to find.

        Returns:
            Optional[tuple]: The URL, or None if not found.
        """
        sql = "SELECT name FROM urls WHERE id = %s"
        db_curs.execute(sql, (url_id,))
        return db_curs.fetchone()

    @with_cursor
    def save_url(self, db_curs, url: str) -> Optional[tuple]:
        """Save a new URL to the database.

        Args:
            url (str): The URL to save.

        Returns:
            Optional[tuple]: The result of the insert , or None if failed.
        """
        sql = "INSERT INTO urls (name) VALUES (%s) RETURNING id"
        db_curs.execute(sql, (url,))
        url_id = db_curs.fetchone()
        url_id = url_id.get('id')
        return url_id

    @with_cursor
    def get_checks(self, db_curs, url_id: int) -> Optional[tuple]:
        """Get the checks for a specific URL by ID.

        Args:
            url_id (int): The ID of the URL to get checks for.

        Returns:
            Optional[tuple]: The checks for the URL, or None if not found.
        """
        sql = """
        SELECT
            id, TO_CHAR(created_at, 'YYYY-MM-DD') as created_at,
            status_code, h1, title, description
        FROM url_checks
        WHERE url_id = %s AND status_code IS NOT NULL
        ORDER BY id DESC;
        """
        db_curs.execute(sql, (url_id,))
        urls_raw = db_curs.fetchall()
        urls_checks = []
        for check in urls_raw:
            urls_checks.append(
                {
                    'check_id': check.get('id'),
                    'url_id': id,
                    'created_at': check.get('created_at'),
                    'status_code': check.get('status_code'),
                    'h1': check.get('h1'),
                    'title': check.get('title'),
                    'description': check.get('description')
                }
            )
        return urls_checks

    @with_cursor
    def save_checks(self, db_curs, url_data: dict) -> None:
        """Save checks for a specific URL.

        Args:
            url_data (dict): The data of the URL checks to save.
        """
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