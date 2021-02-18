import time
from unittest import TestCase
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from scripts.etc import settings
from scripts.usr.lib.executor import DBExecutor


class BasicOpsTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db_executor = DBExecutor(error_handler=None, dbname=settings.DBNAME, user=settings.DBUSER,
                                     password=settings.DBPASS, host=settings.DBHOST, port=settings.DBPORT)

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test__select_must_work(self):
        with self.db_executor as cur:
            cur.execute('SELECT film_id FROM film LIMIT 100')
            results = cur.fetchall()
            self.assertEqual(100, len(results))

    def test__insert_must_work(self):
        with self.db_executor as cursor:
            cursor.execute('INSERT INTO country (country) VALUES (\'Test country 1\') RETURNING country_id')
            self.assertIsNotNone(cursor.fetchone()[0])

            cursor.execute('DELETE FROM country WHERE country = \'Test country 1\'')
            self.assertGreater(cursor.rowcount, 0)

    def test__transaction_must_work(self):
        with self.db_executor as cursor:
            with cursor as cur:
                cur.execute('INSERT INTO country (country) VALUES (\'Test country 1\') RETURNING country_id')
                self.assertIsNotNone(cursor.fetchone()[0])

                cur.execute('DELETE FROM country WHERE country = \'Test country 1\'')
                self.assertGreater(cursor.rowcount, 0)

    def test__sequential_reading_must_not_work(self):
        # This value must be relatively big to represent replication lag
        _NUM_ROWS = 1000

        with self.db_executor as cursor:
            # That's important because Psycopg2 isolate writing instructions
            cursor.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            # Just cleaning data if previous test execution was failed
            cursor.execute('DELETE FROM country WHERE country LIKE \'Test country 1%\'')
            time.sleep(1)  # Waiting a couple of seconds to allow replication does its work

            # Getting initial count of rows
            cursor.execute('SELECT COUNT(*) FROM country')
            initial_num = cursor.fetchone()[0]
            self.assertGreater(initial_num, 0)

            # Sending a long query with huge payload
            _sql_values = ', '.join([f'(\'Test country 1 __ {i}\')' for i in range(_NUM_ROWS)])
            sql = f'INSERT INTO country (country) VALUES{_sql_values}'
            cursor.execute(sql)
            self.assertEqual(_NUM_ROWS, cursor.rowcount, msg=f'We have just inserted {_NUM_ROWS} countries')

            # For the first time it must return wrong result
            # Because SELECT query is being executed across one of READ replica
            # which has not got updates
            cursor.execute('SELECT COUNT(*) FROM country')
            after_insert_sum = cursor.fetchone()[0]
            self.assertGreater(initial_num + _NUM_ROWS, after_insert_sum)

            # Sleeping for a couple of seconds and checking again
            # It should work because 5 seconds seems to be enough to
            # finish replication
            time.sleep(5)
            cursor.execute('SELECT COUNT(*) FROM country')
            after_insert_sum = cursor.fetchone()[0]
            self.assertEqual(initial_num + _NUM_ROWS, after_insert_sum)

            # Removing all created rows
            cursor.execute('DELETE FROM country WHERE country LIKE \'Test country 1%\'')
            self.assertEqual(_NUM_ROWS, cursor.rowcount)

    def test__sequential_reading_within_transaction_must_work(self):
        # This value must be relatively big to represent replication lag
        _NUM_ROWS = 1000

        with self.db_executor as cur:
            # This will start a transaction
            with cur as cursor:
                # Just cleaning data if previous test execution was failed
                cursor.execute('DELETE FROM country WHERE country LIKE \'Test country 1%\'')

                # Getting initial count of rows
                cursor.execute('SELECT COUNT(*) FROM country')
                initial_num = cursor.fetchone()[0]
                self.assertGreater(initial_num, 0)

                # Sending a long query with huge payload
                _sql_values = ', '.join([f'(\'Test country 1 __ {i}\')' for i in range(_NUM_ROWS)])
                sql = f'INSERT INTO country (country) VALUES{_sql_values}'
                cursor.execute(sql)
                self.assertEqual(_NUM_ROWS, cursor.rowcount)

                # Result must be exactly we are expecting to get
                cursor.execute('SELECT COUNT(*) FROM country')
                after_insert_sum = cursor.fetchone()[0]
                self.assertEqual(initial_num + _NUM_ROWS, after_insert_sum)

                # Removing all created rows
                cursor.execute('DELETE FROM country WHERE country LIKE \'Test country 1%\'')
                self.assertEqual(_NUM_ROWS, cursor.rowcount)
