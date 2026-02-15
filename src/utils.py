import sqlite3

def init_playlist_database():
	"""
	Initialises music_ops.db and songs table or creates them if they don't exist.
	:return: SQLite3 db object
	"""
	db = sqlite3.connect(r"Databases/music_ops.db")
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
	db = sqlite3.connect("Databases/music_ops.db")
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