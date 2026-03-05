import customtkinter as ctk  # Used for GUI
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image  # Used for thumbnails
import pyglet  # Used for audio
import tinytag as tt  # Used for retrieving audio metadata
import io
import json
import threading # Used so app doesnt freeze when doing longer processes
from pathlib import Path
import os

# Needed for packaging
try:
	from . import downloader
	from . import widgets
	from . import Components
	from . import utils
except ImportError:
	import downloader
	import widgets
	import Components
	import utils

# Home
class Home(ctk.CTkFrame): # Inheriting CTk class
	# Master to place menu in the tabview frame
	def __init__(self, master, font: ctk.CTkFont):
		super().__init__(master, fg_color="transparent")  # Calls parent class
		# Configuring stretching
		self.grid_columnconfigure((0, 1), weight=1)
		self.grid_rowconfigure(1, weight=1)

		# Creating To Do List
		self.todo = Components.ToDoList(self, font=font)
		self.todo.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="nswe", rowspan = 2)

		# Creating timer
		self.timer = Components.TimerCreate(self, font=font)
		self.timer.grid(row=1, column=1, padx=(10,10), pady=(10,10), sticky = "nwse")

# Tracks
class Tracks(ctk.CTkFrame): # Inheriting CTk class
	# Master to place menu in the tabview frame
	# Player callback to allow song labels to access player
	def __init__(self, master, font: ctk.CTkFont, player_callback):
		# Initalising variables
		# Finding file base direcrtory. Needed for cross compatibility.
		self.BASE_DIR = Path(__file__).parent
		self.master = master
		self.font = font
		self.widgets = []
		self.player_callback= player_callback
		self.prompt = None
		self.song_ids = None

		super().__init__(self.master, fg_color="transparent")  # Calls parent class

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(2, weight=1)

		# Defining buttons
		self.main_topbar_buttons = [["Refresh Tracks", lambda: self.refresh_tracks()],
									["Select Multiple", lambda: self.select_multiple()]]

		# Destoying widgets incase any exist (none should but it acts as safety)
		# Needed to prevent memory leaks
		utils.destroy_widgets(self.widgets)

		# Creating the main view
		self.main_view()

	def main_view(self, force = False):
		"""
		Main view of the Tracks window. Shows all the songs and some options.
		:param force: Forces a refresh if True
		"""

		# Checking if refresh is needed
		# Refresh is needed if forced or new songs added to the database.
		current_song_ids = utils.retrieve_all_song_ids()
		if current_song_ids != self.song_ids or force:
			# Updating song ids as song ids changed
			self.song_ids = current_song_ids
			# Clearing old widgets
			utils.destroy_widgets(self.widgets)

			self.topbar = widgets.ButtonFrame(self,
									  button_values=self.main_topbar_buttons,
									  title=f"{len(self.song_ids)} Songs",
									  title_fg_color="transparent",
									  is_horizontal=True,
									  title_sticky="w",
									  button_sticky="e",
									  font=self.font)
			self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
			self.widgets.append(self.topbar)

			self.track_list = Components.SongFrame(self, song_ids=self.song_ids, font=self.font, player_callback = self.player_callback)
			self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")
			# Adding to widgets list so can clear later if needed
			self.widgets.append(self.track_list)
		# Rerunning function after 500ms to recheck if song ids updated
		self.after(500, self.main_view)

	def select_multiple(self):
		"""
		Select Multiple View of the Tracks window.
		"""
		# Clearing previous widgets to save memory
		utils.destroy_widgets(self.widgets)

		# Defining Buttons and varibales
		self.select_mult_topbar_buttons = [
			["Exit Select", lambda: self.main_view(force=True)],
			["Add to Playlist", self.add_to_playlist],
			["Delete Songs", self.delete_songs]]
		self.song_names = utils.retrieve_all_song_names()
		self.songs = []

		# Adding all song names to displaybale list
		for song in self.song_names:
			# Song[2] is songID
			# song[0] is song name
			# song[1] is song artist
			self.songs.append(f"{song[2]} - {song[0]} - {song[1]}")

		# Creating widgets
		self.topbar = widgets.ButtonFrame(self,
								  button_values=self.select_mult_topbar_buttons,
								  title=f"{len(self.song_names)} Songs",
								  title_fg_color="transparent",
								  is_horizontal=True,
								  title_sticky="w",
								  button_sticky="e",
								  font=self.font)
		self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
		self.widgets.append(self.topbar)

		self.track_list = widgets.CheckboxFrame(master=self,
										values=self.songs,
										font=self.font,
										is_scrollable=True)
		self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")
		self.widgets.append(self.track_list)

	def refresh_tracks(self):
		"""
		Checks if any songs on songs directory exist but are not in the database.
		"""
		filepath = str(self.BASE_DIR / "Songs")

		# Initalising database
		db = downloader.init_database()
		cursor = db.cursor()
		cursor.execute("SELECT file_path FROM songs")
		all_filepaths_raw = cursor.fetchall()

		# Moving all file paths retreived into an easily accessible list
		all_filepaths = []
		for current_filepath in all_filepaths_raw:
			all_filepaths.append(current_filepath[0])

		# reading all files in songs directory. If file is not already held and file si a valid song added to db
		for file in os.listdir(filepath):
			if all_filepaths == [] or (str(self.BASE_DIR/filepath/file) not in all_filepaths):
				try:
					tt.TinyTag.get(str(self.BASE_DIR / "Songs" / file))
					print(f"{file} is an valid file")
					self.add_song(file)
				except Exception as err:
					print(f"{file} is not an audio file")  # Means file is not an audio file
					print(err)
		db.close()

	def add_song(self, song_file_name):
		"""
		Adds a song to the songs table of music_ops.db
		:param song_file_name: file name of the song to add to database
		"""
		db = downloader.init_database()
		filepath = str(self.BASE_DIR / "Songs" / song_file_name)
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

	def add_to_playlist(self):
		"""
		Adds a song to the playlist table of music_ops.db
		"""
		# Gets all checked songs adn puts them into accessable list filtered
		checked = self.track_list.get_checkboxes()
		songIDs = []
		for song in checked:
			songIDs.append(song.split(" ")[0])
		# Creates playlist
		if self.prompt is None or not self.prompt.winfo_exists():
			self.prompt = Components.AddToPlaylist(songIDs=songIDs, font=self.font)
		self.prompt.after(100, self.prompt.lift)

	def delete_songs(self):
		"""
		Removes songs from the playlist table of music_ops.db. (Does not actually delete the files)
		"""
		# Gets all checked songs
		checked = self.track_list.get_checkboxes()

		db = downloader.init_database()
		cursor = db.cursor()
		query = "DELETE FROM songs WHERE songID = ?"
		for song in checked:
			song_id = song.split(" ")[0]  # Formatting into getting songid
			cursor.execute(query, (song_id,))
		db.commit()
		db.close()

		db = utils.init_playlist_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist WHERE songID = ?"
		cursor.execute(query, (song_id,))
		db.commit()
		db.close()

		# Refreshing tracks screen
		self.select_multiple()

class Playlists(ctk.CTkFrame):
	def __init__(self, master, font: ctk.CTkFont, player_callback):
		# Needs to be transparednt so no extra layer.
		super().__init__(master, fg_color="transparent")  # Calls parent class

		# Configuring sizing
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		# Initalising vars
		self.song_ids = []
		self.player_callback = player_callback
		self.widgets = []
		self.font=font
		self.old_playlist_names = None
		self.BASE_DIR = Path(__file__).parent

		# Initalising buttons
		self.main_topbar_buttons = [["Create Playlist", self.create_playlist],
									["Select Multiple", self.select_multiple]]
		self.select_mult_topbar_buttons = [
			["Delete Playlists", lambda: utils.delete_playlists(self.get_checked_ids(self.checkbox_playlist_list))],
			["Exit Select", lambda :self.main_view(force=True)]]
		self.specific_playlist_topbar_buttons = [["Overwrite Queue", lambda: utils.overwrite_queue(self.song_ids, self.player_callback)],
												 ["Add to Queue", lambda: utils.add_to_queue(self.song_ids)],
												 ["Select Multiple", self.songs_view_select_multiple],
												 ["Exit Playlist", lambda: self.main_view(force=True)]]

		# Initialising buttons
		self.playlist_list_db = utils.init_playlist_list_database()
		self.playlist_db = utils.init_playlist_database()

		self.main_view()

	def main_view(self, force = False):
		"""
		Main view of the playlists screen
		"""
		# Gets current list of playlists
		current_playlist_names = utils.retrieve_all_playlist_names()
		# If forced to or playlists have been updtaed the view refreshes
		if current_playlist_names != self.old_playlist_names or force:
			self.playlistIDs = utils.retrieve_all_playlistIDs()
			self.old_playlist_names = current_playlist_names
			utils.destroy_widgets(self.widgets)

			# Creating widgets
			self.topbar = widgets.ButtonFrame(self,
									  button_values=self.main_topbar_buttons,
									  title=f"{len(self.playlistIDs)} Playlists",
									  title_fg_color="transparent",
									  is_horizontal=True,
									  title_sticky="w",
									  button_sticky="e",
									  font=self.font)
			self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
			self.widgets.append(self.topbar)

			self.playlist_list = Components.PlaylistFrame(self, self.playlistIDs, font=self.font, player_callback=self.player_callback,
											open_playlist_callback=self.open_playlist)
			self.playlist_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
			self.widgets.append(self.playlist_list)

		# rerunning function after 100 ms.
		self.after(100, self.main_view)

	def select_multiple(self):
		"""
		Select Multiple view of playlists
		"""
		# Clearing main view screen to prevent memory leak.
		utils.destroy_widgets(self.widgets)

		playlist_details = utils.retrieve_all_playlist_details()

		# Creating list of playlist names for the checkbox frame widget
		# Playlist id needs to be in the name due to technical limitations with custom tkinter checkbox widget
		self.playlist_names = []
		for playlist in playlist_details:
			self.playlist_names.append(f"{playlist[0]} - {playlist[1]}")

		# Creating widgets
		self.topbar = widgets.ButtonFrame(self,
								  button_values=self.select_mult_topbar_buttons,
								  title=f"{len(self.playlist_names)} Songs",
								  title_fg_color="transparent",
								  is_horizontal=True,
								  title_sticky="w",
								  button_sticky="e",
								  font=self.font)
		self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
		self.widgets.append(self.topbar)

		self.checkbox_playlist_list = widgets.CheckboxFrame(master=self,
										values=self.playlist_names,
										font=self.font,
										is_scrollable=True)
		self.checkbox_playlist_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
		self.widgets.append(self.topbar)

	def open_playlist(self, event=None):
		"""
		Opens the selected playlist
		"""
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		# Specific variable path for selected playlistID
		self.playlistID = event.widget.master.playlistID

		# Deleting old frame to prevent memory leak
		utils.destroy_widgets(self.widgets)
		self.songs_view(force=True)

	def songs_view(self, force: bool = False):
		"""
		Opens the specific selected playlist and shows it's songs.
		"""
		# Getting song ids in database for the playlist
		current_song_ids = utils.retrieve_playlist_songIDs(self.playlistID)
		# checking if playlist has been updated since last time.
		if current_song_ids != self.song_ids or force:
			# Updating view if playlist has changed
			self.song_ids = current_song_ids
			utils.destroy_widgets(self.widgets)

			# Creating widgets
			self.topbar = widgets.ButtonFrame(self,
									  button_values=self.specific_playlist_topbar_buttons,
									  title=f"{len(self.song_ids)} Songs",
									  title_fg_color="transparent",
									  is_horizontal=True,
									  title_sticky="w",
									  button_sticky="e",
									  font=self.font)
			self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
			self.widgets.append(self.topbar)

			self.track_list = Components.SongFrame(self, song_ids=self.song_ids, font=self.font,
										player_callback=self.player_callback)
			self.track_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
			self.widgets.append(self.track_list)

		# Rerunning function after 100ms
		self.after(100, self.songs_view)

	def songs_view_select_multiple(self):
		"""
		Multi select for specific playlist
		"""
		# Clearing old frame to prevent memory leaks
		utils.destroy_widgets(self.widgets)

		# Creating song name for checkbox frame
		songIDs = utils.retrieve_playlist_songIDs(self.playlistID)
		all_song_details = utils.retrieve_song_names(songIDs)
		song_names = []
		for song_details in all_song_details:
			# Song ID has to be present due to technical limitations with customtkinter checkbox widget
			song_names.append(f"{song_details[2]} - {song_details[0]} - {song_details[1]}")

		# Defining buttons
		self.mult_specific_playlist_buttons = [
			["Remove from Playlist", lambda: self.remove_from_playlist(self.get_checked_ids(obj=self.song_list), self.playlistID)],
			["Add to Queue", lambda: utils.add_to_queue(self.get_checked_ids(obj=self.song_list))],
			["Exit Select", lambda: self.main_view(force=True)]]

		# Creating widgets
		self.topbar = widgets.ButtonFrame(self,
								  button_values=self.mult_specific_playlist_buttons,
								  title=f"{len(songIDs)} Songs",
								  title_fg_color="transparent",
								  is_horizontal=True,
								  title_sticky="w",
								  button_sticky="e",
								  font=self.font)
		self.topbar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
		self.widgets.append(self.topbar)

		self.song_list = widgets.CheckboxFrame(master=self,
										   values=song_names,
										   font=self.font,
										   is_scrollable=True)
		self.song_list.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
		self.widgets.append(self.topbar)

	def get_checked_ids(self, obj):
		"""
		Retrieves ids of checked items of obj
		:param obj: CheckboxFrame class object
		"""
		checked = obj.get_checkboxes()
		songIDs = []
		for song in checked:
			songIDs.append(int(song.split(" ")[0]))
		return songIDs

	# Event is a required argument as when button is pressed an argument is automatically passed
	def create_playlist(self, event=None):
		"""
		Triggers CTkInputDialog and creates a new playlist
		"""
		dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
		name = dialog.get_input().strip()
		if name != "" and name != None:
			db = utils.init_playlist_list_database()
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
		"""
		Removes provided songs from the provided playlist
		"""
		db = utils.init_playlist_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist WHERE songID = (?) AND playlistID = (?)"
		for song_id in song_ids:
			cursor.execute(query, (int(song_id), int(playlistID)))
		db.commit()
		db.close()

	def delete_playlists(self, playlistIDs):
		"""
		Deletes provided playlist and records of songs attatched to it.
		"""
		db = utils.init_playlist_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist WHERE playlistID = (?)"
		for playlistID in playlistIDs:
			cursor.execute(query, (int(playlistID),))
		db.commit()
		db.close()

		db = utils.init_playlist_list_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist_List WHERE playlistID = (?)"
		for playlistID in playlistIDs:
			cursor.execute(query, (int(playlistID),))
		db.commit()
		db.close()

class MusicFinder(ctk.CTkFrame):
	"""
	Frame which is used for downloading music.
	"""
	def __init__(self, master, font: ctk.CTkFont):
		super().__init__(master, fg_color = "transparent")

		# Configuring weights
		self.grid_rowconfigure(2, weight=1)
		self.grid_columnconfigure(0, weight = 1)

		self.font = font

		# Creating widgets
		self.progress_bar = tk.ttk.Progressbar(self, maximum=100)
		self.progress_bar.grid(row=1, column=0, sticky="new", padx=(10,10), pady=(10,10))

		self.download_output = ScrolledText(self, font=self.font, height=12, state="disabled", bg="gray20", fg="white")
		self.download_output.grid(row=2, column=0, sticky="nsew", pady=(10, 10), padx=(10, 10))

		self.search_frame = Components.SearchFrame(self,
										font=self.font,
										progress_bar_callback=self.progress_bar,
										download_log_callback=self.download_output)
		self.search_frame.grid(row = 0, column = 0, sticky = "new", padx=(10, 10), pady=(10, 10))


class Player(ctk.CTkFrame):
	def __init__(self, master, font: ctk.CTkFont, songID: int = 0):
		super().__init__(master)

		# Configuring weights
		self.grid_rowconfigure((0,1), weight=0)
		self.grid_columnconfigure((0,2), weight=0)
		self.grid_columnconfigure(1, weight=10)

		# Innitalising vars
		self.BASE_DIR = Path(__file__).parent
		self.queue_window = None
		self.font = font
		self.song_name_font = ctk.CTkFont(family="Cascadia Mono", size = 16)
		self.song_artist_font = ctk.CTkFont(family="Cascadia Mono", size = 14)
		self.icons_font = ctk.CTkFont(family="Arial", size=22)
		self.seeking = False

		# initalising Buttons
		self.button_icons = [["↺", self.rewind],
							 ["⏮", self.previous_song],
							 ["⏯", self.toggle_pause],
							 ["⏭", self.skip_song],
							 ["↻", self.skip_foward]]

		# Initalising Queue
		self.queue_settings = utils.load_queue()
		self.current_index = self.queue_settings['current_index']
		self.queue = self.queue_settings['queue']
		self.songID=self.queue[self.current_index]

		# Attempting to retrieve song
		try:
			self.song_details = utils.retrieve_song(self.songID)
			self.song_name = self.song_details[2]
			self.artist = self.song_details[4]
			self.duration = tk.IntVar(value=self.song_details[3])
			self.filepath = self.song_details[1]
		except:  # If no song found
			self.song_details = None
			self.song_name = "No Song"
			self.artist = "Frank Ocean"
			self.duration = tk.IntVar(value=100)
			self.filepath = None

		# Confihuring song/artist name length so playbar does not jitter
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

		# Attempting to load the image
		try:
			self.thumbnail_img = Image.open(io.BytesIO(tt.TinyTag.get(self.filepath, image=True).images.any.data))
		except:
			self.thumbnail_img = None

		# Setting default volume and booting up the player
		self.player = None
		if self.songID != -1:
			self.boot_player()
			self.player.volume = 0.5

		# Drawing widgets
		if self.thumbnail_img is None:
			self.thumbnail = ctk.CTkImage(light_image=Image.open(str(self.BASE_DIR/"Images"/"No-album-art.png")),
										  dark_image=Image.open(str(self.BASE_DIR/"Images"/"No-album-art.png")),
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

		self.playbar_buttons = widgets.LabelFrame(self,
										  values=self.button_icons,
										  font=self.icons_font,
										  is_horizontal=True,
										  button_sticky="ew",
										  frame_fg_color="transparent")
		self.playbar_buttons.grid(row=0, column=1, padx=(5,5), pady=(5,5), sticky="ew")

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
		self.queue_button_label.bind("<Enter>", lambda e:utils.on_enter(e))
		self.queue_button_label.bind("<Leave>", lambda e:utils.on_leave(e))

		self.volume_icon = ctk.CTkLabel(self, text="🔈", font=self.icons_font)
		self.volume_icon.grid(row=0, column=3, rowspan=2, padx=(2, 2), pady=(5, 5), sticky="e")

		self.volume_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.volume_adjust, width=200)
		self.volume_slider.grid(row=0, column=4, rowspan=2, padx=(2, 2), pady=(5, 5), sticky="e")

		self.volume_icon = ctk.CTkLabel(self, text="🔊", font=self.icons_font)
		self.volume_icon.grid(row=0, column=5, rowspan=2, padx=(2, 2), pady=(5, 5), sticky="e")

		# If song is invalid and not the default invalid song we skip to the next song
		if self.song_details == None and self.songID != -1:
			self.song_end()

		# Updates the progress slider.
		self.update_progress()

	def queue_trigger(self, event):
		"""
		Opens the queue.
		"""
		if self.queue_window is None or not self.queue_window.winfo_exists():
			self.queue_window = Components.QueueViewer(event, font= self.font, player_callback=self)
		self.queue_window.after(100, self.queue_window.lift)

	def song_end(self, load_previous: bool = False):
		"""
		Handles the end of a song
		:param load_previous: If true goes to the previous song rather than the next.
		"""
		self.queue_settings = utils.load_queue()
		self.queue = self.queue_settings['queue']
		# changing current_song index
		if load_previous:
			self.current_index = self.queue_settings['current_index'] - 1
		else:
			self.current_index = self.queue_settings['current_index'] + 1

		# looping queue
		if self.current_index >= len(self.queue):
			self.current_index = 0
		elif self.current_index < 0:
			self.current_index = len(self.queue)-1
		queue_config = {
			"current_index": self.current_index,
			"queue": self.queue,
		}
		# storing details
		with open(str(self.BASE_DIR/"Databases"/"queue.json"), "w") as f:
			json.dump(queue_config, f, indent=0)
			f.close()
		# Loads up the next song as long as the queue is not empty
		if len(self.queue) != 0:
			self.load_song(self.queue[self.current_index])

	def load_song(self, songID: int):
		"""
		Loads up the song corresonding to the specified songID
		:param songID: unique ID of a song as found in music_ops.db songs table
		"""
		# Deleting the old player
		if self.player:
			self.player.delete()

		# Initalising variables and details
		self.songID = songID
		self.song_details = utils.retrieve_song(self.songID)

		# Checking if song details coulf be found
		# If not blank song details are loaded
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

		# Standarising artist and song names to prevent playbar jittering
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

		# Loading song details
		try:
			self.thumbnail_img = Image.open(io.BytesIO(tt.TinyTag.get(self.filepath, image=True).images.any.data))
		except:
			self.thumbnail_img = None

		if self.thumbnail_img == None:
			self.thumbnail = ctk.CTkImage(light_image=Image.open(str(self.BASE_DIR/"Images"/"No-album-art.png")),
										  dark_image=Image.open(str(self.BASE_DIR/"Images"/"No-album-art.png")),
										  size=(75, 75))
		else:
			self.thumbnail = ctk.CTkImage(light_image=self.thumbnail_img,
										  dark_image=self.thumbnail_img,
										  size=(75, 75))
		self.song_thumbnail.configure(image=self.thumbnail)
		self.song_name_label.configure(text=self.song_name)
		self.artist_name_label.configure(text=self.artist)
		self.playbar.configure(to=self.duration.get())

		# starting player if songID not the default
		if self.songID != -1:
			try:
				self.boot_player()
				self.player.play()
				self.player.volume = self.volume_slider.get() / 100  # Change this to 0.5 to recreate a bug where volume woudl reset upon song change
			# If an error occurs when trying to boot the song we skip to the next song
			except:
				self.song_end()

	def boot_player(self):
		"""Boots up the music player"""
		self.player = pyglet.media.Player()
		self.init_queue()

	def update_progress(self):
		"""Updates the progress of the song every 100ms"""
		if self.songID != -1:
			if self.player.playing and not self.seeking:
				self.playbar.set(self.player.time)
			if int(round(self.player.time)) == self.duration.get():
				self.song_end()
			self.seeking = False
		self.after(100, self.update_progress)

	def seek(self, time):
		"""Used for seeking in the song"""
		self.seeking=True
		self.player.seek(float(time))

	def init_queue(self):
		"""
		Initalises the queue
		"""
		current_queue = [self.filepath]
		for song_fp in current_queue:
			try:
				song_obj = pyglet.media.load(song_fp, streaming=True)  # Turn freaming to false for Lots of bugs
				self.player.queue(song_obj)
			except Exception as err:
				tk.messagebox.showwarning("Can't play song", "Resetting Queue")
				print(err)
				utils.queue_clear()

	def volume_adjust(self, value):
		"""Adjusts the player volume"""
		self.player.volume = value/100

	def rewind(self, event=None):
		"""Goes back 10 seconds in the song"""
		self.player.seek(self.player.time-10)

	def shuffle(self, event=None):
		"""Deprecated function"""
		print("Shuffle")

	def toggle_pause(self, event=None):
		"""Pauses or unpauses the song"""
		if not self.player.playing:
			self.player.play()
		else:
			self.player.pause()

	def skip_foward(self, event=None):
		"""Jumps foward 10 seconds in the song"""
		self.player.seek(self.player.time+10)

	def skip_song(self, event=None):
		"""Jumps to the next song"""
		# Immediately kills the current song as this will immedately start the next song
		self.song_end()

	def previous_song(self, event=None):
		"""Jumps to the previous song"""
		# Immediately kills the current song as this will immedately start the previous song as specified in arg
		self.song_end(load_previous=True)


class MyTabView(ctk.CTkTabview):
	def __init__(self, master, font: ctk.CTkFont, player_callback):
		# Anchor "s" is needed as otherwise we run into sizing issues with tabview
		super().__init__(master, anchor="s", fg_color="gray10")

		# Configuringn weights
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		# Configuring vars and tabs
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
		# Initialising Window
		super().__init__()
		self.title(title)
		ctk.set_appearance_mode("dark")  # light/dark/system (system is not functional on linux)
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		DEFAULT_FONT = ctk.CTkFont(family="Cascadia Mono", size=18)

		# Creating widgets
		# Needs to be created first to pass player_callback down the chain
		self.player = Player(self, font=DEFAULT_FONT)
		self.player.grid(row=1, column=0, padx=(10, 10), pady=(5, 5), sticky="ew")

		self.tab_view = MyTabView(self, font=DEFAULT_FONT, player_callback=self.player)
		self.tab_view.grid(row=0, column=0, padx=(10,10), pady=(5,5), sticky="nsew")
		self.tab_view.grid_columnconfigure(0, weight=1)
		self.tab_view.grid_rowconfigure(0, weight=1)

def main():
	app = App("Study Music Player")
	app.mainloop()

main()