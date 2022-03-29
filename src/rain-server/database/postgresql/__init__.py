"""PostgreSQL Driver wrapper"""
import contextlib
import logging

import psycopg

from ..datatypes import *
from ..errors import ConnectionException, DatabaseException, DataValidationException


@contextlib.contextmanager
def context_manager():
    """
    Manages standard PostgreSQL errors for encapsulating in generic database errors.

    Dynamically creates new class that inherits from both psycopg errors and framework errors.
    """
    logger = logging.getLogger()

    try:
        yield
    except (psycopg.errors.DataError, psycopg.errors.OperationalError, psycopg.errors.IntegrityError,
            psycopg.errors.ProgrammingError, psycopg.errors.NotSupportedError) as err:
        # Errors matching DataValidationException
        logger.error(err)

        raise DataValidationException(err)
    except psycopg.errors.DatabaseError as err:
        # DatabaseErrors
        logger.error(err)

        raise DatabaseException(err)
    except psycopg.errors.Error as err:
        # Generic Error
        logger.error(err)

        raise ConnectionException(err)


class PGCursor:
    """Manage PostgreSQL cursor"""

    def __init__(self, cursor: psycopg.cursor.Cursor):
        self._cursor = cursor

    @context_manager()
    def __enter__(self):
        self._cursor.__enter__()

    @context_manager()
    def __exit__(self, exc_type, exc_value, trace):
        self._cursor.__exit__(exc_type, exc_value, trace)

    @context_manager()
    def insert(self, item: DataItem):
        """
        Insert 1 data item into the database.

        :param item: DataItem to insert into the database.
        """
        # Uses for loop to ensure attributes list and values are in the same order
        attr_list, attr_format = self.format_keys(item.data_type())
        sql = f"INSERT INTO {item.data_type().get_name}({attr_list}) VALUES({attr_format})"
        self._cursor.execute(sql, item.to_database_dict())

    @context_manager()
    def insert_many(self, items: list[DataItem]):
        """
        Insert multiple DataItems of the same type into the database.

        :param items: Iterable of DataItem objects
        """
        data_type = items[0].data_type()
        attr_list, attr_format = self.format_keys(data_type)
        sql = f"INSERT INTO {data_type.get_name}({attr_list}) VALUES({attr_format})"
        self._cursor.executemany(sql, [i.to_database_dict() for i in items])

    @context_manager()
    def query(
            self,
            item_type: DataItem,
            filters: DataType
    ) -> typing.Iterable[DataItem]:
        """
        Find all Items matching the filter.

        :param item_type: Type of the item to read.
        :param filters: list of attributes name -> values.
        :return: An list of DataItems
        """
        raise NotImplementedError()

    def sanitizer(
            self,
            _: DataAttribute | BaseAttribute
    ) -> DataAttribute | BaseAttribute:
        """
        Input sanitize is natively provided by psycopg execute methods.
        This method is present to complete Cursor implementation.
        """
        pass

    @context_manager()
    def close(self):
        """Closes the cursor"""
        self._cursor.close()

    @staticmethod
    def format_keys(item: DataType) -> typing.Tuple[str, str]:
        """
        Transforms a list got attributes to:
        * attributes names joined by ','
        * '%(<attribute name>)s' joined by ','

        :param item: Type of the data
        :return: Tuple attribute list/list used to formatting
        """
        attr_list, attr_format = list(), list()
        for k in item.keys():
            attr_list.append(k)
            attr_format.append(f"%({k})s")

        return ",".join(attr_list), ",".join(attr_format)


class PGConnection(psycopg.Connection):
    """Manage PostgreSQL Connection"""

    @context_manager()
    def __enter__(self) -> PGCursor:
        self._active_cursor = PGCursor(self.cursor())
        return self._active_cursor

    @context_manager()
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._active_cursor.close()
        self.close()

    @context_manager()
    def cursor(self):
        return PGCursor(self.cursor())

    @context_manager()
    def close(self):
        self.close()
