"""Create DB engine from configuration"""
import io
import os.path

import config
import sqlalchemy.dialects.sqlite
import sqlalchemy.engine
import sqlalchemy.orm

from .paths import CONFIG_PATH


def get_db_config() -> config.ConfigurationSet:
    """
    Reads DB configuration from configuration.

    Environment variable must start with RAIN_DB_ and be upper case.
    Configuration file is stored in the default configuration path and name db.json.

    Valid parameters are:
    - dialect: "sqlite"|"postgresql" or any dialect supported by sqlalchemy
    (other dialect must be manually installed).
    - engine: None or any engine supported by sqlalchemy (must be manually installed).
    - user: DB Username if any.
    - password: DB password if any.
    - host: DB Host if any.
    - port: DB port if not default.
    - schema: DB schema/logical DB.
    - log_queries: True/False Display queries in logs? Default is False.

    Priority is:
    1. Environment variables
    2. Configuration file
    3. Default configuration

    :return: ConfigurationSet
    """
    default = {
        "dialect": "sqlite",
        "log_queries": False,
    }

    try:
        json = open(os.path.join(CONFIG_PATH, "db.json"), "r")
    except FileNotFoundError:
        # Ignores the configuration if the file do not exist.
        json = io.StringIO("{}")

    return config.ConfigurationSet(
        config.config_from_env(prefix="RAIN_DB"),
        config.config_from_json(json, read_from_file=False),
        config.config_from_dict(default),
    )


def get_db_url(cfg: config.ConfigurationSet) -> sqlalchemy.engine.URL:
    """Creates the database URL from configuration"""
    if cfg.dialect == "sqlite":
        return sqlalchemy.engine.URL(
            cfg.dialect, database=":memory:",
        )

    return sqlalchemy.engine.URL(
        cfg.dialect + (f"+{cfg.get('engine')}" if "engine" in cfg else ""),
        username=cfg.get('user'),
        password=cfg.get('password'),
        host=cfg.get('host'),
        port=cfg.get_int("port") if "port" in cfg else None,
        database=cfg.get("schema"),
    )


def get_engine() -> sqlalchemy.engine.Engine:
    """Returns the DB Engine"""
    cfg = get_db_config()
    url = get_db_url(cfg)

    return sqlalchemy.create_engine(
        url=url,
        echo=cfg.get_bool("log_queries"),
        future=True,
    )


class DataBase:
    """
    Defines all database tables for the engine.
    """

    def __init__(self, engine: sqlalchemy.engine.Engine):
        self.engine = engine
        self.meta = sqlalchemy.MetaData()
        self.__create_sensors()

    def __create_sensors(self):
        """Creates the sensor table."""
        self._sensors = sqlalchemy.Table(
            "o_sensors",
            self.meta,
            sqlalchemy.Column("sensor_id", sqlalchemy.String, sqlalchemy.PrimaryKeyConstraint),
            sqlalchemy.Column("sensor_name", sqlalchemy.String, sqlalchemy.UniqueConstraint),
            sqlalchemy.Column("location_id", sqlalchemy.String),
            sqlalchemy.Column("pubkey", sqlalchemy.String),
            sqlalchemy.Column("is_active", sqlalchemy.CHAR),
            sqlalchemy.Column("d_created_date_utc", sqlalchemy.DateTime),
            sqlalchemy.Column("d_updated_date_utc", sqlalchemy.DateTime),
        )

    def __create_measurements(self):
        """Creates the measurement table."""
        self._measurements = sqlalchemy.Table(
            "d_measurements",
            self.meta,
            sqlalchemy.Column("location_id", sqlalchemy.String),
            sqlalchemy.Column("sensor_id", sqlalchemy.String),
            sqlalchemy.Column("measurement_name", sqlalchemy.String),
            sqlalchemy.Column("unit", sqlalchemy.String),
            sqlalchemy.Column("measurement_datetime", sqlalchemy.DateTime),
            sqlalchemy.Column("measurement_value", sqlalchemy.Numeric),
            sqlalchemy.Column("d_created_date_utc", sqlalchemy.DateTime),
            sqlalchemy.Column("d_updated_date_utc", sqlalchemy.DateTime),
        )

    def __create_measurement_types(self):
        """Create the measurement types table."""
        self._measurement_types = sqlalchemy.Table(
            "o_measurement_types",
            self.meta,
            sqlalchemy.Column(
                "measurement_name",
                sqlalchemy.String,
                sqlalchemy.PrimaryKeyConstraint,
            ),
            sqlalchemy.Column("unit", sqlalchemy.String),
            sqlalchemy.Column("string_format", sqlalchemy.String),
            sqlalchemy.Column("d_created_date_utc", sqlalchemy.DateTime),
            sqlalchemy.Column("d_updated_date_utc", sqlalchemy.DateTime),
        )

    def __create_sensors_measurements(self):
        """Links sensors to measurements types"""
        self._sensor_measurements = sqlalchemy.Table(
            "r_sensor_measurements",
            self.meta,
            sqlalchemy.Column("sensor_id", sqlalchemy.String, sqlalchemy.PrimaryKeyConstraint),
            sqlalchemy.Column(
                "measurement_name",
                sqlalchemy.String,
                sqlalchemy.PrimaryKeyConstraint,
            ),
            sqlalchemy.Column("is_active", sqlalchemy.CHAR),
            sqlalchemy.Column("d_created_date_utc", sqlalchemy.DateTime),
            sqlalchemy.Column("d_updated_date_utc", sqlalchemy.DateTime),
        )

    def setup(self):
        """Create all required tables."""
        self.meta.create_all(self.engine)

    @property
    def sensors(self) -> sqlalchemy.Table:
        return self._sensors

    @property
    def measurements(self) -> sqlalchemy.Table:
        return self._measurements

    @property
    def measurement_types(self) -> sqlalchemy.Table:
        return self._measurement_types

    @property
    def sensor_measurements(self) -> sqlalchemy.Table:
        return self._sensor_measurements

    def select_sensors_measurement(self, sensor_id: str, measurement_name: str):
        return self.sensors.select().where(
            sqlalchemy.and_(
                self.sensors.c.sensor_id == sensor_id,
                self.sensors.c.is_active != "N",
            )
        ).join(
            self.sensor_measurements,
            sqlalchemy.and_(
                self.sensors.c.sensor_id == self.sensor_measurements.c.sensor_id,
                self.sensor_measurements.c.is_active != "N",
            )
        ).join(
            self.measurement_types,
            sqlalchemy.and_(
                self.sensor_measurements.c.measurement_name == measurement_name,
                self.measurement_types.c.measurement_name ==
                self.sensor_measurements.c.measurement_name,
            )
        )

    def get_session(self) -> sqlalchemy.orm.Session:
        """Creates a new database session."""
        return sqlalchemy.orm.Session(self.engine)


def get_database() -> DataBase:
    """Creates a database."""
    return DataBase(get_engine())
