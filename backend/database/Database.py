"""
MySQL connection management with connection pooling.

When DB_POOL_SIZE > 0 (default 10), a MySQLConnectionPool is created once
at import time. Every get_connection() call borrows from the pool, and the
existing conn.close() calls in dbQueries.py return the connection to the
pool automatically (the mysql-connector-python library handles this).

Set DB_POOL_SIZE=0 in .env to disable pooling and fall back to
one-connection-per-query (the old behaviour).
"""

import logging

import mysql.connector  # type: ignore
from mysql.connector import pooling  # type: ignore

import utils.config as config

_pool: pooling.MySQLConnectionPool | None = None
_pool_size: int = config.BaseConfig.DB_POOL_SIZE


def _init_pool() -> pooling.MySQLConnectionPool | None:
    """Create the connection pool once. Called at module import."""
    if _pool_size < 1:
        logging.info("DB_POOL_SIZE=%s — connection pooling disabled.", _pool_size)
        return None

    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="seng533_pool",
            pool_size=_pool_size,
            pool_reset_session=True,
            host=config.BaseConfig.DATABASE_HOST,
            user=config.BaseConfig.DATABASE_USER,
            password=config.BaseConfig.DATABASE_PASSWORD,
            database=config.BaseConfig.DATABASE_NAME,
            port=config.BaseConfig.DATABASE_PORT,
        )
        logging.info(
            "MySQL connection pool created: pool_size=%s, host=%s, db=%s",
            _pool_size,
            config.BaseConfig.DATABASE_HOST,
            config.BaseConfig.DATABASE_NAME,
        )
        return pool
    except Exception as e:
        logging.warning(
            "Failed to create connection pool (falling back to per-query connections): %s", e
        )
        return None


# Create pool at import time (runs once when Flask starts)
_pool = _init_pool()


class Database:
    @staticmethod
    def get_connection():
        """
        Borrow a connection from the pool, or create a fresh one if
        pooling is disabled / unavailable.

        Callers MUST close the connection in a finally block — this
        returns it to the pool rather than destroying it.
        """
        if _pool is not None:
            return _pool.get_connection()

        # Fallback: no pool
        return mysql.connector.connect(
            host=config.BaseConfig.DATABASE_HOST,
            user=config.BaseConfig.DATABASE_USER,
            password=config.BaseConfig.DATABASE_PASSWORD,
            database=config.BaseConfig.DATABASE_NAME,
            port=config.BaseConfig.DATABASE_PORT,
        )