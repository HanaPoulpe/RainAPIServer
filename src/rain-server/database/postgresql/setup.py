"""Defines steps for database setup and upgrade."""
import psycopg.errors

from ...configuration import get_configuration
from ...version import APPLICATION_ID
from . import PGConnection


CURRENT_VERSION = "0.0"


def check_tables(*, con: PGConnection) -> str:
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
        return ""

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
        return ""
    except psycopg.errors.Error as err:
        logger.error("Error while reading application version: %s", repr(err), exc_info=err)
        return ""


def table_exists(table_name: str, *, con: PGConnection) -> bool:
    """Returns if the table exists in the database"""
    cur = con.cursor().cursor

    cur.execute(f"SELECT table_name FROM pg_tables WHERE table_name = '{table_name}' "
                f"AND schemaname = '{get_configuration().pg_schema}'")
    return not not cur.rowcount


def full_install() -> None:
    """Creates all the tables required."""
