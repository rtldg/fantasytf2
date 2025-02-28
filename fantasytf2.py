"""
Copyright 2020, rtldg <https://github.com/rtldg>
Copying and distribution of this file, with or without modification, are permitted in any medium without royalty, provided the copyright notice and this notice are preserved. This file is offered as-is, without any warranty.
"""

import a2s # https://github.com/Yepoleb/python-a2s
import sqlite3
import time    # for time.time()
from datetime import datetime # datetime.isoformat() & datetime.utcnow()
import socket  # for socket.timeout
import sys # sys.argv

servers = [
	("us1.uncledane.com", 27015), # Los Angeles
	("us2.uncledane.com", 27015), # Chicago
	("us3.uncledane.com", 27015), # San Francisco
	("us4.uncledane.com", 27015), # New York City
	("eu1.uncledane.com", 27015), # Frankfurt
	("eu2.uncledane.com", 27015), # Berlin
]

conn = sqlite3.connect("fantasytf2.db")
cursor = conn.cursor()
cursor.execute('''
	CREATE TABLE IF NOT EXISTS playerinfo
	(datetime real, name text, score int, duration real, map text, server text)
''')
cursor.execute('''
	CREATE TABLE IF NOT EXISTS fucky
	(name text, score int)
''')

def get_server_data(server):
	players = None
	serverinfo = None
	for x in range(2):
		try:
			players = a2s.players(server)
			break
		except: # probably socket.timeout...
			pass
	if players:
		for x in range(2):
			try:
				serverinfo = a2s.info(server)
				break
			except: # probably socket.timeout...
				pass
	return (players, serverinfo)

server_lobby = {}
def grab_all_servers():
	for server in servers:
		(players, serverinfo) = get_server_data(server)
		if not players or not serverinfo:
			print("[{}] {} skipped".format(
				datetime.isoformat(datetime.utcnow()),
				server
			))
			continue

		lobby = None
		if not server in server_lobby:
			server_lobby[server] = {"map": serverinfo.map_name, "players": {}}
		lobby = server_lobby[server]

		if lobby["map"] != serverinfo.map_name:
			# Just changed maps. Log all the player scores THEN update scores...
			cursor.executemany('INSERT INTO fucky VALUES (?,?)', list(lobby["players"].items()))
			lobby["map"] = serverinfo.map_name
			lobby["players"] = {}

		for player in players:
			lobby["players"][player.name] = player.score

		now = time.time()
		fuckaddress = "{}:{}".format(server[0], server[1])
		players = list(map(
			lambda x: (now, x.name, x.score, x.duration, serverinfo.map_name, fuckaddress),
			filter(lambda x: x.name != "", players)
		))
		cursor.executemany('INSERT INTO playerinfo VALUES (?,?,?,?,?,?)', players)
		conn.commit()
		print("[{}] {} retrieved {} players".format(
			datetime.isoformat(datetime.utcnow()),
			server,
			len(players)
		))
		time.sleep(0.1)

# I don't know SQL so fuck me...
if len(sys.argv) > 1 and sys.argv[1] == "dump":
	cursor.execute("SELECT DISTINCT name FROM fucky WHERE name != '' ORDER BY name ASC")
	names = cursor.fetchall()
	shit = []
	for d in names:
		cursor.execute("SELECT name, SUM(SCORE) FROM fucky WHERE name = (?)", d)
		shit.append(cursor.fetchone())
	shit.sort(reverse = True, key = lambda x: x[1])
	print(shit)
else:
	while True:
		grab_all_servers()
		time.sleep(13.0) # bad luck number


"""
SELECT sum(score) FROM fucky WHERE name = "jake paul hater";
"""

