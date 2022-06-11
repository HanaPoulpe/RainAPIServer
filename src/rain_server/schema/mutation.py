"""Defines the mutations"""
import base64
import datetime
import json

from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import sqlalchemy
import strawberry

from .data_schemas import Measurement
from .errors import InvalidSensorError, InvalidSignature
from ..configuration import get_logger, get_database


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

    message = f"{measurement_date}{measurement_date}{measurement_value}{sensor_id}".encode("utf-8")

    logger.info("Connecting to database...")
    with database.engine.connect() as conn:
        d_sensor = conn.execute(query).first()

        if not d_sensor:
            error_msg = f"No matching sensor or measurement found for {sensor_id=}, " \
                        f"{measurement_name=}"
            logger.error(error_msg)
            raise InvalidSensorError(error_msg)

        logger.info("Checking signature...")
        pubkey = load_der_public_key(base64.b64decode(d_sensor.pubkey), default_backend())
        signature = base64.b64decode(signature)
        try:
            pubkey.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        except InvalidSignature as err:
            error_msg = f"Signature verification failed."
            logger.error(error_msg)
            raise err

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





@strawberry.type
class Mutation:
    """GraphQL mutations"""

    add_measurement = strawberry.field(resolver=add_measurement)
