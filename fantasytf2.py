"""
Copyright 2020, rtldg <https://github.com/rtldg>
Copying and distribution of this file, with or without modification, are permitted in any medium without royalty, provided the copyright notice and this notice are preserved. This file is offered as-is, without any warranty.
"""

import a2s # https://github.com/Yepoleb/python-a2s
import sqlite3
import time    # for time.time()
from datetime import datetime # datetime.isoformat() & datetime.utcnow()
import socket  # for socket.timeout

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

def grab_all_servers():
	for server in servers:
		(players, serverinfo) = get_server_data(server)
		if not players or not serverinfo:
			print("[{}] {} skipped".format(
				datetime.isoformat(datetime.utcnow()),
				server
			))
			continue # skip I guess...
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

while True:
	grab_all_servers()
	time.sleep(13.0) # bad luck number

#conn.close()
