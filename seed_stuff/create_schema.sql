CREATE SCHEMA rinko;
	CREATE TABLE rinko.users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, first_name TEXT, last_name TEXT, password TEXT, email TEXT UNIQUE NOT NULL);
	CREATE TABLE rinko.players (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, position TEXT, goals INTEGER, assists INTEGER, rinko_points INTEGER);
	CREATE TABLE rinko.teams (id SERIAL PRIMARY KEY, name TEXT UNIQUE, owner_id INTEGER REFERENCES rinko.users(id), rinko_points INTEGER);
	CREATE TABLE rinko.rosters (player_id INTEGER REFERENCES rinko.players(id), team_id INTEGER REFERENCES rinko.teams(id));
