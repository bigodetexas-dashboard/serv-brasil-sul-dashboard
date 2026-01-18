"""
Base Repository Module

Provides base database connection and query execution functionality
for all repository classes in the BigodeBot project.
"""

import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()


class SharedConnectionWrapper:
    """
    Wraps a sqlite3 connection to prevent it from being closed by repositories
    during bulk operations (like stress testing).
    """

    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        # Do nothing - connection is managed externally
        pass


class BaseRepository:
    """
    Base repository class providing database connection and query execution.

    All repository classes should inherit from this class to get
    standardized database access methods.

    Attributes:
        db_file (str): Path to the SQLite database file
        _shared_conn (Optional[SharedConnectionWrapper]): Shared connection for bulk operations
    """

    def __init__(self, db_path: str | None = None) -> None:
        """
        Initialize the base repository.

        Args:
            db_path: Optional custom path to database file.
                    If not provided, uses default bigode_unified.db
        """
        if db_path:
            self.db_file = db_path
        else:
            # Determine strict path to DB to avoid relative path issues
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_file = os.path.join(base_dir, "bigode_unified.db")
        self._shared_conn: SharedConnectionWrapper | None = None

    def set_shared_connection(self, conn: sqlite3.Connection) -> None:
        """
        Set a shared connection to be used by all database calls.

        Useful for stress tests or bulk operations where you want to
        manage the connection lifecycle externally.

        Args:
            conn: SQLite connection object to share across operations

        Example:
            >>> conn = sqlite3.connect('bigode_unified.db')
            >>> repo = PlayerRepository()
            >>> repo.set_shared_connection(conn)
            >>> # Perform multiple operations
            >>> conn.close()
        """
        self._shared_conn = SharedConnectionWrapper(conn)
        # Ensure row_factory is set for consistency
        conn.row_factory = sqlite3.Row

    def get_conn(self) -> sqlite3.Connection | None:
        """
        Create and return a SQLite database connection.

        If a shared connection is set, returns that instead of creating a new one.
        Connections are configured with:
        - 60 second timeout
        - Row factory for dictionary-like access
        - check_same_thread=False for multi-threading

        Returns:
            SQLite connection object, or None if connection fails

        Raises:
            None - errors are caught and logged
        """
        if self._shared_conn:
            return self._shared_conn

        try:
            conn = sqlite3.connect(self.db_file, timeout=60.0, check_same_thread=False)
            # Enable dictionary access for rows
            conn.row_factory = sqlite3.Row
            return conn
        except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
            print(f"[ERROR] SQLite Connect Error: {e}")
            return None

    def execute_query(
        self, query: str, params: tuple | list = ()
    ) -> list[sqlite3.Row] | int | bool | None:
        """
        Execute a SQL query safely with automatic commit/rollback.

        For SELECT queries, returns list of rows.
        For INSERT/UPDATE/DELETE, returns lastrowid or True on success.

        Args:
            query: SQL query string (can contain ? placeholders)
            params: Tuple or list of parameters to bind to query

        Returns:
            - List[sqlite3.Row] for SELECT queries
            - int (lastrowid) for INSERT queries
            - True for successful UPDATE/DELETE
            - None on error

        Example:
            >>> # SELECT query
            >>> rows = repo.execute_query("SELECT * FROM users WHERE id = ?", (123,))
            >>>
            >>> # INSERT query
            >>> user_id = repo.execute_query(
            ...     "INSERT INTO users (discord_id, username) VALUES (?, ?)",
            ...     ("123", "TestUser")
            ... )
        """
        conn = self.get_conn()
        if not conn:
            return []

        try:
            cur = conn.cursor()
            cur.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                return rows
            else:
                conn.commit()
                return cur.lastrowid or True
        except (sqlite3.OperationalError, sqlite3.IntegrityError, sqlite3.DatabaseError) as e:
            print(f"[ERROR] Query Execution Failed: {e}")
            print(f"[ERROR] Query: {query}")
            print(f"[ERROR] Params: {params}")
            conn.rollback()
            return None
        finally:
            conn.close()
