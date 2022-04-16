"""
Defines schema related errors

Error created there will be sent to the client
"""


class InvalidSenorError(Exception):
    pass


class InvalidSignatureError(Exception):
    pass


class InvalidMeasurementError(Exception):
    pass
