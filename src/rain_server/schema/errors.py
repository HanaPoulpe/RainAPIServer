"""
Defines schema related errors

Error created there will be sent to the client
"""


class InvalidSensorError(Exception):
    """Invalid Sensor Error"""

    pass


class InvalidMeasurementError(Exception):
    """Invalid Measurement Error"""

    pass


class AuthenticationError(Exception):
    """Authentication issues."""

    pass
