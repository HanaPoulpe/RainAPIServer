"""Defines GraphQL types"""
import datetime
from decimal import Decimal

import strawberry


@strawberry.type
class Location:
    id: str
    name: str


@strawberry.type
class MeasurementType:
    name: str
    unit: str
    is_date: bool = False


@strawberry.type
class Sensor:
    id: str
    name: str
    location: Location
    measurements: list[MeasurementType]


@strawberry.type
class Measurement:
    sensor: Sensor
    measurement: MeasurementType
    date: datetime.datetime
    value: float
