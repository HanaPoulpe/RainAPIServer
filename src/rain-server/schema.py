"""Defines API Schemas"""
import datetime
import decimal
import typing

import Measurement as Measurement
import strawberry

from database.datatypes import *

from .configuration import get_configuration


@strawberry.type
class SensorLocation(DataType):
    """Location of the sensor"""
    location_id: strawberry.ID("sensor_location")
    location_name: str

    @classmethod
    def get_table_name(cls) -> str:
        return "d_locations"

    def to_attribute_tuple(self) -> typing.Tuple[typing.Type[BaseAttribute], BaseAttribute]:
        return str, self.id

    def to_database_dict(self) -> dict[str, DataAttribute | BaseAttribute]:
        return {
            "location_id": self.id,
            "location_name": self.location_name,
        }


@strawberry.type
class Sensor(DataType):
    """Description of the sensor"""
    id: strawberry.ID("sensor")
    name: str
    location: SensorLocation

    @classmethod
    def get_table_name(cls) -> str:
        return "d_sensors"

    def to_attribute_tuple(self) -> typing.Tuple[typing.Type[BaseAttribute], BaseAttribute]:
        return str, self.id

    def to_database_dict(self) -> dict[str, DataAttribute | BaseAttribute]:
        return {
            "sensor_id": self.id,
            "location_id": self.location,
            "sensor_name": self.sensor_name,
        }


@strawberry.type
class SensorMeasurement(DataType):
    """Measurement"""
    sensor: Sensor
    measurement_name: str
    timestamp: datetime.datetime
    value: decimal.Decimal | int | datetime.datetime | datetime.timedelta

    @classmethod
    def get_table_name(cls) -> str:
        return "d_measurements"

    def to_attribute_tuple(self) -> typing.Tuple[typing.Type[BaseAttribute], BaseAttribute]:
        return str, f"{self.sensor.id}#{self.measurement_name}#{self.timestamp.isoformat()}"

    def to_database_dict(self) -> dict[str, DataAttribute | BaseAttribute]:
        return {
            "sensor_id": self.sensor.id,
            "measurement_name": self.measurement_name,
            "unit": str,
            "reporting_date": self.timestamp,
            "measurement_value": decimal.Decimal(self.measurement_value)
        }


@strawberry.type
class Query:
    """Queries"""
    sensors: typing.List[Sensor]
    measurements: typing.List[SensorMeasurement]

    @strawberry.field
    def version(self) -> str:
        """Returns the API Version"""
        from .version import __api_version__
        return __api_version__


@strawberry.type
class Mutation:
    """Mutations"""
    @strawberry.mutation
    def put_measurement(
            self,
            sensor: str,
            timestamp: str,
            measurements: typing.Dict[str, decimal.Decimal | str]
    ) -> typing.List[SensorMeasurement]:
        """
        Register a list of measurements from a Sensor.

        :param sensor: Sensor.id
        :param timestamp: ISO8601 timestamp
        :param measurements: Map of MeasurementType.name -> Value as Decimal or ISO8601 timestamp
        :return: List of SensorMeasurement
        """
        config = get_configuration()

        with config.database as cursor:
            sensor = next(iter(cursor.query(Sensor, {"sensor_id": sensor})))
            timestamp = datetime.datetime.fromisoformat(timestamp)

            measurements = [
                SensorMeasurement(
                    sensor=sensor,
                    measurement_name=m,
                    timestamp=timestamp,
                    value=v,
                ) for m, v in measurements.items()
            ]

            cursor.insert_many(measurements)

        return measurements


schema = strawberry.Schema(query=Query, mutation=Mutation)
