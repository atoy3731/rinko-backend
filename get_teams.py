import psycopg2

try:
    conn = psycopg2.connect("dbname='rinko' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"

def get_query(event):
    query = "SELECT teams.id, teams.name, owners.name, teams.rinko_points FROM teams JOIN owners ON (owners.id = teams.owner_id) ";

    if 'id' in event and event['id'] is not None:
        query += "WHERE teams.id = {} ".format(event['id'])

    query += "ORDER BY rinko_points DESC"

    return query


def main(event, context):
    response = []

    query = get_query(event)

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    for row in rows:
        team = {
            'id': row[0],
            'name': row[1],
            'owner': row[2],
            'rinko_points': row[3]
        }

        response.append(team)

    return response