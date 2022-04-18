"""Create DB engine from configuration"""
import io
import os.path

import config
import sqlalchemy.engine

from .paths import CONFIG_PATH


def get_db_config() -> config.ConfigurationSet:
    """
    Reads DB configuration from configuration.

    Environment variable must start with RAIN_DB_ and be upper case.
    Configuration file is stored in the default configuration path and name db.json.

    Valid parameters are:
    - dialect: "sqlite"|"postgresql" or any dialect supported by sqlalchemy (other dialect must be manually installed).
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
            cfg.dialect, database=":memory:"
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
