"""PostgreSQL Driver wrapper"""
import psycopg

from ..datatypes import *


class PGCursor(psycopg.Cursor):
    """Manage PostgreSQL cursor"""

    def insert(self, item: DataItem):
        """
        Insert 1 data item into the database.

        :param item: DataItem to insert into the database.
        """
        # Uses for loop to ensure attributes list and values are in the same order
        attr_list, attr_format = self.format_keys(item.data_type())
        sql = f"INSERT INTO {item.data_type().get_name}({attr_list}) VALUES({attr_format})"
        self.execute(sql, item.to_database_dict())

    def insert_many(self, items: list[DataItem]):
        """
        Insert multiple DataItems of the same type into the database.

        :param items: Iterable of DataItem objects
        """
        data_type = items[0].data_type()
        attr_list, attr_format = self.format_keys(data_type)
        sql = f"INSERT INTO {data_type.get_name}({attr_list}) VALUES({attr_format})"
        self.executemany(sql, [i.to_database_dict() for i in items])

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
