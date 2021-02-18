from os import getenv


DBNAME = getenv('DBNAME', 'target_db')
DBUSER = getenv('DBUSER', 'postgres')
DBPASS = getenv('DBPASS', 'pass')
DBHOST = getenv('DBHOST', 'localhost')
DBPORT = getenv('DBPORT', '5555')


DATABASE = {
    'dbname': DBNAME,
    'user': DBUSER,
    'password': DBPASS,
    'host': DBHOST,
    'port': DBPORT
}
