"""Manages database exceptions"""


class DatabaseException(Exception):
    """Basic database exception"""
    pass


class ConnectionException(DatabaseException):
    """Exception related to database connection"""
    pass


class DataValidationException(DatabaseException):
    """Exception related to data validation"""
    pass
