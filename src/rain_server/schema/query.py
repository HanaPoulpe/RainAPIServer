"""Defines queries"""
import strawberry

from .data_schemas import Location, Sensor, Measurement


def get_locations() -> list[Location]:
    """Returns a list of location"""
    raise NotImplementedError()


def get_sensors(*, location_name: str | None = None, location_id: str = None) -> list[Sensor]:
    """
    Returns a list of sensors for specified location

    Only one of the parameters can be specified.

    :param location_name: Name of the location to list related sensors
    :param location_id: Id of the location to list related sensors
    """
    raise NotImplementedError()


def get_measurements(
        *,
        measurements: list[str],
        sensor_ids: list[str] | None = None,
        location_names: list[str] | None = None,
        location_ids: list[str] | None = None,
        start_time: str = "TODAY",
        end_time: str = "TODAY",
) -> list[Measurement]:
    """
    Read measurements

    Location must be provided only by name or ids

    Date are provided:
    - as ISO8601 formatted strings for absolute value.
    - "-nP" where:
     - "n" is the number of periods
     - "P" is:
      - "m" for minutes
      - "h" for hours
      - "d" for days
      - "w" for weeks
     - "TODAY" for start/end of day (GMT)
     - "NOW" for current time. Note that for end_time, "TODAY" and "NOW" are equivalent

    When both start_time and end_time are set to "NOW", returns the last measurements

    :param measurements: list of measurement names
    :param sensor_ids: list of sensor ids
    :param location_names: list of location names
    :param location_ids: list of location ids
    :param start_time: start time
    :param end_time: end time
    """
    raise NotImplementedError()


@strawberry.type
class Query:
    locations: list[Location] = strawberry.field(resolver=get_locations)
    sensors: list[Sensor] = strawberry.field(resolver=get_sensors)
    measurements: list[Measurement] = strawberry.field(resolver=get_measurements)
