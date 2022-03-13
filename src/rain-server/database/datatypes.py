"""Defines basic data types"""
import datetime
import decimal
import typing


BaseAttribute: typing.TypeAlias = (
        int | float | decimal.Decimal |
        str |
        datetime.datetime | datetime.date | datetime.timedelta |
        dict[str, 'BaseAttribute'] | list['BaseAttribute']
)


class DataAttribute(typing.Protocol):
    """Complex Data Item Attribute"""
    def to_attribute_tuple(self) -> typing.Tuple[typing.Type[BaseAttribute], BaseAttribute]:
        """
        Transforms DataAttribute to a BaseAttribute

        :returns: BaseAttribute (type, value)
        """
        ...


class DataType(dict[str, DataAttribute | BaseAttribute]):
    """Datatype definition."""
    pass


class DataItem(typing.Protocol):
    """Basic Item"""
    @classmethod
    def data_type(cls) -> DataType:
        """Returns the DataType of the item"""
        ...

    def to_database_dict(self) -> dict[str, DataAttribute | BaseAttribute]:
        """
        Represents an Item for database operations.

        :return: dict of attribute name -> attribute value
        """
        ...


def convert(value: DataAttribute | BaseAttribute) -> typing.Tuple[typing.Type[BaseAttribute],
                                                                  BaseAttribute]:
    """
    Converts a value to a type, value tuple.

    :param value: Value to convert
    :returns: Attribute type, attribute value
    :raises TypeError: when value is not supported
    """
    if isinstance(value, BaseAttribute):
        return type(value), value
    if hasattr(value, "to_attribute_tuple"):
        return value.to_attribute_tuple()
    raise TypeError(f"{value!r} is neither a BaseAttribute nor a DataAttribute")
