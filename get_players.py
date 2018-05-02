import psycopg2

try:
    conn = psycopg2.connect("dbname='rinko' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"

#
ev = {
    "team": None,
    "limit": 25,
    "offset": 0,
    "name": "Sidney Crosby"
}


def get_count_query(event):
    query = "SELECT COUNT(*) FROM players ";

    filter_by_team = False

    # Filter by team_id if desired
    if "team" in event and event["team"] is not None:
        filter_by_team = True
        query += "JOIN team_rosters ON (players.id = team_rosters.player_id) WHERE team_id = '{}' ".format(event['team'])

    # First first and last name by name entry if desired
    if 'name' in event and event['name'] is not None:
        if filter_by_team:
            query += "AND "
        else:
            query += "WHERE "

        name_parts = str(event['name']).split(' ')

        for i, name_part in enumerate(name_parts):
            name_part = str(name_part).lower()

            if i != 0:
                query += "AND "

            query += "(LOWER(first_name) LIKE '%{0}%' OR LOWER(last_name) LIKE '%{0}%') ".format(name_part)

    return query


def get_query(event):
    query = "SELECT * FROM players ";

    # Get the limit and offset from the event if they exist
    limit = event['limit'] if 'limit' in event and event['limit'] is not None else 25
    offset = event['offset'] if 'offset' in event and event['offset'] is not None else 0

    filter_by_team = False

    # Filter by team_id if desired
    if "team" in event and event["team"] is not None:
        filter_by_team = True
        query += "JOIN team_rosters ON (players.id = team_rosters.player_id) WHERE team_id = '{}' ".format(event['team'])

    # First first and last name by name entry if desired
    if 'name' in event and event['name'] is not None:
        if filter_by_team:
            query += "AND "
        else:
            query += "WHERE "

        name_parts = str(event['name']).split(' ')

        for i, name_part in enumerate(name_parts):
            name_part = str(name_part).lower()

            if i != 0:
                query += "AND "

            query += "(LOWER(first_name) LIKE '%{0}%' OR LOWER(last_name) LIKE '%{0}%') ".format(name_part)

    query += "LIMIT {} OFFSET {}".format(limit, offset)

    return query


def main(event, context):
    response = {'players': []}

    cur = conn.cursor()

    count_query = get_count_query(event)
    cur.execute(count_query)
    result = cur.fetchone()
    response['total'] = result[0]

    if response['total'] > 0:
        query = get_query(event)

        cur.execute(query)
        rows = cur.fetchall()

        for row in rows:
            player = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'goals': row[3],
                'assists': row[4],
                'rinko_points': row[5]
            }

            response['players'].append(player)

    return response