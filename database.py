import psycopg2
from psycopg2.extras import DictCursor
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager

# Defaults assuming local postgres instance
DB_NAME = os.getenv("PG_DB_NAME", "postgres")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(5, 50,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
    return _pool

@contextmanager
def get_connection():
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)
