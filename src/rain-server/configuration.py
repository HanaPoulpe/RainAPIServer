"""Manage the application configuration"""
import importlib
import logging
import os
import typing

import environment as environment

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
        self.db_driver = "postgresql"
        self.database: Connection | None = None
        self.logger = logging.getLogger(APPLICATION_ID)

        # PostgreSQL configuration
        self.pg_dbname: str | None = None
        self.pg_user: str | None = None
        self.pg_password: str | None = None
        self.pg_host: str | None = None
        self.pg_port: int | None = None

        self.instance = self

    def check_configuration(self) -> list[str]:
        """
        Checks if all mandatory configuration are set.

        :return: True if all mandatory configuration are set
        """
        mandatory_settings = ["database"]

        return [setting for setting in mandatory_settings if not hasattr(self, setting)]

    def from_environment(self, *, getenv: typing.Callable[[str, typing.Any | None], typing.Any] = os.getenv) -> None:
        """
        Reads configuration from environment variables

        :param getenv: Function that receives an environment variable name and a Python object as default value
        """
        environment_variable = {
            "DB_DRIVER": "db_driver",
            "PG_DBNAME": "pg_dbname",
            "PG_USER": "pg_user",
            "PG_PASSWORD": "pg_password",
            "PG_HOST": "pg_host",
            "PG_PORT": "pg_port",
        }

        for env, cfg in environment_variable.items():
            value = getenv(env, self.__dict__.get(cfg))
            setattr(self, cfg, value)

    def load(self) -> None:
        """
        Loads configuration

        Source Priority is:
        1) environment

        Convert primitive types (eg: str to int, etc...)
        Create complex types (eg: db connections)
        """
        self.from_environment()

        convert_map = {
            "pg_port": int,
        }
        for cfg, t in convert_map.items():
            value = getattr(self, cfg)
            if value and isinstance(value, t):
                continue
            setattr(self, cfg, t(value))

        self.create_connection()

    def create_connection(self) -> None:
        """
        Creates a database connection.

        - Loads the driver from self.db_driver
        - Creates a connection from the driver
        """
        self.logger.info("Loading database driver: %s", self.db_driver)

        try:
            db_driver = importlib.import_module(f".database.{self.db_driver}")
        except ImportError as err:
            self.logger.error("Could not load database driver %s", err, exc_info=err)
            raise err

        if not hasattr(db_driver, "DRIVER"):
            self.logger.error("Database driver not found")
            raise ImportError(f"Module %s has no 'DRIVER' attribute...", db_driver)

        self.database = db_driver.DRIVER()  # type: ignore

        if hasattr(db_driver, "setup"):
            self.logger.info("Checking database setup...")
            db_driver.setup()
            self.logger.info("Database setup")


def get_configuration() -> __Configuration:
    """Returns the configuration"""
    if __Configuration.instance:
        return __Configuration.instance

    configuration = __Configuration()

    configuration.load()
    missing = configuration.check_configuration()
    if not missing:
        raise RuntimeError(f"Missing mandatory settings: {repr(missing)}", missing)

    return configuration
