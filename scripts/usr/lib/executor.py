import psycopg2
from psycopg2.extensions import cursor


class DBExecutor(object):
    def __init__(self, error_handler=print, **kwargs):
        self._options = {str(k).lower(): v for k, v in kwargs.items()}
        self._error_handler = error_handler

    def __enter__(self) -> cursor:
        self._connection = psycopg2.connect(**self._options)
        self._cursor = self._connection.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._cursor.close()
        self._connection.close()

        if not self._error_handler:
            if exc_type:
                raise exc_value
            return
        self._error_handler(exc_value)
