import bcrypt, jwt

import datetime
import psycopg2

JWT_SECRET='[o$wEKG*QDM^M.&&Gf[l!OW~xs_|]i}9}NR92Yay,FBEh!kq"cc7z"M-1Tu`ujz'

try:
    conn = psycopg2.connect("dbname='rinko' user='rinko' host='localhost' password='rinko'")
except:
    print "I am unable to connect to the database"


def login(username, password):
    cur = conn.cursor()
    # cur.execute("""UPDATE teams SET rinko_points = %s WHERE id = %s""", (team_rinko_points, team_id))
    cur.execute("""SELECT id, username, password, admin FROM users where username = %s""", [username])

    response = cur.fetchone()

    if response is None:
        return {'status': 'failed', 'error': 'user_not_exists_exception', 'message': 'User does not exist.'}
    else:
        if bcrypt.hashpw(str(password).encode('utf-8'), response[2]) == response[2]:
            return {'status': 'success', 'username': username, 'id': response[0], 'admin': response[3]}
        else:
            return {'status': 'failed', 'error': 'invalid_password_exception', 'message': 'Invalid password.'}
    cur.close()

    return response


def create_token(obj):
    payload = {
        'id': obj['id'],
        'username': obj['username'],
        'admin': obj['admin'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=15)
    }
    token = (jwt.encode(payload, JWT_SECRET, algorithm='HS256'))
    token = '.{}'.format(token.split('.',1)[1])

    return token


def main(event, context):
    if 'username' not in event or 'password' not in event:
        return {'status': 'failed', 'error': 'missing_parameters_exception', 'message': 'Missing required parameters: username, password'}

    username = event['username']
    password = event['password']

    login_response = login(username, password)

    if login_response['status'] == 'failed':
        return login_response
    else:
        # Create token
        token = create_token(login_response)
        login_response['token'] = token
        return login_response
