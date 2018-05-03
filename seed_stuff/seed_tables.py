import base64, json, requests, psycopg2
import random

from psycopg2 import extras
import bcrypt

try:
    conn = psycopg2.connect("dbname='rinko' user='rinko' host='localhost' password='rinko'")
except:
    print("I am unable to connect to the database")

FORWARDS = 10
DEFENSE = 4
GOALIES = 2

USERS = [
    {
        'username': 'adam.toy',
        'first_name': 'Adam',
        'last_name': 'Toy',
        'password': 'password1',
        'email': 'atoy3731@gmail.com',
        'team': "Adam's Team"
    },
    {
        'username': 'test.user.1',
        'first_name': 'Test',
        'last_name': 'User1',
        'password': 'password2',
        'email': 'test.user1@test.com',
        'team': "Test1's Team"
    },
    {
        'username': 'test.user.2',
        'first_name': 'Test',
        'last_name': 'User2',
        'password': 'password3',
        'email': 'test.user2@test.com',
        'team': "Test2's Team"
    }
]


def get_payload(limit, offset):
    response = {}
    response['playerstats'] = 'G,A'
    response['limit'] = limit
    response['offset'] = offset

    return response


def seed_players():


    creds = 'atoy3731:people_31'
    encoded_creds = base64.b64encode(creds.encode('utf-8'))
    headers = {'Authorization': 'Basic {}'.format(encoded_creds.decode('utf-8'))}

    limit = 200
    offset = 0
    url = 'https://api.mysportsfeeds.com/v1.2/pull/nhl/2018-playoff/cumulative_player_stats.json'
    hasMore = True

    while hasMore:
        payload = get_payload(limit, offset)
        response = requests.get(url, params=payload, headers=headers)

        if response.status_code == 200:
            player_obj = json.loads(response.content.decode('utf-8'))['cumulativeplayerstats']

            if 'playerstatsentry' not in player_obj or len(player_obj['playerstatsentry']) == 0:
                hasMore = False
                continue

            players = []

            for player_response in player_obj['playerstatsentry']:
                player_info = player_response['player']
                player_stats = player_response['stats']['stats']
                player = {}

                player['id'] = player_info['ID']
                player['first_name'] = player_info['FirstName']
                player['last_name'] = player_info['LastName']

                if player_info['Position'] == 'RW' or player_info['Position'] == 'LW' or player_info['Position'] == 'C':
                    player['position'] = 'Forward'
                elif player_info['Position'] == 'D':
                    player['position'] = 'Defense'
                else:
                    player['position'] = 'Goalie'


                player['goals'] = int(player_stats['Goals']['#text'])
                player['assists'] = int(player_stats['Assists']['#text'])

                rinko_points = (player['goals'] * 3) + (player['assists'] * 1)

                player['rinko_points'] = rinko_points

                players.append(
                    (player['id'], player['first_name'], player['last_name'], player['position'], player['goals'], player['assists'], player['rinko_points'])
                )

            insert_query = 'INSERT INTO rinko.players (id, first_name, last_name, position, goals, assists, rinko_points) VALUES %s'

            cur = conn.cursor()

            extras.execute_values(
               cur, insert_query, players, template=None, page_size=100
            )
            conn.commit()

        offset += limit


def seed_users_and_teams():
    cur = conn.cursor()
    for user in USERS:
        encrypted_pw = (bcrypt.hashpw(str(user['password']).encode('utf-8'), bcrypt.gensalt(13))).decode('utf-8')

        cur.execute("""INSERT INTO users (username, first_name, last_name, password, email) VALUES (%s,%s,%s,%s,%s) RETURNING id""", (user['username'], user['first_name'], user['last_name'], encrypted_pw, user['email']))
        user_id = cur.fetchone()[0]

        cur.execute("""INSERT INTO teams (name, owner_id) VALUES (%s, %s) RETURNING id""", (user['team'], user_id))
        team_id = cur.fetchone()[0]

        conn.commit()

        user['id'] = user_id
        user['team_id'] = team_id

def seed_rosters():
    cur = conn.cursor()

    for user in USERS:
        user_id = user['id']
        team_id = user['team_id']

        team_rinko_points = 0

        try:
            # Forwards
            cur.execute("""SELECT count(*) FROM players WHERE position = 'Forward'""")
            forward_count = int(cur.fetchone()[0])
            forward_offset = random.randint(0,(forward_count-FORWARDS))
            cur.execute("""SELECT id, rinko_points FROM players WHERE position = 'Forward' LIMIT %s OFFSET %s""", (FORWARDS, forward_offset))
            rows = cur.fetchall()

            for row in rows:
                team_rinko_points += int(row[1])
                cur.execute("""INSERT INTO rosters (player_id, team_id) VALUES (%s, %s)""",
                            (row[0], team_id))

            # Defense
            cur.execute("""SELECT count(*) FROM players WHERE position = 'Defense'""")
            defense_count = int(cur.fetchone()[0])
            defense_offset = random.randint(0,(defense_count-DEFENSE))
            cur.execute("""SELECT id, rinko_points FROM players WHERE position = 'Defense' LIMIT %s OFFSET %s""", (DEFENSE, defense_offset))
            rows = cur.fetchall()

            for row in rows:
                team_rinko_points += int(row[1])
                cur.execute("""INSERT INTO rosters (player_id, team_id) VALUES (%s, %s)""",
                            (row[0], team_id))


            # Goalies
            cur.execute("""SELECT count(*) FROM players WHERE position = 'Goalie'""")
            goalie_count = int(cur.fetchone()[0])
            goalie_offset = random.randint(0,(goalie_count-GOALIES))
            cur.execute("""SELECT id, rinko_points FROM players WHERE position = 'Goalie' LIMIT %s OFFSET %s""", (GOALIES, goalie_offset))
            rows = cur.fetchall()

            for row in rows:
                team_rinko_points += int(row[1])
                cur.execute("""INSERT INTO rosters (player_id, team_id) VALUES (%s, %s)""", (row[0], team_id))
        except Exception as E:
            print(E)

        cur.execute("""UPDATE teams SET rinko_points = %s WHERE id = %s""", (team_rinko_points, team_id))
    conn.commit()

seed_players()
seed_users_and_teams()
seed_rosters()
