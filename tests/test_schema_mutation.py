"""Test schema mutations"""
import base64
import importlib
import typing
import unittest
from datetime import datetime

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

import src.rain_server.schema.mutation
from src.rain_server.configuration import get_database
from src.rain_server.schema.mutation import add_measurement


class TestMutations(unittest.TestCase):
    def setUp(self):
        """
        Creates RSA Keys
        Reloads target module
        Creates database in local SQLite database
        """
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        importlib.reload(src.rain_server.schema.mutation)

        self.database = get_database()
        self.database.locations.insert(
            location_id='loc1',
            location_name="test location",
            d_created_date_utc=datetime.utcnow(),
            d_updated_date_utc=datetime.utcnow(),
        )
        self.database.sensors.insert(
            sensors_id="test_sensor",
            sensor_name="test sensor",
            location_id="loc1",
            pubkey=base64.b64encode(pem),
            is_active="Y",
            d_created_date_utc=datetime.utcnow(),
            d_updated_date_utc=datetime.utcnow(),
        )

    def sign(self, message: dict[str, typing.Any]) -> str:
        """
        Signs the message using the RSA key
        """
        ordered_keys = list(message.keys())
        ordered_keys.sort()

        message_str = ''.join(message[k] if isinstance(message[k], str) else str(message[k])
                              for k in ordered_keys)

        signed = self.private_key.sign(
            message_str.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        return base64.b64encode(signed).decode('utf-8')

    def assertTableItems(self, table_name: str, expected_items: list[dict[str, typing.Any]]):
        raise NotImplementedError()

    def test_add_measurement_invalid_sensor(self):
        """
        Trys to add a measurement to an invalid sensor.

        The mutation returns an InvalidSensorError.
        No data should be inserted in the measurement table
        """
        from src.rain_server.schema.errors import InvalidSensorError
        message = {
            "sensor_id": "invalid",
            "measurement_name": "unittest_count",
            "measurement_date": datetime(2022, 1, 1, 0, 0, 0),
            "measurement_value": 1,
        }
        self.assertRaises(
            InvalidSensorError,
            add_measurement,
            signature=self.sign(message),
            **message,
        )
        self.assertTableItems("d_measurements", [])

    def test_add_measurement_invalid_signature(self):
        """
        Trys to add a measurement with an invalid signature.

        The mutation should return an invalid signature
        No data should be inserted in the measurement table
        """
        from src.rain_server.schema.errors import AuthenticationError

        signatures = ["not a base64", base64.b64encode(b"invalid signature").decode("utf-8")]

        for s in signatures:
            self.assertRaises(
                AuthenticationError,
                add_measurement,
                sensor_id="test_sensor",
                measurement_name="unittest_count",
                measurement_date=datetime(2022, 1, 1, 0, 0, 0),
                measurement_value=1,
                signature=s,
            )
            self.assertTableItems("d_measurements", [])

    def test_add_measurement_invalid_measurement(self):
        """
        Trys to add a measurement with an invalid measurement name

        The mutation should return an invalid measurement
        No data should be inserted in the measurement table
        """
        from src.rain_server.schema.errors import InvalidMeasurementError
        message = {
            "sensor_id": "test_sensor",
            "measurement_name": "invalid",
            "measurement_date": datetime(2022, 1, 1, 0, 0, 0),
            "measurement_value": 1,
        }
        self.assertRaises(
            InvalidMeasurementError,
            add_measurement,
            signature=self.sign(message),
            **message,
        )
        self.assertTableItems("d_measurements", [])

    def test_add_measurement(self):
        """
        Trys to add a measurement with an invalid measurement name

        The mutation should return an invalid measurement
        No data should be inserted in the measurement table
        """
        from src.rain_server.schema.data_schemas import (Location, Measurement,
                                                         MeasurementType,
                                                         Sensor)
        message = {
            "sensor_id": "test_sensor",
            "measurement_name": "unittest_count",
            "measurement_date": datetime(2022, 1, 1, 0, 0, 0),
            "measurement_value": 1,
        }
        added = add_measurement(
            signature=self.sign(message),
            **message,
        )

        self.assertEqual(
            added,
            Measurement(
                sensor=Sensor(
                    id="test_sensor",
                    name="test_sensor_name",
                    location=Location(
                        id="test_location",
                        name="test_location_name",
                    ),
                    measurements=[MeasurementType("unittest_count", "count", False)],
                ),
                measurement_type=MeasurementType("unittest_count", "count", False),
                value=1.0
            ),
        )

        self.assertTableItems(
            "d_measurements",
            [
                {
                    "sensor_id": "test_sensor",
                    "measurement_name": "unittest_count",
                    "measurement_date": datetime(2022, 1, 1, 0, 0, 0),
                    "measurement_value": 1,
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
