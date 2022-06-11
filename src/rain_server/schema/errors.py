"""
Defines schema related errors

Error created there will be sent to the client
"""
from cryptography.exceptions import InvalidSignature # noqa


class InvalidSensorError(Exception):
    """Invalid Sensor Error"""

    pass


class InvalidMeasurementError(Exception):
    """Invalid Measurement Error"""

    pass
