import customtkinter as ctk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import downloader
from widgets import *
from Components import *
from utils import *
from PIL import Image  # Used for thumbnails
import pyglet  # Used for audio
import tinytag as tt
import io
import json
import threading # Used so app doesnt freeze when doing longer processes

class Home(ctk.CTkFrame): # Inheriting CTk class
	def __init__(self, master, font: ctk.CTkFont):
		super().__init__(master, fg_color="transparent") # Calls parent class
		self.widgets = []
		self.grid_columnconfigure((0, 1), weight=1)
		self.grid_rowconfigure(1, weight=1)

		# Creating To Do List
		self.todo = ToDoList(self, font=font)
		self.todo.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="nswe", rowspan = 2)
		self.widgets.append(self.todo)

		# Creating timer
		self.timer = TimerCreate(self, font=font)
		self.timer.grid(row=1, column=1, padx=(10,10), pady=(10,10), sticky = "nwse")
		self.widgets.append(self.timer)


class Tracks(ctk.CTkFrame): # Inheriting CTk class
	def __init__(self, master, font: ctk.CTkFont, player_callback):
		self.master = master
		self.font = font
		self.widgets = []
		self.prompt = None
		self.player_callback= player_callback
		self.song_ids = None

		super().__init__(self.master, fg_color="transparent")  # Calls parent class

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(2, weight=1)

		self.main_topbar_buttons = [["Refresh Tracks", lambda: self.refresh_tracks()],
									["Select Multiple", lambda: self.select_multiple()]]

		destroy_widgets(self.widgets)

		self.font = font
		self.main_view()

	def main_view(self, force = False):
		current_song_ids = self.retrieve_songs()
		if current_song_ids != self.song_ids or force:
			self.song_ids = current_song_ids
			destroy_widgets(self.widgets)
			self.topbar = ButtonFrame(self,
									  button_values=self.main_topbar_buttons,
									  title=f"{len(self.song_ids)} Songs",
									  title_fg_color="transparent",
									  is_horizontal=True,
									  title_sticky="w",
									  button_sticky="e",
									  font=self.font)
			self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
			self.widgets.append(self.topbar)

			self.track_list = SongFrame(self, song_ids=self.song_ids, font=self.font, player_callback = self.player_callback)
			self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")

			self.widgets.append(self.track_list)
		self.after(100, self.main_view)

	def select_multiple(self):
		destroy_widgets(self.widgets)
		self.select_mult_topbar_buttons = [
			["Exit Select", lambda: self.main_view(force=True)],
			["Add to Playlist", self.add_to_playlist],
			["Delete Songs", self.delete_songs]]
		self.song_names = self.retrieve_song_names()
		self.songs = []

		for song in self.song_names:
			self.songs.append(f"{song[2]} - {song[0]} - {song[1]}")

		self.topbar = ButtonFrame(self,
								  button_values=self.select_mult_topbar_buttons,
								  title=f"{len(self.song_names)} Songs",
								  title_fg_color="transparent",
								  is_horizontal=True,
								  title_sticky="w",
								  button_sticky="e",
								  font=self.font)
		self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
		self.widgets.append(self.topbar)

		self.track_list = CheckboxFrame(master=self,
										values=self.songs,
										font=self.font,
										is_scrollable=True)
		self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")
		self.widgets.append(self.track_list)

	def refresh_tracks(self):
		filepath = str(os.path.abspath(os.getcwd()))+"/Songs"
		db = downloader.init_database()
		cursor = db.cursor()
		cursor.execute("SELECT file_path FROM songs")
		all_filepaths_raw = cursor.fetchall()
		all_filepaths = []
		for current_filepath in all_filepaths_raw:
			all_filepaths.append(current_filepath[0])
		for file in os.listdir(filepath):
			if all_filepaths == [] or (filepath+"/"+file not in all_filepaths):
				try:
					tt.TinyTag.get(f"Songs/{file}")
					print(f"{file} is an valid file")
					self.add_song(db, file)
				except Exception as err:
					print(f"{file} is not an audio file")  # Means file is not an audio file
					print(err)
		db.close()

	def add_song(self, db, song_file_name):
		filepath = str(os.path.abspath(os.getcwd())) + "/Songs/" + song_file_name
		song = tt.TinyTag.get(filepath)  # Extracting the metadata
		# Gives title of song if held in metadata otherise we use file name
		song_name = song.title if song.title != None else song_file_name
		song_duration = int(round(song.duration))  # Gives length of songs as seconds
		artist = song.artist if song.artist != None else "Unknown"  # Gives artist name
		publish_date = song.year if song.artist != None else "Unknown"  # song.year givees the exact date
		cursor = db.cursor()
		cursor.execute(
			"INSERT INTO "
			"songs("
			"file_path,"
			"song_name,"
			"song_duration,"
			"artist,"
			"publish_date"
			") "
			"VALUES (?, ?, ?, ?, ?)",
			(filepath, song_name, song_duration, artist, publish_date))
		db.commit()

	def create_playlist(self):
		dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist", font = self.font)
		print("Name:", dialog.get_input())

	def add_to_playlist(self):
		checked = self.track_list.get_checkboxes()
		songIDs = []
		for song in checked:
			songIDs.append(song.split(" ")[0])
		if self.prompt is None or not self.prompt.winfo_exists():
			self.prompt = AddToPlaylist(songIDs = songIDs, font= self.font)
		self.prompt.focus()

	def delete_songs(self):
		checked = self.track_list.get_checkboxes()

		db = downloader.init_database()
		cursor = db.cursor()
		query = "DELETE FROM songs WHERE songID = ?"
		for song in checked:
			song_id = song.split(" ")[0]
			cursor.execute(query, (song_id,))
		db.commit()
		db.close()

		self.select_multiple()

	def retrieve_songs(self):
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

	def retrieve_song_names(self):
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


class Playlists(ctk.CTkFrame):
	def __init__(self, master, font: ctk.CTkFont, player_callback):
		super().__init__(master, fg_color="transparent")  # Calls parent class

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.song_ids = []
		self.player_callback = player_callback
		self.widgets = []
		self.font=font
		self.main_topbar_buttons = [["Create Playlist", self.create_playlist],
									["Select Multiple", self.select_multiple]]
		self.select_mult_topbar_buttons = [
			["Delete Playlists", lambda: self.delete_playlists(self.get_checked_ids(self.checkbox_playlist_list))],
			["Exit Select", lambda :self.main_view(force=True)]]
		self.specific_playlist_topbar_buttons = [["Overwrite Queue", lambda: self.overwrite_queue(self.song_ids)],
												 ["Add to Queue", lambda: self.add_to_queue(self.song_ids)],
												 ["Select Multiple", self.specific_playlist_select_multiple],
												 ["Exit Playlist", lambda: self.main_view(force=True)]]

		self.playlist_list_db = init_playlist_list_database()
		self.playlist_db = init_playlist_database()
		self.old_playlist_names = None

		self.main_view()

	def main_view(self, force = False):
		current_playlist_names = self.retrieve_playlist_names()
		if current_playlist_names != self.old_playlist_names or force:
			self.playlistIDs = self.retrieve_playlistIDs()
			self.old_playlist_names = current_playlist_names
			destroy_widgets(self.widgets)
			self.topbar = ButtonFrame(self,
									  button_values=self.main_topbar_buttons,
									  title=f"{len(self.playlistIDs)} Playlists",
									  title_fg_color="transparent",
									  is_horizontal=True,
									  title_sticky="w",
									  button_sticky="e",
									  font=self.font)
			self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
			self.widgets.append(self.topbar)

			self.playlist_list = PlaylistFrame(self, self.playlistIDs, font=self.font, player_callback=self.player_callback,
											open_playlist_callback=self.open_playlist)
			self.playlist_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
			self.widgets.append(self.playlist_list)
		self.after(100, self.main_view)

	def select_multiple(self):
		destroy_widgets(self.widgets)
		playlist_details = self.retrieve_playlist_details()
		self.playlist_names = []
		for playlist in playlist_details:
			self.playlist_names.append(f"{playlist[0]} - {playlist[1]}")

		self.topbar = ButtonFrame(self,
								  button_values=self.select_mult_topbar_buttons,
								  title=f"{len(self.playlist_names)} Songs",
								  title_fg_color="transparent",
								  is_horizontal=True,
								  title_sticky="w",
								  button_sticky="e",
								  font=self.font)
		self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
		self.widgets.append(self.topbar)

		self.checkbox_playlist_list = CheckboxFrame(master=self,
										values=self.playlist_names,
										font=self.font,
										is_scrollable=True)
		self.checkbox_playlist_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
		self.widgets.append(self.topbar)

	def open_playlist(self, event=None):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.playlistID = event.widget.master.playlistID

		destroy_widgets(self.widgets)
		self.songs_view(force=True)

	def songs_view(self, force: bool = False):
		current_song_ids = self.retrieve_playlist_songIDs(self.playlistID)
		if current_song_ids != self.song_ids or force:
			self.song_ids = current_song_ids
			destroy_widgets(self.widgets)

			self.topbar = ButtonFrame(self,
									  button_values=self.specific_playlist_topbar_buttons,
									  title=f"{len(self.song_ids)} Songs",
									  title_fg_color="transparent",
									  is_horizontal=True,
									  title_sticky="w",
									  button_sticky="e",
									  font=self.font)
			self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
			self.widgets.append(self.topbar)

			self.track_list = SongFrame(self, song_ids=self.song_ids, font=self.font,
										player_callback=self.player_callback)
			self.track_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
			self.widgets.append(self.track_list)

		self.after(100, self.songs_view)

	def specific_playlist_select_multiple(self):
		destroy_widgets(self.widgets)
		songIDs = self.retrieve_playlist_songIDs(self.playlistID)
		all_song_details = self.retrieve_song_names(songIDs)
		song_names = []
		for song_details in all_song_details:
			song_names.append(f"{song_details[2]} - {song_details[0]} - {song_details[1]}")

		self.mult_specific_playlist_buttons = [
			["Remove from Playlist", lambda: self.remove_from_playlist(self.get_checked_ids(obj=self.song_list), self.playlistID)],
			["Add to Queue", lambda: self.add_to_queue(self.get_checked_ids(obj=self.song_list))],
			["Exit Select", lambda: self.main_view(force=True)]]

		self.topbar = ButtonFrame(self,
								  button_values=self.mult_specific_playlist_buttons,
								  title=f"{len(songIDs)} Songs",
								  title_fg_color="transparent",
								  is_horizontal=True,
								  title_sticky="w",
								  button_sticky="e",
								  font=self.font)
		self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
		self.widgets.append(self.topbar)

		self.song_list = CheckboxFrame(master=self,
										   values=song_names,
										   font=self.font,
										   is_scrollable=True)
		self.song_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
		self.widgets.append(self.topbar)

	def load_queue(self):
		with open("Databases/queue.json", "r") as f:
			queue_settings = json.load(f)
			f.close()
		return queue_settings

	def add_to_queue(self, song_ids:list):
		self.queue_settings = self.load_queue()
		self.queue = self.queue_settings['queue']
		self.current_index = self.queue_settings['current_index']
		for song_id in song_ids:
			self.queue.append(song_id)

		queue_config = {
			"current_index": self.current_index,
			"queue": self.queue,
		}
		with open("Databases/queue.json", "w") as f:
			json.dump(queue_config, f, indent=0)
			f.close()

	def overwrite_queue(self, song_ids:list):
		queue_config = {
			"current_index": 0,
			"queue": song_ids
		}
		with open("Databases/queue.json", "w") as f:
			json.dump(queue_config, f, indent=0)
			f.close()
		self.player_callback.load_song(song_ids[0])

	def get_checked_ids(self, obj):
		checked = obj.get_checkboxes()
		songIDs = []
		for song in checked:
			songIDs.append(int(song.split(" ")[0]))
		return songIDs

	def retrieve_song_names(self, songIDs):
		raw_song_names = []
		db = downloader.init_database()
		cursor = db.cursor()
		for songID in songIDs:
			query = "SELECT song_name, artist, songID FROM songs WHERE songID = (?)"
			cursor.execute(query, (songID, ))
			raw_song_names.append(cursor.fetchone())
		db.close()
		song_names = []
		for name in raw_song_names:
			song_names.append([name[0], name[1], name[2]])
		return song_names

	# Event is a required argument as when button is pressed an argument is automatically passed
	def create_playlist(self, event=None):
		dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
		name = dialog.get_input().strip()
		if name != "" and name != None:
			db = init_playlist_list_database()
			cursor = db.cursor()
			cursor.execute(
				"INSERT INTO "
				"Playlist_List("
				"Name"
				")"
				"VALUES (?)",
				(name,))
			db.commit()
			db.close()
			self.main_view(force=True)

	def remove_from_playlist(self, song_ids:list, playlistID):
		db = init_playlist_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist WHERE songID = (?) AND playlistID = (?)"
		for song_id in song_ids:
			cursor.execute(query, (int(song_id), int(playlistID)))
		db.commit()
		db.close()

	def delete_playlists(self, playlistIDs):
		db = init_playlist_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist WHERE playlistID = (?)"
		for playlistID in playlistIDs:
			cursor.execute(query, (int(playlistID),))
		db.commit()
		db.close()

		db = init_playlist_list_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist_List WHERE playlistID = (?)"
		for playlistID in playlistIDs:
			cursor.execute(query, (int(playlistID),))
		db.commit()
		db.close()

	def retrieve_playlist_songIDs(self, playlistID):
		db = init_playlist_database()
		cursor = db.cursor()
		query = "SELECT songID FROM Playlist WHERE playlistID = ?"
		cursor.execute(query, (playlistID,))
		songs_unfiltered = cursor.fetchall()

		song_ids = []
		for songID in songs_unfiltered:
			song_ids.append(songID[0])
		return song_ids

	def retrieve_playlist_details(self):
		playlistIDs = self.retrieve_playlistIDs()
		playlist_names = self.retrieve_playlist_names()
		playlist_details = []
		for i in range (0, len(playlistIDs)):
			playlist_details.append([playlistIDs[i], playlist_names[i]])
		return playlist_details

	def retrieve_playlistIDs(self):
		cursor = self.playlist_list_db.cursor()
		query = ("SELECT PlaylistID FROM Playlist_List")
		cursor.execute(query)
		playlistIDs = cursor.fetchall()
		configured_playlistIDs = []
		for playlistID in playlistIDs:
			configured_playlistIDs.append(playlistID[0])
		return configured_playlistIDs

	def retrieve_playlist_names(self):
		cursor = self.playlist_list_db.cursor()
		query = ("SELECT Name FROM Playlist_List")
		cursor.execute(query)
		playlist_names = cursor.fetchall()
		configured_playlist_names = []
		for playlist_name in playlist_names:
			configured_playlist_names.append(playlist_name[0])
		return configured_playlist_names

class MusicFinder(ctk.CTkFrame):
	def __init__(self, master, font: ctk.CTkFont):
		super().__init__(master, fg_color = "transparent")

		self.grid_rowconfigure(2, weight=1)
		self.grid_columnconfigure(0, weight = 1)

		self.font = font

		self.progress_bar = tk.ttk.Progressbar(self, maximum=100)
		self.progress_bar.grid(row=1, column=0, sticky="new", padx=(10,10), pady=(10,10))

		self.download_output = ScrolledText(self, font=self.font, height=12, state="disabled", bg="gray20", fg="white")
		self.download_output.grid(row=2, column=0, sticky="nsew", pady=(10, 10), padx=(10, 10))

		self.search_frame = SearchFrame(self,
										font=self.font,
										progress_bar_callback=self.progress_bar,
										download_log_callback=self.download_output)
		self.search_frame.grid(row = 0, column = 0, sticky = "new", padx=(10, 10), pady=(10, 10))


class Player(ctk.CTkFrame):
	def __init__(self, master, font: ctk.CTkFont, songID: int = 0):
		super().__init__(master)

		self.grid_rowconfigure((0,1), weight=0)
		self.grid_columnconfigure((0,2), weight=0)
		self.grid_columnconfigure(1, weight=10)

		self.queue_window = None
		self.font = font
		self.song_name_font = ctk.CTkFont(family="Cascadia Mono", size = 16)
		self.song_artist_font = ctk.CTkFont(family="Cascadia Mono", size = 14)
		self.icons_font = ctk.CTkFont(family="Arial", size=22)

		self.button_icons = [["↺", self.rewind],
							 ["⏮", self.previous_song],
							 ["⏯", self.toggle_pause],
							 ["⏭", self.skip_song],
							 ["↻", self.skip_foward]]

		self.queue_settings = self.load_queue()
		self.current_index = self.queue_settings['current_index']
		self.queue = self.queue_settings['queue']
		self.songID=self.queue[self.current_index]

		try:
			self.song_details = self.retrieve_song()
			self.song_name = self.song_details[2]
			self.artist = self.song_details[4]
			self.duration = tk.IntVar(value=self.song_details[3])
			self.filepath = self.song_details[1]
		except:
			self.song_name = "No Song"
			self.artist = "Frank Ocean"
			self.duration = tk.IntVar(value=100)
			self.filepath = None

		self.printable_song_name = self.song_name
		if len(self.printable_song_name) > 30:
			self.printable_song_name = self.printable_song_name[:27]+"..."
		elif len(self.printable_song_name) <= 30:
			self.printable_song_name = self.printable_song_name
			while len(self.printable_song_name) < 30:
				self.printable_song_name += " "

		self.printable_artist = self.artist
		if len(self.printable_artist) > 30:
			self.printable_artist = self.printable_artist[:27] + "..."
		elif len(self.printable_artist) <= 30:
			self.printable_artist = self.printable_artist
			while len(self.printable_artist) < 30:
				self.printable_artist += " "

		try:
			self.thumbnail_img = Image.open(io.BytesIO(tt.TinyTag.get(self.filepath, image=True).images.any.data))
		except:
			self.thumbnail_img = None

		self.player = None
		if self.songID != -1:
			self.boot_player()
			self.player.volume = 0.5

		# Thumbnail Rendering
		if self.thumbnail_img is None:
			self.thumbnail = ctk.CTkImage(light_image=Image.open("Images/No-album-art.png"),
										  dark_image=Image.open("Images/No-album-art.png"),
										  size = (75,75))
		else:
			self.thumbnail = ctk.CTkImage(light_image=self.thumbnail_img,
						 dark_image=self.thumbnail_img,
						 size=(75, 75))

		self.song_details_frame = ctk.CTkFrame(self, fg_color="transparent")
		self.song_details_frame.grid(row=0, column=0, rowspan=2, pady=(5, 5), sticky="ew")

		self.song_thumbnail = ctk.CTkLabel(self.song_details_frame, image=self.thumbnail, text="")
		self.song_thumbnail.grid(row=0, column=0, rowspan=2, padx=(10, 10), pady=(5, 5), sticky="w")

		self.song_name_label = ctk.CTkLabel(self.song_details_frame, text=self.printable_song_name, font=self.song_name_font)
		self.song_name_label.grid(row=0, column=1, pady=(5,5), sticky="w")

		self.artist_name_label = ctk.CTkLabel(self.song_details_frame, text=self.printable_artist, font=self.song_artist_font)
		self.artist_name_label.grid(row=1, column=1, pady=(5, 5), sticky="w")

		self.playbar_buttons = LabelFrame(self,
										  values=self.button_icons,
										  font=self.icons_font,
										  is_horizontal=True,
										  button_sticky="ew",
										  frame_fg_color="transparent")
		self.playbar_buttons.grid(row=0, column=1, padx=(5,5), pady=(5,5), sticky="ew")

		self.seeking = False
		self.playbar = ctk.CTkSlider(self,
									 from_=0,
									 to=self.duration.get(),
									 command= self.seek,
									 )
		self.playbar.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="sew")
		self.playbar.set(0)

		self.queue_button_label = ctk.CTkLabel(self, text="≡", font=self.icons_font)
		self.queue_button_label.grid(row=0, column=2, rowspan=2, padx=(10, 10), pady=(5, 5), sticky="e")
		self.queue_button_label.bind("<Button-1>", self.queue_trigger)
		self.queue_button_label.bind("<Enter>", lambda e:on_enter(e))
		self.queue_button_label.bind("<Leave>", lambda e:on_leave(e))

		self.volume_icon = ctk.CTkLabel(self, text="🔈", font=self.icons_font)
		self.volume_icon.grid(row=0, column=3, rowspan=2, padx=(2, 2), pady=(5, 5), sticky="e")

		self.volume_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.volume_adjust, width=200)
		self.volume_slider.grid(row=0, column=4, rowspan=2, padx=(2, 2), pady=(5, 5), sticky="e")

		self.volume_icon = ctk.CTkLabel(self, text="🔊", font=self.icons_font)
		self.volume_icon.grid(row=0, column=5, rowspan=2, padx=(2, 2), pady=(5, 5), sticky="e")

		if self.song_details == None and self.songID != -1:
			self.song_end()

		self.update_progress()

	def queue_trigger(self, event):
		if self.queue_window is None or not self.queue_window.winfo_exists():
			self.queue_window = QueueViewer(event, font= self.font, player_callback=self)
		self.queue_window.after(100, self.queue_window.lift)

	def song_end(self, load_previous: bool = False):
		self.queue_settings = self.load_queue()
		self.queue = self.queue_settings['queue']
		if load_previous:
			self.current_index = self.queue_settings['current_index'] - 1
		else:
			self.current_index = self.queue_settings['current_index'] + 1

		if self.current_index >= len(self.queue):
			self.current_index = 0
		elif self.current_index < 0:
			self.current_index = len(self.queue)-1
		queue_config = {
			"current_index": self.current_index,
			"queue": self.queue,
		}
		with open("Databases/queue.json", "w") as f:
			json.dump(queue_config, f, indent=0)
			f.close()
		if len(self.queue) != 0:
			self.load_song(self.queue[self.current_index])

	def load_queue(self):
		with open("Databases/queue.json", "r") as f:
			queue_settings = json.load(f)
			f.close()
		if -1 in queue_settings["queue"] and (len(queue_settings["queue"]) >= 2):
			queue_settings["queue"].remove(-1)
		return queue_settings

	def load_song(self, songID: int):
		if self.player:
			self.player.delete()

		self.songID = songID
		self.song_details = self.retrieve_song()

		if self.song_details is None:
			if self.songID != -1:
				self.queue.remove(self.songID)
				self.song_end()

			self.song_name = "No Song"
			self.artist = "Frank Ocean"
			self.duration = tk.IntVar(value=100)
			self.filepath = None
		else:
			self.song_name = self.song_details[2]
			self.artist = self.song_details[4]
			self.duration.set(self.song_details[3])
			self.filepath = self.song_details[1]

		if len(self.song_name) > 30:
			self.song_name = self.song_name[:27] + "..."
		elif len(self.song_name) <= 30:
			while len(self.song_name) < 30:
				self.song_name += " "

		if len(self.artist) > 30:
			self.artist = self.artist[:27] + "..."
		elif len(self.artist) <= 30:
			self.artist = self.artist
			while len(self.artist) < 30:
				self.artist += " "

		try:
			self.thumbnail_img = Image.open(io.BytesIO(tt.TinyTag.get(self.filepath, image=True).images.any.data))
		except:
			self.thumbnail_img = None

		if self.songID != -1:
			try:
				self.boot_player()
				self.player.play()
				self.player.volume = self.volume_slider.get()/100   # Change this to 0.5 to recreate a bug where volume woudl reset upon song change
			except:
				self.song_end()

		if self.thumbnail_img == None:
			self.thumbnail = ctk.CTkImage(light_image=Image.open("Images/No-album-art.png"),
										  dark_image=Image.open("Images/No-album-art.png"),
										  size=(75, 75))
		else:
			self.thumbnail = ctk.CTkImage(light_image=self.thumbnail_img,
										  dark_image=self.thumbnail_img,
										  size=(75, 75))
		self.song_thumbnail.configure(image=self.thumbnail)
		self.song_name_label.configure(text=self.song_name)
		self.artist_name_label.configure(text=self.artist)
		self.playbar.configure(to=self.duration.get())

	def boot_player(self):
		self.player = pyglet.media.Player()
		self.init_queue()

	def retrieve_song(self):
		self.db = downloader.init_database()
		cursor = self.db.cursor()
		query = "SELECT * FROM songs WHERE songID = ?"
		cursor.execute(query, (self.songID,))
		song_details = cursor.fetchone()
		self.db.close()
		return song_details

	def update_progress(self):
		if self.songID != -1:
			if self.player.playing and not self.seeking:
				self.playbar.set(self.player.time)
			if int(round(self.player.time)) == self.duration.get():
				self.song_end()
			self.seeking = False
		self.after(100, self.update_progress)

	def delete_song(self):
		db = downloader.init_database()
		cursor = db.cursor()
		query = "DELETE FROM songs WHERE songID = ?"
		cursor.execute(query, (self.songID,))
		db.commit()
		db.close()

		db = init_playlist_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist WHERE songID = ?"
		cursor.execute(query, (self.songID,))
		db.commit()
		db.close()

	def seek(self, time):
		self.seeking=True
		self.player.seek(float(time))

	def init_queue(self):
		current_queue = [self.filepath]
		for song_fp in current_queue:
			try:
				song_obj = pyglet.media.load(song_fp, streaming=True)  # Turn freaming to false for Lots of bugs
				self.player.queue(song_obj)
			except Exception as err:
				tk.messagebox.showwarning("Can't play song", "Resetting Queue")
				print(err)
				self.queue_clear()

	def queue_clear(self):
		queue_settings = {
			"current_index": 0,
			"queue": [-1]
		}
		with open("Databases/queue.json", "w") as f:
			json.dump(queue_settings, f, indent=0)
			f.close()

	def volume_adjust(self, value):
		self.player.volume = value/100

	def rewind(self, event=None):
		self.player.seek(self.player.time-10)

	def shuffle(self, event=None):
		print("Shuffle")

	def toggle_pause(self, event=None):
		if not self.player.playing:
			self.player.play()
		else:
			self.player.pause()

	def skip_foward(self, event=None):
		self.player.seek(self.player.time+10)

	def skip_song(self, event=None):
		self.song_end()

	def toggle_loop(self, event=None):
		if self.player.loop == False:
			self.player.loop = True
		elif self.player.loop == True:
			self.player.loop = False

	def previous_song(self, event=None):
		self.song_end(load_previous=True)


class MyTabView(ctk.CTkTabview):
	def __init__(self, master, font: ctk.CTkFont, player_callback):
		super().__init__(master, anchor="s")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.configure(fg_color="gray10")

		self.player_callback=player_callback
		TABS = ["    Home    ",
				"   Tracks   ",
				"  Playlist  ",
				"Music Finder"]

		for current_tab in TABS:
			self.add(current_tab)
			self.tab(current_tab).grid_columnconfigure(0, weight=1)
			self.tab(current_tab).grid_rowconfigure(0, weight=1)

		self.home = Home(master=self.tab(TABS[0]), font=font)
		self.home.grid(row=0, column=0, sticky="nsew")

		self.tracks = Tracks(master=self.tab(TABS[1]), font=font, player_callback=self.player_callback)
		self.tracks.grid(row=0, column=0, sticky="nsew")

		self.playlists = Playlists(master=self.tab(TABS[2]), font=font, player_callback=player_callback)
		self.playlists.grid(row=0, column=0, sticky="nsew")

		self.finder = MusicFinder(master=self.tab(TABS[3]), font=font)
		self.finder.grid(row=0, column=0, sticky="nsew")

class App(ctk.CTk):
	def __init__(self, title="My App"):
		super().__init__()
		DEFAULT_FONT = ctk.CTkFont(family="Cascadia Mono", size=18)
		# Initialising Window
		self.title(title)
		ctk.set_appearance_mode("dark")  # light/dark/system (system is not functional on linux)
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		# Needs to be created first to pass player_callback down the chain
		self.player = Player(self, font=DEFAULT_FONT)
		self.player.grid(row=1, column=0, padx=(10, 10), pady=(5, 5), sticky="ew")

		self.tab_view = MyTabView(self, font=DEFAULT_FONT, player_callback=self.player)
		self.tab_view.grid(row=0, column=0, padx=(10,10), pady=(5,5), sticky="nsew")
		self.tab_view.grid_columnconfigure(0, weight=1)
		self.tab_view.grid_rowconfigure(0, weight=1)



def destroy_widgets(widgets):
	for widget in widgets:
		widget.destroy()


app = App("Study Music Player")

app.mainloop()