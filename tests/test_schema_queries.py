"""Tests GraphQL Queries"""
import importlib
import unittest

import src.rain_server.schema.query
from src.rain_server.schema.query import get_sensors, get_locations, get_measurements
from src.rain_server.schema.data_schemas import Location, MeasurementType


class TestQueries(unittest.TestCase):
    def setUp(self) -> None:
        """
        Reloads target module
        """
        importlib.reload(src.rain_server.schema.query)

    def test_get_locations(self):
        """
        Test locations query

        Expect:
        - return being a list of Location
        - expect list containing [(test1, test_location), (test2, test_location2)]
        """
        locs = get_locations()
        self.assertIsInstance(
            locs,
            list,
            "get_location should return a list",
        )
        self.assertEqual(
            len(locs),
            2,
            "get_location should return a list of 2 objects"
        )

        for e in [Location("loc1", "test_location"), Location("loc2", "test_location2")]:
            self.assertIn(
                e,
                locs,
                "get_location list is not as expected"
            )

    def test_get_sensors_no_param(self):
        """
        Test sensor query with no param

        Expect:
        - raise a ValueError
        """
        self.assertRaises(ValueError, get_sensors)

    def test_get_sensors_id_and_name(self):
        """
        Test sensor query with both param

        Expect:
        - raise a ValueError
        """
        self.assertRaises(ValueError, get_sensors, location_id="loc1", location_name="test_location")

    def test_get_sensors_id_exists(self):
        """
        Test sensor query with existing sensor id

        Expect:
        - return being a list of sensors
        - expect list containing sensors [{
            id: sen1,
            name: test_sensor,
            location: {id: loc1, name: test_location},
            measurements: [{name: test_measurement, unit: count, is_date: False}]]
        """
        sensor = get_sensors(location_id="loc1")

        self.assertIsInstance(
            sensor,
            list,
            "get_sensors returns a list of sensors",
        )
        self.assertEqual(
            len(sensor),
            1,
            "get_sensors should give a list of 1 sensor",
        )

        sensor = sensor[0]
        self.assertEqual(
            sensor.location,
            Location(location_id="loc1", location_name="test_location"),
            "Location is not matching the expected one",
        )
        self.assertEqual(
            sensor.name,
            "test_sensor",
            "Sensor name is not matching the expected one",
        )
        self.assertEqual(
            sensor.id,
            "sen1"
        )
        self.assertEqual(
            len(sensor.measurements),
            1,
            "Unexpected number of measurements",
        )
        self.assertListEqual(
            sensor.measurements,
            [MeasurementType(name="test_measurement", unit="count", is_date=False)],
        )

    def test_get_sensors_id_not_exists(self):
        """
        Test sensor query with non existing sensor id

        Expect:
        - return being an empty list of sensors
        """
        sensor = get_sensors(location_id="loc1")

        self.assertIsInstance(
            sensor,
            list,
            "get_sensors returns a list of sensors",
        )
        self.assertEqual(
            len(sensor),
            0,
            "get_sensors should give a list of 1 sensor",
        )


if __name__ == "__main__":
    unittest.main()
