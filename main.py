import customtkinter as ctk
import tkinter as tk
from widgets import *
from Components import *


class Home(ctk.CTkFrame): # Inheriting CTk class
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master, fg_color="transparent") # Calls parent class
        self.widgets = []
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        BUTTONS = [["Scan Music", self.scan_music], ["Add Folder", self.add_folder]]

        # Creating To Do List
        self.todo = ToDoList(self, font=font)
        self.todo.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="nswe", rowspan = 2)
        self.widgets.append(self.todo)

        # Creating timer
        self.timer = TimerCreate(self, font=font)
        self.timer.grid(row=1, column=1, padx=(10,10), pady=(10,10), sticky = "nwse")
        self.widgets.append(self.timer)

        self.buttons = ButtonFrame(self, button_values=BUTTONS, is_horizontal=True, font=font)
        self.buttons.grid(row=2, column=1, padx=10, pady=(10, 10), sticky="sew")
        self.widgets.append(self.buttons)

    def scan_music(self, event=None):
        print("Scan Music")

    def add_folder(self, event=None):
        print("Add Folder")


class Tracks(ctk.CTkFrame): # Inheriting CTk class
    def __init__(self, master, font: ctk.CTkFont):
        self.master = master
        self.font = font
        self.widgets = []
        self.prompt = None

        super().__init__(self.master, fg_color="transparent")  # Calls parent class

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.main_topbar_buttons = [["Select Multiple", lambda: self.select_multiple()]]
        self.songs = [["Song 1", "Jeremy", "852", None], ["Song 2", "Balls", "852", None],
                 ["Song 3", "Kahled", "852", None], ["Song 4", "Polio", "852", None],
                 ["Song 5", "Johnathan", "852", None], ["Song 6", "Sinera", "852", None],
                 ["Song 7", "Fred", "852", None], ["Song 8", "Flavio", "852", None],
                 ["Song 9", "Trap", "852", None], ["Song 10", "Honest", "852", None]]
        self.playlists = [["Playlist 1", "27", "852"], ["Playlist 2", "27", "852"],
                          ["Playlist 3", "27", "852"], ["Playlist 4", "27", "852"],
                          ["Playlist 5", "27", "852"], ["Playlist 6", "27", "852"],
                          ["Playlist 7", "27", "852"], ["Playlist 8", "27", "852"],
                          ["Playlist 9", "27", "852"], ["Playlist 10", "27", "852"]]
        self.font = font

        self.main_view()

    def main_view(self):
        destroy_widgets(self.widgets)
        self.topbar = ButtonFrame(self,
                                  button_values=self.main_topbar_buttons,
                                  title=f"{len(self.songs)} Songs",
                                  title_fg_color="transparent",
                                  is_horizontal=True,
                                  title_sticky="w",
                                  button_sticky="e",
                                  font=self.font)
        self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
        self.widgets.append(self.topbar)

        self.track_list = SongFrame(self, self.songs, font=self.font)
        self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self.widgets.append(self.track_list)

    def select_multiple(self):
        destroy_widgets(self.widgets)
        self.select_mult_topbar_buttons = [["Exit Select", lambda: self.main_view()],
                  ["Add to Playlist", self.add_to_playlist],
                  ["Delete Songs", self.delete_songs]]
        self.song_names = []
        for song in self.songs:
            self.song_names.append(f"{song[0]} - {song[1]}")

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
                                        values=self.song_names,
                                        font=self.font,
                                        is_scrollable=True)
        self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self.widgets.append(self.track_list)

    def create_playlist(self):
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist", font = self.font)
        print("Name:", dialog.get_input())

    def add_to_playlist(self):
        if self.prompt is None or not self.prompt.winfo_exists():
            self.prompt = AddToPlaylist(playlists = self.playlists, font= self.font)
        self.prompt.focus()

    def delete_songs(self):
        print("Delete Songs")



class Playlists(ctk.CTkFrame):
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master, fg_color="transparent")  # Calls parent class

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.widgets = []
        self.font=font
        self.main_topbar_buttons = [["Create Playlist", self.create_playlist], ["Select Multiple", self.select_multiple]]
        self.playlists = [["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],
                 ["Playlist 1", "27", "852"], ["Playlist 1", "27", "852"],]

        self.main_view()

    def main_view(self):
        destroy_widgets(self.widgets)
        self.topbar = ButtonFrame(self,
                                  button_values=self.main_topbar_buttons,
                                  title=f"{len(self.playlists)} Playlists",
                                  title_fg_color="transparent",
                                  is_horizontal=True,
                                  title_sticky="w",
                                  button_sticky="e",
                                  font=self.font)
        self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
        self.widgets.append(self.topbar)

        self.track_list = PlaylistFrame(self, self.playlists, font=self.font)
        self.track_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self.widgets.append(self.track_list)

    def select_multiple(self):
        destroy_widgets(self.widgets)
        self.select_mult_topbar_buttons = [["Exit Select", lambda: self.main_view()],
                                           ["Delete Playlists", self.delete_playlist]]
        self.playlist_names = []
        for playlist in self.playlists:
            self.playlist_name = playlist[0]
            self.playlist_song_count = playlist[1]
            self.playlist_names.append(f"{self.playlist_name} - {self.playlist_song_count}")

        self.topbar = ButtonFrame(self,
                                  button_values=self.select_mult_topbar_buttons,
                                  title=f"{len(self.playlist_names)} Songs",
                                  title_fg_color="transparent",
                                  is_horizontal=True,
                                  title_sticky="w",
                                  button_sticky="ew",
                                  font=self.font)
        self.topbar.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
        self.widgets.append(self.topbar)

        self.playlist_list = CheckboxFrame(master=self,
                                        values=self.playlist_names,
                                        font=self.font,
                                        is_scrollable=True)
        self.playlist_list.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self.widgets.append(self.topbar)

    # Event is a required argument as when button is pressed an argument is automatically passed
    def create_playlist(self ,event=None):
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
        print("Name:", dialog.get_input())

    def delete_playlist(self):
        print("Delete Playlist")

class MusicFinder(ctk.CTkFrame):
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master, fg_color = "transparent")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight = 1)

        SONGS = [["Song 1", "Balls", "852", None], ["Song 2", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None],
                 ["Song 3", "Balls", "852", None], ["Song 4", "Balls", "852", None]]

        self.search_frame = SearchFrame(self, font=font)
        self.search_frame.grid(row = 0, column = 0, sticky = "new", padx=(10, 10), pady=(10, 10))

        self.search_results = SongFrame(self, track_list = SONGS, font=font)
        self.search_results.grid(row = 1, column = 0, sticky = "nsew")

class Player(ctk.CTkFrame):
    def __init__(self, master, song: list = ["No Song", "---", "0", None]):
        super().__init__(master)

        self.grid_rowconfigure((0,1), weight=0)
        self.grid_columnconfigure((0,2), weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.song_name_font = ctk.CTkFont(family="Arial", size = 20)
        self.song_artist_font = ctk.CTkFont(family="Arial", size = 16)
        self.icons_font = ctk.CTkFont(family="Arial", size=22)

        self.song_name = song[0]
        self.artist = song[1]
        self.duration = song[2]
        self.thumbnail = song[3]

        self.song_name_label = ctk.CTkLabel(self, text=self.song_name, font=self.song_name_font)
        self.song_name_label.grid(row=0, column=0, padx=(5,5), pady=(5,5), sticky="w")

        self.artist_name_label = ctk.CTkLabel(self, text=self.artist, font=self.song_artist_font)
        self.song_name_label.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="w")

        self.playbar_buttons_frame = ctk.CTkFrame(self, bg_color="transparent")
        self.playbar_buttons_frame.grid(row=0, column=1, padx=(5,5), pady=(5,5), sticky="new")

        # Label frame here
        self.pla

        self.playbar = ctk.CTkSlider(self, from_=0, to=int(self.duration), command=self.retrive_slider_val)
        self.playbar.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="sew")

        self.volume_slider= self.playbar = ctk.CTkSlider(self, from_=0, to=100, command=self.retrive_slider_val)
        self.playbar.grid(row=0, column=2, rowspan=2, padx=(5, 5), pady=(5, 5), sticky="e")


    def retrive_slider_val(self, value):
        print(value)

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master, anchor="s")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color="gray10")

        TABS = ["Home", "Tracks", "Playlists", "Music Finder"]

        for current_tab in TABS:
            self.add(current_tab)
            self.tab(current_tab).grid_columnconfigure(0, weight=1)
            self.tab(current_tab).grid_rowconfigure(0, weight=1)

        self.home = Home(master=self.tab("Home"), font=font)
        self.home.grid(row=0, column=0, sticky="nsew")

        self.tracks = Tracks(master=self.tab("Tracks"), font=font)
        self.tracks.grid(row=0, column=0, sticky="nsew")

        self.playlists = Playlists(master=self.tab("Playlists"), font=font)
        self.playlists.grid(row=0, column=0, sticky="nsew")

        self.finder = MusicFinder(master=self.tab("Music Finder"), font=font)
        self.finder.grid(row=0, column=0, sticky="nsew")

class App(ctk.CTk):
    def __init__(self, title="My App"):
        super().__init__()
        DEFAULT_FONT = ctk.CTkFont(family="Arial", size=18)
        # Initialising Window
        self.title(title)
        ctk.set_appearance_mode("dark")  # light/dark/system (system is not functional on linux)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tab_view = MyTabView(self, DEFAULT_FONT)
        self.tab_view.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky="nsew")
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)

        self.player = Player(self)
        self.player.grid(row=1, column=0, padx=(10, 10), pady=(10,10), sticky="ew")

def destroy_widgets(widgets):
    for widget in widgets:
        widget.destroy()

app = App("Balls")

app.mainloop()