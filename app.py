import json

import time
from flask import Flask, request
from flask_restplus import Api, Resource

import add_user
import get_players, get_teams, add_player_to_team
import login
from flask_cors import CORS

application = Flask(__name__)
CORS(application)


api = Api(
    application,
    title='SG Microservice',
    description="Kub.io's microservice for security groups.",
    default='sg-service'
)


@api.route('/api/players')
class Players(Resource):
    def get(self):
        event = {
            'team': request.args.get('team'),
            'limit': request.args.get('limit'),
            'offset': request.args.get('offset'),
            'name': request.args.get('name')
        }

        response = get_players.main(event, {})
        return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    def post(self):
        event = {
            'player_id': request.args.get('player_id'),
            'team_id': request.args.get('team_id')
        }

        response = add_player_to_team.main(event, {})
        return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@api.route('/api/teams')
class Teams(Resource):
    def get(self):
        event = {
            'id': request.args.get('id')
        }

        response = get_teams.main(event, {})
        return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@api.route('/api/login')
class Login(Resource):
    def post(self):
        event = {
            'username': request.args.get('username'),
            'password': request.args.get('password'),
        }

        response = login.main(event, {})
        return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@api.route('/api/users')
class Users(Resource):
    def post(self):
        event = request.get_json()

        response = add_user.main(event, {})
        return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    application.run(host='localhost', port=9000, debug=True)