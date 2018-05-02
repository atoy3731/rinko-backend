import re
import traceback, bcrypt, jwt

import datetime
import psycopg2

JWT_SECRET='[o$wEKG*QDM^M.&&Gf[l!OW~xs_|]i}9}NR92Yay,FBEh!kq"cc7z"M-1Tu`ujz'

try:
    conn = psycopg2.connect("dbname='rinko' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"


def login(username, password):
    query = "SELECT username, password, admin FROM users where LOWER(username) = '{}'".format(username)
    cur = conn.cursor()
    cur.execute(query)

    response = cur.fetchone()

    if response is None:
        return {'status': 'failed', 'error': 'user_not_exists_exception', 'message': 'User does not exist.'}
    else:
        if bcrypt.hashpw(str(password).encode('utf-8'), response[1]) == response[1]:
            return {'status': 'success', 'admin': response[2]}
        else:
            return {'status': 'failed', 'error': 'invalid_password_exception', 'message': 'Invalid password.'}
    cur.close()

    return response


def create_token(username, admin):
    payload = {
        'username': username,
        'admin': admin,
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
        token = create_token(username, login_response['admin'])
        return {'status': 'success', 'token': token}
