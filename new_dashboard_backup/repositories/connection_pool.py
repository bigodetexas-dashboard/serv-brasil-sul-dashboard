"""
Database Connection Pool

Provides a simple connection pool for SQLite to improve performance
by reusing database connections instead of creating new ones for each query.
"""

import sqlite3
import threading
from queue import Queue, Empty
from typing import Optional


class ConnectionPool:
    """
    Thread-safe SQLite connection pool.

    Manages a pool of reusable database connections to reduce overhead
    of creating new connections for each query.
    """

    def __init__(self, db_path: str, pool_size: int = 5, timeout: int = 30) -> None:
        """
        Initialize the connection pool.

        Args:
            db_path: Path to SQLite database file
            pool_size: Maximum number of connections in pool
            timeout: Connection timeout in seconds
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0

        # Pre-create connections
        for _ in range(pool_size):
            self._pool.put(self._create_connection())

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimizations."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode for better performance
        )
        conn.row_factory = sqlite3.Row

        # Performance optimizations
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables

        self._created_connections += 1
        return conn

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection from the pool.

        Returns:
            Database connection

        Raises:
            Empty: If no connection available within timeout
        """
        try:
            return self._pool.get(timeout=5)
        except Empty:
            # Pool exhausted, create new connection if under limit
            with self._lock:
                if self._created_connections < self.pool_size * 2:
                    return self._create_connection()
            raise RuntimeError("Connection pool exhausted")

    def return_connection(self, conn: sqlite3.Connection) -> None:
        """
        Return a connection to the pool.

        Args:
            conn: Database connection to return
        """
        try:
            # Rollback any pending transaction
            conn.rollback()
            self._pool.put_nowait(conn)
        except Exception:
            # Pool full or connection bad, close it
            conn.close()

    def close_all(self) -> None:
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except Empty:
                break


# Global connection pool instance
_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def get_pool(db_path: str = "bigodebot.db") -> ConnectionPool:
    """
    Get or create the global connection pool.

    Args:
        db_path: Path to database file

    Returns:
        Connection pool instance
    """
    global _pool

    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ConnectionPool(db_path)

    return _pool


def get_connection(db_path: str = "bigodebot.db") -> sqlite3.Connection:
    """
    Get a database connection from the pool.

    Args:
        db_path: Path to database file

    Returns:
        Database connection

    Example:
        >>> conn = get_connection()
        >>> try:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM users")
        ... finally:
        ...     return_connection(conn)
    """
    pool = get_pool(db_path)
    return pool.get_connection()


def return_connection(conn: sqlite3.Connection, db_path: str = "bigodebot.db") -> None:
    """
    Return a connection to the pool.

    Args:
        conn: Database connection
        db_path: Path to database file
    """
    pool = get_pool(db_path)
    pool.return_connection(conn)
