"""PostgreSQL Driver wrapper"""
import contextlib

import psycopg

from ..datatypes import *
from ..errors import ConnectionException, DatabaseException, DataValidationException


@contextlib.contextmanager
def context_manager():
    """
    Manages standard PostgreSQL errors for encapsulating in generic database errors.

    Dynamically creates new class that inherits from both psycopg errors and framework errors.
    """
    try:
        yield
    except (psycopg.errors.DataError, psycopg.errors.OperationalError, psycopg.errors.IntegrityError,
            psycopg.errors.ProgrammingError, psycopg.errors.NotSupportedError) as err:
        # Errors matching DataValidationException
        class PGException(err.__class__, DataValidationException):
            def __init__(self, base_err: err.__class__, *args):
                super().__init__(*base_err.args, *args)

        raise PGException(err)
    except psycopg.errors.DatabaseError as err:
        # DatabaseErrors
        class PGException(err.__class__, DatabaseException):
            def __init__(self, base_err: psycopg.errors.DatabaseError, *args):
                super().__init__(*base_err.args, *args)

        raise PGException(err)
    except psycopg.errors.Error as err:
        # Generic Error
        class PGException(err.__class__, ConnectionException):
            def __init__(self, base_err: err.__class__, *args):
                super().__init__(*base_err.args, *args)

        raise PGException(err)


class PGCursor(psycopg.Cursor):
    """Manage PostgreSQL cursor"""

    @context_manager()
    def insert(self, item: DataItem):
        """
        Insert 1 data item into the database.

        :param item: DataItem to insert into the database.
        """
        # Uses for loop to ensure attributes list and values are in the same order
        attr_list, attr_format = self.format_keys(item.data_type())
        sql = f"INSERT INTO {item.data_type().get_name}({attr_list}) VALUES({attr_format})"
        self.execute(sql, item.to_database_dict())

    @context_manager()
    def insert_many(self, items: list[DataItem]):
        """
        Insert multiple DataItems of the same type into the database.

        :param items: Iterable of DataItem objects
        """
        data_type = items[0].data_type()
        attr_list, attr_format = self.format_keys(data_type)
        sql = f"INSERT INTO {data_type.get_name}({attr_list}) VALUES({attr_format})"
        self.executemany(sql, [i.to_database_dict() for i in items])

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
    """Manage PostgreSQL"""
