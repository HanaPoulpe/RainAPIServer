"""Defines API Schemas"""
import datetime
import decimal
import typing

import strawberry


@strawberry.type
class SensorLocation:
    """Location of the sensor"""
    location_id: strawberry.ID("sensor_location")
    location_name: str


@strawberry.type
class MeasurementType:
    """Defines a measurement"""
    id: strawberry.ID("measurement_type")
    name: str
    unit: str


@strawberry.type
class Sensor:
    """Description of the sensor"""
    id: strawberry.ID("sensor")
    name: str
    location: SensorLocation
    address: str


@strawberry.type
class SensorMeasurement:
    """Measurement"""
    sensor: Sensor
    measurement_type: MeasurementType
    timestamp: datetime.datetime
    value: decimal.Decimal | int | datetime.datetime | datetime.timedelta


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
        raise NotImplementedError()


schema = strawberry.Schema(query=Query, mutation=Mutation)
