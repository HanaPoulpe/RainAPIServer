"""Defines steps for database setup and upgrade."""
import os.path

import psycopg.errors

from ...configuration import get_configuration
from ...version import APPLICATION_ID
from . import PGConnection


CURRENT_VERSION = "0.1.20220411"


def check_tables(*, con: PGConnection) -> str | None:
    """
    Checks if the tables are created.

    Will check the o_applications tables for existence of the last version of the application.

    :param con: Connection to the database.
    :return: Version of the tables or empty string.
    """
    logger = get_configuration().logger

    logger.info("Checking o_applications...")
    if not table_exists("o_applications"):
        logger.warning("Application tables not found.")
        return None

    logger.info("Checking application tables version...")
    cur = con.cursor().cursor

    try:
        cur.execute(
            f"SELECT application_id, table_version FROM o_applications WHERE application_id = '{APPLICATION_ID}'")
        ver = cur.fetchone()
        if ver:
            logger.info("Found application version %s", ver["table_version"])
            return ver["table_version"]
        logger.warning("Application version not found.")
        return None
    except psycopg.errors.Error as err:
        logger.error("Error while reading application version: %s", repr(err), exc_info=err)
        return None


def table_exists(table_name: str, *, con: PGConnection) -> bool:
    """Returns if the table exists in the database"""
    cur = con.cursor().cursor

    cur.execute(f"SELECT table_name FROM pg_tables WHERE table_name = '{table_name}' "
                f"AND schemaname = '{get_configuration().pg_dbname}'")
    return not not cur.rowcount


def full_install(*, con: PGConnection) -> None:
    """
    Creates all the tables required.

    - Loads script file
    - Execute statements into the database
    """
    path = os.path.dirname(__file__)
    with open(os.path.join(path, 'create.sql'), 'r') as fp:
        sql = fp.read()

    cur = con.cursor().cursor
    cur.execute(sql)


def setup():
    """
    Prepare the database if needed

    - Check the tables version
    - If no version is installed, create all the tables
    - If an outdated version is installed, updates the tables
    - If the tables are the last version, do nothing
    """
    con: PGConnection = get_configuration().database  # type: ignore

    current_version = check_tables(con=con)

    if not current_version:
        full_install(con=con)
    # No update process ATM, it's the first version

    return None
