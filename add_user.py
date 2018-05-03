import re
import traceback, bcrypt

import psycopg2

try:
    conn = psycopg2.connect("dbname='rinko' user='rinko' host='localhost' password='rinko'")
except:
    print "I am unable to connect to the database"


def user_exists(username):
    query = "SELECT username FROM users where LOWER(username) = '{}'".format(username)
    cur = conn.cursor()
    cur.execute(query)

    response = False

    if cur.fetchone() is not None:
        response = True

    cur.close()
    return response


def create_user(username, password, email, admin):
    hashed = bcrypt.hashpw(str(password).encode('utf-8'), bcrypt.gensalt(rounds=13))
    query = "INSERT INTO users (username, password, email, admin) VALUES ('{}', '{}', '{}', {})".format(username, hashed, email, admin)

    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


def main(event, context):
    if 'username' not in event or 'password' not in event or 'email' not in event:
        return {'status': 'failed', 'error': 'missing_parameters_exception', 'message': 'Missing required parameters: username, password, email'}

    username = event['username']
    password = event['password']
    email = event['email']

    if 'admin' in event:
        admin = event['admin']
    else:
        admin = False

    if user_exists(username):
        return {'status': 'failed', 'error': 'user_exists_exception', 'message': 'User already exists.'}

    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        return {'status': 'failed', 'error': 'invalid_email_exception', 'message': 'Invalid email address.'}

    create_user(username, password, email, admin)

    return {'status': 'success', 'username': username, 'email': email, 'admin': admin}
