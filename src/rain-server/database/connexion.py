"""Manages database connection"""
import typing

from . import datatypes


T = typing.TypeVar("T", bound=datatypes.DataItem)


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

    def insert(self, item: datatypes.DataItem) -> None:
        """
        Insert 1 DataItem into the database.

        :param item: Item to insert
        """
        ...

    def insert_many(self, items: list[T]):
        """
        Insert multiple DataItems of the same type into the database.

        :param items: Iterable of DataItem objects
        """
        ...

    def query(
            self,
            item_type: T,
            filters: datatypes.DataType
    ) -> typing.Iterable[datatypes.DataItem]:
        """
        Find all Items matching the filter.

        :param item_type: Type of the item to read.
        :param filters: list of attributes name -> values.
        :return: An list of DataItems
        """
        ...

    def sanitizer(
            self,
            input_value: datatypes.DataAttribute | datatypes.BaseAttribute,
    ) -> datatypes.DataAttribute | datatypes.BaseAttribute:
        """
        Secures a value to be safely inserted into the database.

        :param input_value: value to be sanitized.
        :return: sanitized value of the same type as the input.
        """
        ...

    def close(self):
        """Close the cursor."""
        ...


class Connection(typing.Protocol):
    """
    Basic Database connection object.

    Allows to:
    - Get a cursor to run queries against.
    - Setup the tables.
    """
    def __enter__(self) -> Cursor:
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    def cursor(self) -> Cursor:
        """Create a connection cursor"""
        ...

    def close(self):
        """Closes the database connection"""
        ...

    def open(self):
        """Opens the database connection"""
        ...
