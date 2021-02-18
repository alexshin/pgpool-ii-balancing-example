import psycopg2
from psycopg2.extensions import cursor as CursorFn
from pypika import Query


def do_entrypoint(cursor: CursorFn):
    for i in range(1000):
        q = Query.from_('users').select('*').limit(15)
        cursor.execute(q.get_sql())
        print(f'Iteration {i}')


if __name__ == '__main__':
    conn = psycopg2.connect(dbname='target_db', user='user', password='pass', host='localhost', port='5555')
    cur = conn.cursor()

    do_entrypoint(cur)

    cur.close()
    conn.close()
