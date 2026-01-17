"""
Database connection and utility functions for PostgreSQL
"""
import os
from contextlib import contextmanager
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Manages PostgreSQL database connections"""

    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.database = os.getenv("POSTGRES_DB", "analytics_db")
        self.user = os.getenv("POSTGRES_USER", "analytics_user")
        self.password = os.getenv("POSTGRES_PASSWORD", "analytics_password")

    def get_connection_string(self) -> str:
        """Returns the PostgreSQL connection string"""
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            yield conn
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as a list of dictionaries

        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized queries

        Returns:
            List of dictionaries representing query results
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if cursor.description:  # SELECT query
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:  # INSERT, UPDATE, DELETE
                    conn.commit()
                    return [{"affected_rows": cursor.rowcount}]

    def test_connection(self) -> bool:
        """Test if database connection is working"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
