import traceback

import psycopg2

try:
    conn = psycopg2.connect("dbname='rinko' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"


def player_exists(event):
    query = "SELECT player_id FROM team_rosters where player_id = {} and team_id = {}".format(event['player_id'], event['team_id'])
    cur = conn.cursor()
    cur.execute(query)
    response = cur.fetchone() is not None
    cur.close()

    return response

def get_insert_query(event):
    query = "INSERT INTO team_rosters (player_id, team_id) VALUES ({}, {})".format(event['player_id'], event['team_id'])
    print(query)
    return query


def main(event, context):
    if player_exists(event):
        return {'status': 'failed', 'error': 'add_player_exception', 'message': 'Player already on team.'}
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
