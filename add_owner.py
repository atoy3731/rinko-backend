import traceback

import psycopg2

try:
    conn = psycopg2.connect("dbname='rinko' user='rinko' host='localhost' password='rinko'")
except:
    print "I am unable to connect to the database"


def owner_exists(event):
    query = "SELECT id FROM teams where LOWER(name) = '%{}%'".format(event['name'])
    cur = conn.cursor()
    cur.execute(query)
    response = cur.fetchone() is not None
    cur.close()

    return response


def get_insert_query(event):
    query = "INSERT INTO owners (name) VALUES ({})".format(event['name'])
    print(query)
    return query


def main(event, context):
    if owner_exists(event):
        return {'status': 'failed', 'error': 'owner_exists_exception', 'message': 'owner already exists.'}
    else:
        try:
            cur = conn.cursor()
            query = get_insert_query(event)
            cur.execute(query)
            conn.commit()
            cur.close()

        except Exception, E:
            traceback.print_exc()
            return {'status': 'failed', 'error': 'add_player_exception', 'message': 'Could not add player to team.'}

        return {'status': 'success'}
