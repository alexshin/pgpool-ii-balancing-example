#!/usr/bin/env python

import click
import os
import sys
import subprocess
from scripts.etc import settings
from scripts.usr.lib.executor import DBExecutor

_CLEAR_DB_QUERIES = [
    'DROP SCHEMA public CASCADE',
    'CREATE SCHEMA public',
    'GRANT ALL ON SCHEMA public TO postgres',
    'GRANT ALL ON SCHEMA public TO public',
]


@click.command()
@click.option('--filename', default='./assets/pagila-insert-data.sql', help='Dump filename')
@click.option('--dbhost', default=settings.DBHOST, help='DBHost')
@click.option('--dbport', default=settings.DBPORT, help='DBPort')
@click.option('--dbuser', default=settings.DBUSER, help='DBUser')
@click.option('--dbpass', default=settings.DBPASS, help='DBPass')
@click.option('--dbname', default=settings.DBNAME, help='DBName')
def do_cmd(filename, dbhost, dbport, dbuser, dbpass, dbname):
    err_handler = lambda e: click.echo(e, err=True)
    """Command to load data from sql-dump"""
    db_executor = DBExecutor(error_handler=err_handler, dbname=dbname, user=dbuser, password=dbpass,
                             host=dbhost, port=dbport)

    if not os.path.exists(filename):
        err_handler(f'File with dump has not found')
        exit(1)

    with db_executor as cursor:
        click.echo('Clearing DB')
        for q in _CLEAR_DB_QUERIES:
            formatted_query = q.format(dbname=dbname, dbuser=dbuser)
            cursor.execute(formatted_query)
            click.echo(f' [+] {formatted_query}')

    click.echo('Loading Dump')
    p1 = subprocess.Popen([
        "psql",
        "-d", dbname,
        "-h", dbhost,
        "-p", dbport,
        "-U", dbuser,
        # "-W", dbpass,
        "-f", filename
    ], stdout=subprocess.DEVNULL, env={'PGPASSWORD': dbpass, **os.environ})
    p1.wait()

    # Load dumps
    click.echo('Done')


if __name__ == '__main__':
    do_cmd()
