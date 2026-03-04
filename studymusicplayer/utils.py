import sqlite3
from pathlib import Path
import json

try:
	from . import downloader
except ImportError:
	import downloader

def init_playlist_database():
	"""
	Initialises music_ops.db and songs table or creates them if they don't exist.
	:return: SQLite3 db object
	"""
	BASE_DIR = Path(__file__).parent
	db = sqlite3.connect(str(BASE_DIR/"Databases"/"music_ops.db"))
	cursor = db.cursor()
	query = ("CREATE TABLE IF NOT EXISTS "  # Needed as otherwise if the table is lost the program will not boot
			 "Playlist("
			 "PlaylistID INTEGER ,"
			 "songID INTEGER"
			 ")")
	cursor.execute(query)
	db.commit()  # Committing the query
	return db

def init_playlist_list_database():
	"""
    Initialises music_ops.db and songs table or creates them if they don't exist.
    :return: SQLite3 db object
	"""
	BASE_DIR = Path(__file__).parent
	db = sqlite3.connect(str(BASE_DIR/"Databases"/"music_ops.db"))
	cursor = db.cursor()
	query = ("CREATE TABLE IF NOT EXISTS "  # Needed as otherwise if the table is lost the program will not boot
             "Playlist_List(" 
             "PlaylistID INTEGER PRIMARY KEY AUTOINCREMENT,"
			 "Name TEXT"
             ")")
	cursor.execute(query)
	db.commit()  # Committing the query
	return db

def on_enter(event=None):
	event.widget.configure(cursor="hand2")

def on_leave(event=None):
	event.widget.configure(cursor="")

def retrieve_all_song_ids():
	db = downloader.init_database()
	cursor = db.cursor()
	query = "SELECT songID FROM songs"
	cursor.execute(query)
	raw_song_ids = cursor.fetchall()
	db.close()
	song_ids = []
	for id in raw_song_ids:
		song_ids.append(id[0])
	return song_ids

def retrieve_song_names(self, songIDs):
	raw_song_names = []
	db = downloader.init_database()
	cursor = db.cursor()
	for songID in songIDs:
		query = "SELECT song_name, artist, songID FROM songs WHERE songID = (?)"
		cursor.execute(query, (songID,))
		raw_song_names.append(cursor.fetchone())
	db.close()
	song_names = []
	for name in raw_song_names:
		song_names.append([name[0], name[1], name[2]])
	return song_names

def retrieve_all_song_names():
	db = downloader.init_database()
	cursor = db.cursor()
	query = "SELECT song_name, artist, songID FROM songs"
	cursor.execute(query)
	raw_song_names = cursor.fetchall()
	db.close()
	song_names = []
	for name in raw_song_names:
		song_names.append([name[0], name[1], name[2]])
	return song_names

def retrieve_playlist_names():
	db = init_playlist_list_database()
	cursor = db.cursor()
	query = "SELECT Name FROM Playlist_List"
	cursor.execute(query)
	playlist_names = cursor.fetchall()
	configured_playlist_names = []
	for playlist_name in playlist_names:
		configured_playlist_names.append(playlist_name[0])
	db.close()
	return configured_playlist_names

def retrieve_playlistIDs():
	db = init_playlist_list_database()
	cursor = db.cursor()
	query = "SELECT PlaylistID FROM Playlist_List"
	cursor.execute(query)
	playlistIDs = cursor.fetchall()
	configured_playlistIDs = []
	for playlistID in playlistIDs:
		configured_playlistIDs.append(playlistID[0])
	return configured_playlistIDs

def retrieve_playlist_songIDs(self, playlistID):
	db = utils.init_playlist_database()
	cursor = db.cursor()
	query = "SELECT songID FROM Playlist WHERE playlistID = ?"
	cursor.execute(query, (playlistID,))
	songs_unfiltered = cursor.fetchall()

	song_ids = []
	for songID in songs_unfiltered:
		song_ids.append(songID[0])
	return song_ids

def retrieve_playlist_details():
	playlistIDs = retrieve_playlistIDs()
	playlist_names = retrieve_playlist_names()
	playlist_details = []
	for i in range(0, len(playlistIDs)):
		playlist_details.append([playlistIDs[i], playlist_names[i]])
	return playlist_details

def load_queue():
	BASE_DIR = Path(__file__).parent
	with open(str(BASE_DIR / "Databases" / "queue.json"), "r") as f:
		queue_settings = json.load(f)
		f.close()
	if -1 in queue_settings["queue"] and (len(queue_settings["queue"]) >= 2):
		queue_settings["queue"].remove(-1)
	return queue_settings

def add_to_queue(song_ids: list):
	BASE_DIR = Path(__file__).parent
	queue_settings = load_queue()
	queue = queue_settings['queue']
	current_index = queue_settings['current_index']
	for song_id in song_ids:
		queue.append(song_id)

	queue_config = {
		"current_index": current_index,
		"queue": queue,
	}
	with open(str(BASE_DIR / "Databases" / "queue.json"), "w") as f:
		json.dump(queue_config, f, indent=0)
		f.close()

def overwrite_queue(song_ids: list, player_callback):
	BASE_DIR = Path(__file__).parent
	queue_config = {
		"current_index": 0,
		"queue": song_ids
	}
	with open(str(BASE_DIR / "Databases" / "queue.json"), "w") as f:
		json.dump(queue_config, f, indent=0)
		f.close()
	player_callback.load_song(song_ids[0])

print(Path(__file__).parent)