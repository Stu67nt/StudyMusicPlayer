import customtkinter as ctk
from customtkinter import CTkFrame
import tkinter as tk
import sqlite3
import downloader
import json
import threading
from studymusicplayer.utils import *
from pathlib import Path

"""
TODO: 
Allow for fg_colour and corner radius to be scaled.
Fix Sticky

Widgets exists to hold the most fundamental GUI elements which make up the program. Complex GUI elements such as 
the To Do Lists will be found in Components.py
"""

class ButtonFrame(ctk.CTkFrame):
	"""
	A frame which holds buttons. Not Scrollable.
	:param master: tkinter frame where the button should be held
	:param button_values: 2D list where each element is a list with the following structure
	[Button_text, button_function]
	:param font: Custom Tkinter font object. Selects font the button text uses.
	:param title: title text of the button frame if needed. Leave blank for no text
	:param is_horizontal: Selects if buttons go veritcally down or horizontaally across
	"""
	def __init__(self,
				 master,
				 button_values: list,
				 font: ctk.CTkFont,
				 title: str = "",
				 is_horizontal: bool = False,
				 title_sticky: str = "nsew",
				 title_fg_color: str = "gray30",
				 title_corner_radius:int = 6,
				 button_sticky: str = "nsew",
				 button_frame_color = "grey20"):

		# Setting up grid structure
		super().__init__(master, fg_color = button_frame_color)
		self.grid(row=0, column=0, sticky="nsew")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		# Initialising variables
		self.button_values = button_values
		self.title = title

		# Creating and positioning title in frame only if requested
		if self.title != "":
			self.title_label = ctk.CTkLabel(self,
											text=self.title,
											fg_color=title_fg_color,
											corner_radius=title_corner_radius,
											font = font)
			self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=title_sticky)
			self.grid_columnconfigure(0, weight=0)
			self.grid_rowconfigure(0, weight=0)

		# Creating frame to place buttons in
		self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
		self.button_frame.grid(row=0 if is_horizontal else 1,
								   column=1 if is_horizontal else 0,
								   sticky=button_sticky)


		# Iterating through each item in values and creating a button for it.
		# Each button is then added to a list of buttons so we can track their state.
		for i, value in enumerate(self.button_values):
			self.button = ctk.CTkButton(self.button_frame, text=value[0], command=value[1], font = font)
			# Gridding is based on whether the frame is ment to be horizontal or vertical.
			# Weights added so buttons spread out evenly
			if is_horizontal:
				self.button.grid(row=0, column=i, padx=20, pady=20, sticky=button_sticky)
				self.grid_columnconfigure(i, weight=1)
			else:
				self.button.grid(row=i, column=0, padx=20, pady=20, sticky=button_sticky)
				self.grid_rowconfigure(i, weight=1)


class CheckboxFrame(ctk.CTkFrame):  # Inheriting CTkFrame class
	"""
	A frame which holds Checkboxes.
	:param master: tkinter/customtkinter frame where the Checkbox should be held
	:param button_values: List where each element is the text/value of the checkbox
	:param font: Custom Tkinter font object. Selects font the Checkbox text uses.
	:param title: title text of the Checkbox frame if needed. Leave blank for no text
	:param is_horizontal: Selects if Checkbox go veritcally down or horizontally across
	:param is_scrollable: Selects if the frame can be scrolled or not
	"""
	def __init__(self,
				 master,
				 values,
				 font: ctk.CTkFont,
				 title: str = "",
				 is_horizontal: bool = False,
				 is_scrollable: bool = False):
		super().__init__(master)

		# self.container needed to add a scrollable frame inside the main frame if requested
		# All widgets inside class to be placed in self.container
		if is_scrollable:
			self.container = ctk.CTkScrollableFrame(self)
		else:
			self.container = ctk.CTkFrame(self)

		# placing self.container inside the main frame
		self.container.grid(row=0, column=0, sticky="nsew")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		# Initialising variables
		self.font = font
		self.values = values
		self.checkboxes = []
		self.title = title

		# Creating and positioning title in frame
		if self.title != "":
			self.title_label = ctk.CTkLabel(self.container,
											text=self.title,
											fg_color="transparent",
											font = self.font)
			self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nwe")

		# Iterating through each item in values and creating a checkbox for it.
		# Each checkbox is then added to a list of checkboxes so we can track their state.
		for i, value in enumerate(self.values):
			self.checkbox = ctk.CTkCheckBox(self.container, text=value, font=self.font)
			if is_horizontal:
				self.checkbox.grid(row=0, column=i+1, padx=(10,10), pady=(10,10), sticky="w")
			else:
				self.checkbox.grid(row=i + 1, column=0, padx=(10,10), pady=(10,10), sticky="w")
			# All checkboxes stored so we can easily refrence them to get if they are ticked
			self.checkboxes.append(self.checkbox)

	def get_checkboxes(self):
		"""
		Returning which checkboxes have been ticked.
		:return: List of all checkboxes which have been ticked
		"""
		checked = []
		for box in self.checkboxes:
			if box.get() == 1:
				checked.append(box.cget("text"))
		return checked


class RadioButtonFrame(ctk.CTkFrame):
	"""
	A frame which holds Radio Buttons.
	:param master: tkinter/customtkinter frame where the Radio Buttons should be held
	:param button_values: List where each element is the text/value of the Radio Button
	:param font: Custom Tkinter font object. Selects font the Radio Button text uses.
	:param title: title text of the Radio Button frame if needed. Leave blank for no text
	:param is_horizontal: Selects if Radio Buttons go veritcally down or horizontaally across
	:param is_scrollable: Selects if the frame can be scrolled or not
	"""
	def __init__(self,
				 master,
				 values: list,
				 title: str,
				 font: ctk.CTkFont,
				 is_horizontal: bool = False,
				 is_scrollable: bool = False,
				 title_sticky: str = "ew",
				 title_fg_color: str = "transparent",
				 title_corner_radius:int = 6,
				 button_sticky: str = "nesw"):
		super().__init__(master)  # Initilising parent class
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		# self.container needed to add a scrollable frame inside the main frame if requested
		# All widgets inside class to be placed in self.container
		if is_scrollable:
			self.container = ctk.CTkScrollableFrame(self)
		else:
			self.container = ctk.CTkFrame(self)

		# Configuring grid
		self.container.configure(fg_color = "transparent")
		self.container.grid(row=0, column=0, sticky="nsew")
		self.container.grid_rowconfigure(0, weight=1)
		self.container.grid_columnconfigure(0, weight=0)
		self.container.grid_columnconfigure(1, weight=1)

		# Initialising vars
		self.values = values
		self.title = title
		self.var = ctk.StringVar(value = "")

		# Creating title label
		if self.title != "":
			self.title_label = ctk.CTkLabel(self.container,
											text=self.title,
											fg_color=title_fg_color,
											corner_radius=title_corner_radius,
											font = font)
			self.title_label.grid(row=0, column=0, sticky="ew")

		self.button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
		self.button_frame.grid(row=0 if is_horizontal else 1,
							   column=1 if is_horizontal else 0,
							   sticky=button_sticky)
		self.button_frame.grid_columnconfigure("all", weight=1)

		# Iterating thorugh each value
		for i, value in enumerate(self.values):
			self.radio_button = ctk.CTkRadioButton(self.button_frame,
												   text=value,
												   variable=self.var,
												   value=value,
												   font = font)
			if is_horizontal:
				self.radio_button.grid(row=0, column=i+1, padx=20, pady=20, sticky=button_sticky)

			else:
				self.radio_button.grid(row=i + 1, column=0, padx=20, pady=20, sticky=button_sticky)

	def get_radio_val(self):
		return self.var.get()


class LabelFrame(ctk.CTkFrame):
	def __init__(self,
				 master,
				 values: list,
				 font = ctk.CTkFont,
				 title: str = "",
				 is_horizontal: bool = False,
				 is_scrollable: bool = False,
				 title_sticky: str = "nesw",
				 title_fg_color: str = "gray30",
				 title_corner_radius: int = 6,
				 button_sticky: str = "nesw",
				 frame_fg_color = "transparent"):
		super().__init__(master, fg_color=frame_fg_color)  # Calls/runs parent class. This is necessary so it initialises the inherited class.

		# self.container needed to add a scrollable frame inside the main frame if requested
		# All widgets inside class to be placed in self.container
		if is_scrollable:
			self.container = ctk.CTkScrollableFrame(self, fg_color = frame_fg_color)
		else:
			self.container = ctk.CTkFrame(self, fg_color = frame_fg_color)

		# Configuring grid
		self.container.grid(row=0, column=0, sticky="ew")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		# Initalising variables
		self.values = values
		self.labels = []
		self.title = title

		# Creating and positioning title in frame
		if self.title != "":  # As empty string is default if this is true means title is wanted.
			self.title_label = ctk.CTkLabel(self.container,
											text=self.title,
											fg_color=title_fg_color,
											corner_radius=title_corner_radius,
											font = font)
			self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=title_sticky)

		# Iterating through each item in values and creating a button for it.
		# Each button is then added to a list of buttons so we can track their state.
		for i, value in enumerate(self.values):
			self.label = ctk.CTkLabel(self.container, text=value[0], font= font)
			if is_horizontal:
				self.label.grid(row=0, column=i + 1, padx=20, pady=20, sticky=button_sticky)
				self.container.grid_columnconfigure(i+1, weight=1)
			else:
				self.label.grid(row=i + 1, column=0, padx=20, pady=20, sticky=button_sticky)
				self.container.grid_rowconfigure(i+1, weight=1)

			self.labels.append(self.label)

		# Binds each label to it's relevant function
		for i in range(len(self.labels)):
			self.labels[i].bind("<Button-1>", self.values[i][1])
			self.labels[i].bind("<Enter>", lambda e:on_enter(e))
			self.labels[i].bind("<Leave>", lambda e:on_leave(e))


class SongLabel(ctk.CTkFrame):
	def __init__(self,
				 master,
				 songID,
				 font: ctk.CTkFont,
				 player_callback):
		super().__init__(master)

		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(1, weight=1)

		self.font = font
		self.prompt = None
		self.player_callback = player_callback
		self.BASE_DIR = Path(__file__).parent

		self.songID = songID
		self.song_details = self.retrieve_song()
		self.song_filepath = self.song_details[1]
		self.song_name = self.song_details[2]
		self.mins, self.secs = self.convert_time(self.song_details[3])
		self.artist = self.song_details[4]

		self.name_label = ctk.CTkLabel(self, text = self.song_name, font = self.font)
		self.name_label.grid(column=1, row=0, padx=(10,10), sticky= "nw")

		self.artist_label = ctk.CTkLabel(self, text = self.artist, font = self.font)
		self.artist_label.grid(column=1, row=1, padx=(10, 10), sticky="nw")

		self.time_text_str = "%d:%02d" % (self.mins, self.secs)
		self.duration_label = ctk.CTkLabel(self, text=self.time_text_str, font = self.font)
		self.duration_label.grid(column=2, row=0, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="e")

		self.options_button_font = ctk.CTkFont(family="Cascadia Mono", size=30, weight="bold")
		self.options_button = ctk.CTkLabel(self, text = "⋮", font = self.options_button_font)
		self.options_button.grid(column=3, row=0, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="e")

		MENU_OPTIONS = [["Add to Queue", self.add_to_queue],
						["Add to Playlist", self.add_to_playlist],
						["Delete Song", self.delete_song]]

		self.menu = tk.Menu(self, tearoff=0)
		for option in MENU_OPTIONS:
			name = option[0]
			func = option[1]
			self.menu.add_command(label=name, command=func)

		self.options_button.bind("<Button-1>", self.menu_trigger)
		self.options_button.bind("<Enter>", lambda e: on_enter(e))
		self.options_button.bind("<Leave>", lambda e: on_leave(e))

		self.bind("<Button-1>", self.play_song)
		self.bind("<Enter>", lambda e: on_enter(e))
		self.bind("<Leave>", lambda e: on_leave(e))


	# ChatGPT Slop - Change it
	def menu_trigger(self, event):
		try:
			self.menu.tk_popup(event.x_root, event.y_root)
		finally:
			self.menu.grab_release()

	def play_song(self, event):
		self.player_callback.load_song(self.songID)

	def retrieve_song(self):
		self.db = downloader.init_database()
		cursor = self.db.cursor()
		query = "SELECT * FROM songs WHERE songID = ?"
		cursor.execute(query, (self.songID,))
		song_details = cursor.fetchone()
		self.db.close()
		return song_details

	def add_to_playlist(self):
		from studymusicplayer.Components import *  # Import needs to be done here as otherwise program does not run

		songID = [self.songID]  # needs to be in a list so add to playlist can properly process the id
		if self.prompt is None or not self.prompt.winfo_exists():
			self.prompt = Components.AddToPlaylist(songIDs=songID, font=self.font)
		self.prompt.after(100, self.prompt.lift)

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


	def load_queue(self):
		with open(str(self.BASE_DIR/"Databases"/"queue.json"), "r") as f:
			queue_settings = json.load(f)
			f.close()
		return queue_settings

	def add_to_queue(self):
		self.queue_settings = self.load_queue()
		self.queue = self.queue_settings['queue']
		self.current_index = self.queue_settings['current_index']
		self.queue.append(self.songID)

		queue_config = {
			"current_index": self.current_index,
			"queue": self.queue,
		}
		with open("Databases/queue.json", "w") as f:
			json.dump(queue_config, f, indent=0)
			f.close()

	def convert_time(self, secs):
		mins = int(secs // 60)
		secs = int(secs % 60)
		return mins, secs

class PlaylistLabel(ctk.CTkFrame):
	"""
	TODO: Add default thumbnail.
		  Create Checkboxable version
		  BInding click to relevant playlist
	"""
	def __init__(self,
				 master,
				 playlistID: int,
				 playlist_name,
				 font: ctk.CTkFont,
				 open_playlist_callback,
				 player_callback):
		super().__init__(master)

		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(1, weight=1)

		self.playlist_name = playlist_name
		self.playlistID = playlistID
		self.player_callback = player_callback
		self.BASE_DIR = Path(__file__).parent

		self.name_label = ctk.CTkLabel(self, text = playlist_name, font = font)
		self.name_label.grid(column=1, row=0, padx=(10,10), sticky= "nw")

		self.options_button_font = ctk.CTkFont(family="Cascadia Mono", size=30, weight="bold")
		self.options_button = ctk.CTkLabel(self, text = "⋮", font = self.options_button_font)
		self.options_button.grid(column=3, row=0, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="e")

		MENU_OPTIONS = [["Delete Playlist", self.delete_playlist],
						["Add to Queue", self.add_to_queue],
						["Rename Playlist", self.rename_playlist],
						["Overwrite Queue", self.overwrite_queue]]

		self.menu = tk.Menu(self, tearoff=0)
		for option in MENU_OPTIONS:
			name = option[0]
			func = option[1]
			self.menu.add_command(label=name, command=func)

		self.options_button.bind("<Button-1>", self.menu_trigger)
		self.options_button.bind("<Enter>", lambda e: on_enter(e))
		self.options_button.bind("<Leave>", lambda e: on_leave(e))

		self.bind("<Button-1>", lambda event=None: open_playlist_callback(event = event))
		self.bind("<Enter>", lambda e: on_enter(e))
		self.bind("<Leave>", lambda e: on_leave(e))

	def menu_trigger(self, event):
		try:
			self.menu.tk_popup(event.x_root, event.y_root)
		finally:
			self.menu.grab_release()

	def temp(self):
		print("temp")

	def delete_playlist(self):
		db = init_playlist_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist WHERE playlistID = (?)"
		cursor.execute(query, (self.playlistID,))
		db.commit()
		db.close()

		db = init_playlist_list_database()
		cursor = db.cursor()
		query = "DELETE FROM Playlist_List WHERE playlistID = (?)"
		cursor.execute(query, (self.playlistID,))
		db.commit()
		db.close()

	def add_to_queue(self):
		queue_settings = self.player_callback.load_queue()
		queue = queue_settings['queue']
		current_index = queue_settings['current_index']
		song_ids = self.retrieve_playlist_songIDs(self.playlistID)
		for song_id in song_ids:
			queue.append(song_id)

		queue_config = {
			"current_index": current_index,
			"queue": queue,
		}
		with open(str(self.BASE_DIR/"Databases"/"queue.json"), "w") as f:
			json.dump(queue_config, f, indent=0)
			f.close()

	def overwrite_queue(self):
		queue_settings = self.player_callback.load_queue()
		queue = self.retrieve_playlist_songIDs(self.playlistID)
		current_index = 0

		queue_config = {
			"current_index": current_index,
			"queue": queue,
		}
		with open(self.BASE_DIR/"Databases"/"queue.json", "w") as f:
			json.dump(queue_config, f, indent=0)
			f.close()
		self.player_callback.load_song(queue[current_index])

	def rename_playlist(self, event=None):
		dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
		name = dialog.get_input().strip()
		if name != "" and name != None:
			db = init_playlist_list_database()
			cursor = db.cursor()
			cursor.execute(
				"UPDATE Playlist_List "
				"SET Name = ? "
				"WHERE playlistID = ?",
				(name, self.playlistID,))
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