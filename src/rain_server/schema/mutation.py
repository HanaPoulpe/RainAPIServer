"""Defines the mutations"""
import datetime

import strawberry

from .data_schemas import Measurement


def add_measurement(
    sensor_id: str,
    measurement_name: str,
    measurement_date: datetime.datetime,
    measurement_value: float,
    signature: str,
) -> Measurement:
    """
    Add measurement from a MeasurementInput.

    - Check for sensor_id, measurement_name to retrieve the related public_key.
    - Checks the signature with the gathered public key.
    - Puts the measurement into the database.
    """
    raise NotImplementedError()


@strawberry.type
class Mutation:
    """GraphQL mutations"""

    add_measurement = strawberry.field(resolver=add_measurement)
