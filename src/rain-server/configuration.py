"""Manage the application configuration"""
import logging
import typing

from .database import Connection
from .version import APPLICATION_ID


class __Configuration:
    """
    Configuration class for the application.

    Use the get_configuration method.
    """
    instance: typing.Optional['__Configuration'] = None

    def __init__(self):
        """Set up the default configuration."""
        self.database: Connection | None = None
        self.logger = logging.getLogger(APPLICATION_ID)

        # PostgreSQL configuration
        self.pg_schema: str | None = None

        self.instance = self

    def check_configuration(self) -> list[str]:
        """
        Checks if all mandatory configuration are set.

        :return: True if all mandatory configuration are set
        """
        mandatory_settings = ["database"]

        return [setting for setting in mandatory_settings if not hasattr(self, setting)]


def get_configuration() -> __Configuration:
    """Returns the configuration"""
    if __Configuration.instance:
        return __Configuration.instance

    configuration = __Configuration()

    missing = configuration.check_configuration()
    if not missing:
        raise RuntimeError(f"Missing mandatory settings: {repr(missing)}", missing)

    return configuration
