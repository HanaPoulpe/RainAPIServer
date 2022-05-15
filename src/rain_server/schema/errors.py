"""
Defines schema related errors

Error created there will be sent to the client
"""


class InvalidSenorError(Exception):
    """Invalid Sensor Error"""

    pass


class InvalidSignatureError(Exception):
    """Invalid Signature Error"""

    pass


class InvalidMeasurementError(Exception):
    """Invalid Measurement Error"""

    pass
