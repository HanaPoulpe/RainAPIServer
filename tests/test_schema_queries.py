"""Tests GraphQL Queries"""
import datetime
import importlib
import unittest

import src.rain_server.schema.query
from src.rain_server.schema.data_schemas import (Location, Measurement,
                                                 MeasurementType)
from src.rain_server.schema.query import (get_locations, get_measurements,
                                          get_sensors)


class TestQueries(unittest.TestCase):
    def setUp(self) -> None:
        """
        Reloads target module
        Patch datetime.datetime.utcnow()
        Patch datetime.date.today()
        """
        importlib.reload(src.rain_server.schema.query)
        # ToDo: Patches

    def tearDown(self) -> None:
        """
        Removes Patches
        """
        pass  # ToDo: Patches

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
        Test sensor query with not existing location id

        Expect:
        - return being an empty list of sensors
        """
        sensor = get_sensors(location_id="no_loc")

        self.assertIsInstance(
            sensor,
            list,
            "get_sensors returns a list of sensors",
        )
        self.assertListEqual(
            sensor,
            [],
            "get_sensors should give an empty list.",
        )

    def test_get_measurements_no_input(self):
        """
        Test empty measurement query

        Expect:
        - return an empty list
        """
        measurements = get_measurements(
            measurements=[],
        )

        self.assertIsInstance(measurements, list, "get_measurements should return an empty list.")
        self.assertListEqual(measurements, [])

    def test_get_measurements_no_empty(self):
        """
        Test measurement query with no matching measurements

        expect:
        - return an empty list
        """
        measurements = get_measurements(
            measurements=["no_values"],
        )

        self.assertIsInstance(measurements, list, "get_measurements should return an empty list.")
        self.assertListEqual(measurements, [])

    def test_get_measurements_not_empty(self):
        """
        Test measurements query with matching measurements

        expect:
        - [(Sensor("sen1"), MeasurementType("test_measurement"), 2022-04-30 00:00:00.0000, 123),
           (Sensor("sen2"), MeasurementType("test_measurement"), 2022-04-30 01:01:01.0000, 456)]
        """
        measurements = get_measurements(
            measurements=["test_measurement"],
        )

        self.assertIsInstance(measurements, list, "get_measurements should return a list.")
        self.assertEqual(
            len(measurements),
            2,
            "get_measurements should return 2 measurements."
        )

        measurement = measurements[0]
        self.assertEqual(measurement.sensor.id, "sen1")
        self.assertEqual(measurement.measurement.name, "test_measurement")
        self.assertEqual(measurement.date, datetime.datetime(2022, 4, 30, 0, 0, 0, 0))
        self.assertEqual(measurement.value, 123)

        measurement = measurements[1]
        self.assertEqual(measurement.sensor.id, "sen2")
        self.assertEqual(measurement.measurement.name, "test_measurement")
        self.assertEqual(measurement.date, datetime.datetime(2022, 4, 30, 1, 1, 1, 0))
        self.assertEqual(measurement.value, 456)

    def test_get_measurements_sensor_filter(self):
        """
        Test measurement query for sensor sen1

        expect:
        - [(Sensor("sen1"), MeasurementType("test_measurement"), 2022-04-30 00:00:00.0000, 123)]
        """
        measurements = get_measurements(
            measurements=["test_measurement"],
            sensor_ids=["sen1"],
        )

        self.assertIsInstance(measurements, list, "get_measurements should return a list.")
        self.assertEqual(
            len(measurements),
            1,
            "get_measurements should return 1 measurements."
        )

        measurement = measurements[0]
        self.assertEqual(measurement.sensor.id, "sen1")
        self.assertEqual(measurement.measurement.name, "test_measurement")
        self.assertEqual(measurement.date, datetime.datetime(2022, 4, 30, 0, 0, 0, 0))
        self.assertEqual(measurement.value, 123)

    def test_get_measurements_location_name_filter(self):
        """
        Test measurement query for location name = test_location

        expect:
        - [(Sensor("sen1"), MeasurementType("test_measurement"), 2022-04-30 00:00:00.0000, 123)]
        """
        measurements = get_measurements(
            measurements=["test_measurement"],
            location_names=["test_location"],
        )

        self.assertIsInstance(measurements, list, "get_measurements should return a list.")
        self.assertEqual(
            len(measurements),
            1,
            "get_measurements should return 1 measurements."
        )

        measurement = measurements[0]
        self.assertEqual(measurement.sensor.id, "sen1")
        self.assertEqual(measurement.measurement.name, "test_measurement")
        self.assertEqual(measurement.date, datetime.datetime(2022, 4, 30, 0, 0, 0, 0))
        self.assertEqual(measurement.value, 123)

    def test_get_measurements_location_id_filter(self):
        """
        Test measurement query for location id = test_location

        expect:
        - [(Sensor("sen1"), MeasurementType("test_measurement"), 2022-04-30 00:00:00.0000, 123)]
        """
        measurements = get_measurements(
            measurements=["test_measurement"],
            location_ids=["loc1"],
        )

        self.assertIsInstance(measurements, list, "get_measurements should return a list.")
        self.assertEqual(
            len(measurements),
            1,
            "get_measurements should return 1 measurements."
        )

        measurement = measurements[0]
        self.assertEqual(measurement.sensor.id, "sen1")
        self.assertEqual(measurement.measurement.name, "test_measurement")
        self.assertEqual(measurement.date, datetime.datetime(2022, 4, 30, 0, 0, 0, 0))
        self.assertEqual(measurement.value, 123)

    def test_get_measurements_location_id_and_name_filter(self):
        """
        Test measurement query with location id and location name

        expect:
        - raises ValueError
        """
        self.assertRaises(
            ValueError,
            get_measurements,
            measurements=["test_measurement"],
            location_ids=["loc1"],
            location_names=["test_location"],
        )

    def test_get_measurements_invalid_period(self):
        """
        Test multiple invalid periods:
        - Invalid start_time string
        - Invalid end_time string
        - start_time > end_time

        expect:
        - raises ValueError
        """
        params = [
            {"start_time": "invalid"},
            {"end_time": "invalid"},
            {
                "start_time": "NOW",
                "end_time": "-1d",
            },
        ]

        for p in params:
            self.assertRaises(
                ValueError,
                get_measurements,
                measurements=["test_measurement"],
                **p,
            )


if __name__ == "__main__":
    unittest.main()
