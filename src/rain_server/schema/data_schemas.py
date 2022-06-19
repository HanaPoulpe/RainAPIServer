"""Defines GraphQL types"""
import datetime

import strawberry


@strawberry.type
class Location:
    """Sensor Location"""

    id: str
    name: str


@strawberry.type
class MeasurementType:
    """Measurement Type"""

    name: str
    unit: str
    default_format: str


@strawberry.type
class Sensor:
    """Sensor"""

    id: str
    name: str
    location: Location
    measurements: list[MeasurementType]


@strawberry.type
class Measurement:
    """Measurement"""

    sensor: Sensor
    measurement: MeasurementType
    date: datetime.datetime
    value: float
