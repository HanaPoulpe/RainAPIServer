"""Defines the mutations"""
import datetime

import strawberry

from ..authenticate import check_signature
from ..configuration import get_database, get_logger
from .data_schemas import Location, Measurement, MeasurementType, Sensor
from .errors import AuthenticationError, InvalidSensorError


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
    logger = get_logger()
    database = get_database()

    query = database.select_sensors_measurement(sensor_id, measurement_name)

    message = f"{measurement_date}{measurement_date}{measurement_value}{sensor_id}"

    logger.info("Connecting to database...")
    with database.engine.connect() as conn:
        d_sensor = conn.execute(query).first()

        if not d_sensor:
            error_msg = (f"No matching sensor or measurement found for {sensor_id=}, "
                         f"{measurement_name=}")
            logger.error(error_msg)
            raise InvalidSensorError(error_msg)

        logger.info("Checking signature...")
        if not check_signature(message, d_sensor.public_key, signature):
            raise AuthenticationError("Signature verification failed.")

        insert = database.measurements.insert().values(
            location_id=d_sensor.location_id,
            sensor_id=sensor_id,
            measurement_name=measurement_name,
            unit=d_sensor.unit,
            measurement_datetime=measurement_date,
            measurement_value=measurement_value,
            d_created_date_utc=datetime.datetime.utcnow(),
            d_updated_date_utc=datetime.datetime.utcnow(),
        ).on_conflict_do_update(
            database.measurements.primary_key,
            set={
                "location_id": d_sensor.location_id,
                "sensor_id": sensor_id,
                "measurement_name": measurement_name,
                "unit": d_sensor.unit,
                "measurement_datetime": measurement_date,
                "measurement_value": measurement_value,
                "d_updated_date_utc": datetime.datetime.utcnow(),
            },
        )
        conn.execute(insert)

        measurement_type = MeasurementType(
            name=d_sensor.measurement_name,
            unit=d_sensor.unit,
            default_format=d_sensor.format,
        )
        return Measurement(
            sensor=Sensor(
                id=d_sensor.sensor_id,
                name=d_sensor.sensor_name,
                location=Location(
                    id=d_sensor.location_id,
                    name=d_sensor.locactio_name,
                ),
                measurements=[measurement_type],
            ),
            measurement=measurement_type,
            date=measurement_date,
            value=measurement_value,
        )


@strawberry.type
class Mutation:
    """GraphQL mutations"""

    add_measurement = strawberry.field(resolver=add_measurement)
