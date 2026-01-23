import customtkinter
import tkinter as tk
from widgets import *
from Components import *


class Home(customtkinter.CTkFrame): # Inheriting CTk class
    def __init__(self, master):
        super().__init__(master, fg_color="transparent") # Calls parent class

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        BUTTONS = [["Scan Music", self.hi], ["Add Folder", self.hi]]

        # Creating To Do List
        self.todo = ToDoList(self)
        self.todo.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="nswe", rowspan = 2)

        # Creating timer
        self.timer = TimerCreate(self)
        self.timer.grid(row=1, column=1, padx=(10,10), pady=(10,10), sticky = "nwse")

        self.buttons = ButtonFrame(self, button_values=BUTTONS, is_horizontal=True)
        self.buttons.grid(row=2, column=1, padx=10, pady=(10, 10), sticky="sew")

    def hi(self):
        print("hi")


class Tracks(customtkinter.CTkFrame): # Inheriting CTk class
    def __init__(self, master, title: str="My App"):
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
        dialog = customtkinter.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
        print("Name:", dialog.get_input())

    def select_multiple(self, event=None):
        print("Select Multiple")


class Playlists(customtkinter.CTkFrame):
    def __init__(self, master, title: str="My App"):
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

        self.topbar = ButtonFrame(self, button_values=TOPBAR, title=f"{playlist_count} Playlists",
                                  title_fg_color="transparent", is_horizontal=True, title_sticky="w",
                                  button_sticky="e")
        self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")

        self.track_list = PlaylistFrame(self, PLAYLISTS)
        self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")

    # Event is a required argument as when button is pressed an argument is automatically passed
    def create_playlist(event=None):
        dialog = customtkinter.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
        print("Name:", dialog.get_input())

    def select_multiple(self, event=None):
        print("Select Multiple")


class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master):
        super().__init__(master, anchor="s")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color="gray10")

		# create tabs
        self.add("Home")
        self.tab("Home").grid_columnconfigure(0, weight=1)
        self.tab("Home").grid_rowconfigure(0, weight=1)

        self.add("Tracks")
        self.tab("Tracks").grid_columnconfigure(0, weight=1)
        self.tab("Tracks").grid_rowconfigure(0, weight=1)

        self.add("Playlists")
        self.tab("Playlists").grid_columnconfigure(0, weight=1)
        self.tab("Playlists").grid_rowconfigure(0, weight=1)

		# add widgets on tabs
        self.home = Home(master=self.tab("Home"))
        self.home.grid(row=0, column=0, sticky="nsew")

        self.tracks = Tracks(master=self.tab("Tracks"))
        self.tracks.grid(row=0, column=0, sticky="nsew")

        self.playlists = Playlists(master=self.tab("Playlists"))
        self.playlists.grid(row=0, column=0, sticky="nsew")

class App(customtkinter.CTk):
    def __init__(self, title="My App"):
        super().__init__()

        # Initialising Window
        self.title(title)
        customtkinter.set_appearance_mode("dark")  # light/dark/system (system is not functional on linux)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tab_view = MyTabView(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)

        self.song_label = SongLabel(self, song_name="song_name", artist="song_artist",
                                    duration="song_duration")
        self.song_label.grid(row=1, column=0, padx=(10, 10), pady=(10,10), sticky="ew")


app = App("Balls")

app.mainloop()
