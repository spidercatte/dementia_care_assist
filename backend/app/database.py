import os
import sqlite3
import urllib.parse
from typing import List, Dict, Any, Optional

try:
    import psycopg2
except ImportError:
    psycopg2 = None

from app.config import settings

class DatabaseClient:
    def __init__(self):
        self.db_url = getattr(settings, "database_url", None)
        # Fallback to config path or environment variable
        if not self.db_url:
            self.db_url = os.environ.get("DATABASE_URL", "")

        self.is_postgres = self.db_url.startswith("postgresql://") or self.db_url.startswith("postgres://")

        if self.is_postgres and psycopg2 is None:
            raise ImportError(
                "psycopg2 is required for PostgreSQL connections. "
                "Ensure psycopg2-binary is installed."
            )

    def _get_connection(self):
        if self.is_postgres:
            # Parse connection URL for psycopg2
            result = urllib.parse.urlparse(self.db_url)
            username = result.username
            password = result.password
            database = result.path[1:]
            hostname = result.hostname
            port = result.port or 5432

            return psycopg2.connect(
                database=database,
                user=username,
                password=password,
                host=hostname,
                port=port
            )
        else:
            conn = sqlite3.connect(settings.db_path)
            conn.row_factory = sqlite3.Row
            return conn

    def _format_query(self, query: str) -> str:
        if self.is_postgres:
            # Rewrite SQLite-specific AUTOINCREMENT syntax to PostgreSQL SERIAL syntax
            query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            # Convert SQLite placeholder '?' to PostgreSQL placeholder '%s'
            query = query.replace("?", "%s")
        return query

    def execute(self, query: str, params: tuple = ()) -> None:
        formatted_query = self._format_query(query)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(formatted_query, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        formatted_query = self._format_query(query)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(formatted_query, params)
            row = cursor.fetchone()
            if not row:
                return None

            if self.is_postgres:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            else:
                return dict(row)
        finally:
            conn.close()

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        formatted_query = self._format_query(query)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(formatted_query, params)
            rows = cursor.fetchall()

            if self.is_postgres:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            else:
                return [dict(row) for row in rows]
        finally:
            conn.close()

db_client = DatabaseClient()
