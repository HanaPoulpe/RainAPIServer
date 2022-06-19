"""Create DB engine from configuration"""
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
        with open(os.path.join(CONFIG_PATH, "db.json"), "r") as fp:
            json_file = fp.read()
    except FileNotFoundError:
        # Ignores the configuration if the file do not exist.
        json_file = "{}"

    return config.ConfigurationSet(
        config.config_from_env(prefix="RAIN_DB"),
        config.config_from_json(json_file, read_from_file=False),
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
    """Defines all database tables for the engine."""

    def __init__(self, engine: sqlalchemy.engine.Engine):
        """
        Setups database engine.

        :param engine:SQLAlchemy engine
        """
        self.engine = engine
        self.meta = sqlalchemy.MetaData()
        self.__create_sensors()
        self.__create_locations()
        self.__create_measurements()
        self.__create_measurement_types()
        self.__create_sensors_measurements()
        self.setup()

    def __create_sensors(self):
        """Creates the sensor table."""
        self._sensors = sqlalchemy.Table(
            "o_sensors",
            self.meta,
            sqlalchemy.Column("sensor_id", sqlalchemy.String, primary_key=True),
            sqlalchemy.Column("sensor_name", sqlalchemy.String),
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
                primary_key=True,
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
            sqlalchemy.Column("sensor_id", sqlalchemy.String, primary_key=True),
            sqlalchemy.Column(
                "measurement_name",
                sqlalchemy.String,
                primary_key=True,
            ),
            sqlalchemy.Column("is_date", sqlalchemy.CHAR),
            sqlalchemy.Column("d_created_date_utc", sqlalchemy.DateTime),
            sqlalchemy.Column("d_updated_date_utc", sqlalchemy.DateTime),
        )

    def __create_locations(self):
        """Locations list"""
        self._locations = sqlalchemy.Table(
            "d_locations",
            self.meta,
            sqlalchemy.Column("location_id", sqlalchemy.String, primary_key=True),
            sqlalchemy.Column("location_name", sqlalchemy.String),
            sqlalchemy.Column("d_created_date_utc", sqlalchemy.DateTime),
            sqlalchemy.Column("d_updated_date_utc", sqlalchemy.DateTime),
        )

    def setup(self):
        """Create all required tables."""
        self.meta.create_all(self.engine)

    @property
    def sensors(self) -> sqlalchemy.Table:
        """Sensors table."""
        return self._sensors

    @property
    def measurements(self) -> sqlalchemy.Table:
        """Measurements table."""
        return self._measurements

    @property
    def measurement_types(self) -> sqlalchemy.Table:
        """Measurement types table."""
        return self._measurement_types

    @property
    def sensor_measurements(self) -> sqlalchemy.Table:
        """Measurements table."""
        return self._sensor_measurements

    @property
    def locations(self) -> sqlalchemy.Table:
        """Location table."""
        return self._locations

    def select_sensors_measurement(self, sensor_id: str, measurement_name: str):
        """
        Retrieve sensor, measurements and location details.

        :param sensor_id: Sensor ID
        :param measurement_name: Name for the measurement
        :return: SQLAlchemy Select statement
        """
        return self.sensors.select().where(
            sqlalchemy.and_(
                self.sensors.c.sensor_id == sensor_id,
                self.sensors.c.is_active != "N",
            ),
        ).join(
            self.sensor_measurements,
            self.sensors.c.sensor_id == self.sensor_measurements.c.sensor_id,
        ).join(
            self.measurement_types,
            sqlalchemy.and_(
                self.sensor_measurements.c.measurement_name == measurement_name,
                self.measurement_types.c.measurement_name
                == self.sensor_measurements.c.measurement_name,  # noqa
            ),
        ).join(
            self.locations,
            self.sensors.c.location_id == self.locations.c.location_id,
        )

    def get_session(self) -> sqlalchemy.orm.Session:
        """Creates a new database session."""
        return sqlalchemy.orm.Session(self.engine)


def get_database() -> DataBase:
    """Creates a database."""
    return DataBase(get_engine())
