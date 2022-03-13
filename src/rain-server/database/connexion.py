"""Manages database connection"""
import typing

from . import datatypes

class Cursor(typing.Protocol):
    """
    Database cursor, non transactional

    Provides:
    - Query execution
    - Insert/Update Objects
    - Select Objects
    - Commit/Rollback
    """
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, trace):
        ...

    def insert(self, item: datatypes.DataItem):
        ...


class Connection(typing.Protocol):
    """
    Basic Database connection object.

    Allows to:
    - Get a cursor to run queries against.
    - Setup the tables.
    """
    def cursor(self) -> Cursor:
        """Create a connection cursor"""
        ...
