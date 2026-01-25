import customtkinter as ctk
import tkinter as tk
from widgets import *
from Components import *


class Home(ctk.CTkFrame): # Inheriting CTk class
    def __init__(self, master):
        super().__init__(master, fg_color="transparent") # Calls parent class

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        BUTTONS = [["Scan Music", self.scan_music], ["Add Folder", self.add_folder]]

        # Creating To Do List
        self.todo = ToDoList(self)
        self.todo.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="nswe", rowspan = 2)

        # Creating timer
        self.timer = TimerCreate(self)
        self.timer.grid(row=1, column=1, padx=(10,10), pady=(10,10), sticky = "nwse")

        self.buttons = ButtonFrame(self, button_values=BUTTONS, is_horizontal=True)
        self.buttons.grid(row=2, column=1, padx=10, pady=(10, 10), sticky="sew")

    def scan_music(self, event=None):
        print("Scan Music")

    def add_folder(self, event=None):
        print("Add Folder")

class Tracks(ctk.CTkFrame): # Inheriting CTk class
    def __init__(self, master):
        super().__init__(master, fg_color="transparent") # Calls parent class

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        TOPBAR = [["Select Multiple", self.select_multiple]]
        SONGS = [["Song 1", "Balls", "852", None], ["Song 2", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None]]
        song_count = len(SONGS)

        self.topbar = ButtonFrame(self,
                                  button_values = TOPBAR,
                                  title = f"{song_count} Songs",
                                  title_fg_color = "transparent",
                                  is_horizontal = True,
                                  title_sticky = "w",
                                  button_sticky = "ew")
        self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")

        self.track_list = SongFrame(self, SONGS)
        self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")

    # Event is a required argument as when button is pressed an argument is automatically passed
    def create_playlist(event=None):
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
        print("Name:", dialog.get_input())

    def select_multiple(self, event=None):
        print("Select Multiple")


class Playlists(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")  # Calls parent class

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        TOPBAR = [["Create Playlist", self.create_playlist], ["Select Multiple", self.select_multiple]]
        PLAYLISTS = [["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],]
        playlist_count = len(PLAYLISTS)

        self.topbar = ButtonFrame(self,
                                  button_values=TOPBAR,
                                  title=f"{playlist_count} Playlists",
                                  title_fg_color="transparent",
                                  is_horizontal=True,
                                  title_sticky="w",
                                  button_sticky="e")
        self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")

        self.track_list = PlaylistFrame(self, PLAYLISTS)
        self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")

    # Event is a required argument as when button is pressed an argument is automatically passed
    def create_playlist(event=None):
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
        print("Name:", dialog.get_input())

    def select_multiple(self, event=None):
        print("Select Multiple")

class MusicFinder(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color = "transparent")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight = 1)

        SONGS = [["Song 1", "Balls", "852", None], ["Song 2", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None]]

        self.search_frame = SearchFrame(self)
        self.search_frame.grid(row = 0, column = 0, sticky = "new", padx=(10,10), pady=(10, 10))

        self.search_results = SongFrame(self, track_list = SONGS)
        self.search_results.grid(row = 1, column = 0, sticky = "nsew", padx=(10,10), pady=(10, 10))



class MyTabView(ctk.CTkTabview):
    def __init__(self, master):
        super().__init__(master, anchor="s")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color="gray10")

        TABS = ["Home", "Tracks", "Playlists", "Music Finder"]

        for current_tab in TABS:
            self.add(current_tab)
            self.tab(current_tab).grid_columnconfigure(0, weight=1)
            self.tab(current_tab).grid_rowconfigure(0, weight=1)

        self.home = Home(master=self.tab("Home"))
        self.home.grid(row=0, column=0, sticky="nsew")

        self.tracks = Tracks(master=self.tab("Tracks"))
        self.tracks.grid(row=0, column=0, sticky="nsew")

        self.playlists = Playlists(master=self.tab("Playlists"))
        self.playlists.grid(row=0, column=0, sticky="nsew")

        self.finder = MusicFinder(master=self.tab("Music Finder"))
        self.finder.grid(row=0, column=0, sticky="nsew")

class App(ctk.CTk):
    def __init__(self, title="My App"):
        super().__init__()

        # Initialising Window
        self.title(title)
        ctk.set_appearance_mode("dark")  # light/dark/system (system is not functional on linux)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tab_view = MyTabView(self)
        self.tab_view.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky="nsew")
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)

        self.song_label = SongLabel(self, song_name="song_name", artist="song_artist",
                                    duration="song_duration")
        self.song_label.grid(row=1, column=0, padx=(10, 10), pady=(10,10), sticky="ew")


app = App("Balls")

app.mainloop()
