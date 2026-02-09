import customtkinter as ctk
import tkinter as tk
import downloader
from widgets import *
from Components import *
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


    def scan_music(self, event=None):
        print("Scan Music")

    def add_folder(self, event=None):
        print("Add Folder")


class Tracks(ctk.CTkFrame): # Inheriting CTk class
    def __init__(self, master, font: ctk.CTkFont, player_callback):
        self.master = master
        self.font = font
        self.widgets = []
        self.prompt = None
        self.player_callback= player_callback

        super().__init__(self.master, fg_color="transparent")  # Calls parent class

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.main_topbar_buttons = [["Select Multiple", lambda: self.select_multiple()]]
        self.song_ids = self.retrieve_songs()
        self.playlists = [["Playlist 1", "1"],
                          ["Playlist 2", "2"],
                          ["Playlist 3", "3"],
                          ["Playlist 4", "4"]]

        self.font = font
        self.main_view()

    def main_view(self):
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

    def select_multiple(self):
        destroy_widgets(self.widgets)
        self.select_mult_topbar_buttons = [
            ["Exit Select", lambda: self.main_view()],
            ["Add to Playlist", self.add_to_playlist],
            ["Delete Songs", self.delete_songs]]
        self.song_names = self.retrieve_song_names()
        self.songs = []

        for song in self.song_names:
            self.songs.append(f"{song[0]} - {song[1]} {song[2]}")

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



    def create_playlist(self):
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist", font = self.font)
        print("Name:", dialog.get_input())

    def add_to_playlist(self):
        if self.prompt is None or not self.prompt.winfo_exists():
            self.prompt = AddToPlaylist(playlists = self.playlists, font= self.font)
        self.prompt.focus()

    def delete_songs(self):
        checked = self.track_list.get_checkboxes()

        db = downloader.init_database()
        cursor = db.cursor()
        query = "DELETE FROM songs WHERE songID = ?"
        for song in checked:
            song_id = song.split(" ")[-1]
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
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master, fg_color="transparent")  # Calls parent class

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.widgets = []
        self.font=font
        self.main_topbar_buttons = [["Create Playlist", self.create_playlist], ["Select Multiple", self.select_multiple]]
        self.playlists = [["Playlist 1", "1", "123", lambda: self.retrieve_playlist(1)],
                          ["Playlist 2", "2", "246", lambda: self.retrieve_playlist(2)],
                          ["Playlist 3", "3", "369", lambda: self.retrieve_playlist(3)],
                          ["Playlist 4", "4", "492", lambda: self.retrieve_playlist(4)]]

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
                                  button_sticky="e",
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
    def create_playlist(self, event=None):
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="Create Playlist")
        print("Name:", dialog.get_input())

    def delete_playlist(self):
        print("Delete Playlist")

    def retrieve_playlist(self, param):
        pass


class MusicFinder(ctk.CTkFrame):
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master, fg_color = "transparent")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight = 1)

        self.search_frame = SearchFrame(self, font=font)
        self.search_frame.grid(row = 0, column = 0, sticky = "new", padx=(10, 10), pady=(10, 10))

class Player(ctk.CTkFrame):
    def __init__(self, master, songID: int = 0):
        super().__init__(master)

        self.grid_rowconfigure((0,1), weight=0)
        self.grid_columnconfigure((0,2), weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.song_name_font = ctk.CTkFont(family="Arial", size = 20)
        self.song_artist_font = ctk.CTkFont(family="Arial", size = 16)
        self.icons_font = ctk.CTkFont(family="Arial", size=22)

        self.button_icons = [["↺", self.rewind],
                             ["🔀", self.shuffle],
                             ["⏮", self.previous_song],
                             ["⏯", self.toggle_pause],
                             ["⏭", self.skip_song],
                             ["🔁", self.toggle_loop],
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

        try:
            self.thumbnail_img = Image.open(io.BytesIO(tt.TinyTag.get(self.filepath, image=True).images.any.data))
        except:
            self.thumbnail_img = None

        self.player = None
        if self.songID != 0:
            self.boot_player()

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
        self.song_details_frame.grid(row=0, column=0, rowspan=2, padx=(5, 5), pady=(5, 5), sticky="nsw")

        self.song_thumbnail = ctk.CTkLabel(self.song_details_frame, image=self.thumbnail, text="")
        self.song_thumbnail.grid(row=0, column=0, rowspan=2, padx=(10, 10), pady=(5, 5), sticky="w")

        self.song_name_label = ctk.CTkLabel(self.song_details_frame, text=self.song_name, font=self.song_name_font)
        self.song_name_label.grid(row=0, column=1, padx=(10,10), pady=(5,5), sticky="w")

        self.artist_name_label = ctk.CTkLabel(self.song_details_frame, text=self.artist, font=self.song_artist_font)
        self.artist_name_label.grid(row=1, column=1, padx=(10, 10), pady=(5, 5), sticky="w")

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

        self.volume_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.volume_adjust, width=100)
        self.volume_slider.grid(row=0, column=2, rowspan=2, padx=(5, 5), pady=(5, 5), sticky="e")
        self.player.volume = 0.5

        if self.song_details == None:
            self.song_end()

        self.update_progress()

    def song_end(self):
        self.queue_settings = self.load_queue()
        self.current_index = self.queue_settings['current_index'] +1
        self.queue = self.queue_settings['queue']

        if self.current_index >= len(self.queue):
            self.current_index = 0
        queue_config = {
            "current_index": self.current_index,
            "queue": self.queue,
        }
        with open("Databases\\queue.json", "w") as f:
            json.dump(queue_config, f, indent=0)
            f.close()
        if len(self.queue) != 0:
            self.load_song(self.queue[self.current_index])

    def load_queue(self):
        with open("Databases\\queue.json", "r") as f:
            queue_settings = json.load(f)
            f.close()
        return queue_settings

    def load_song(self, songID: int):
        print("hai")
        if self.player:
            self.player.delete()

        self.songID = songID
        self.song_details = self.retrieve_song()

        if self.song_details == None:
            self.queue.remove(self.songID)
            self.song_end()

        self.song_name = self.song_details[2]
        self.artist = self.song_details[4]
        self.duration.set(self.song_details[3])
        self.filepath = self.song_details[1]
        try:
            self.thumbnail_img = Image.open(io.BytesIO(tt.TinyTag.get(self.filepath, image=True).images.any.data))
        except:
            self.thumbnail_img = None

        try:
            self.boot_player()
            self.player.play()
            self.player.volume = 0.5
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
        if self.songID != 0 and self.player.playing and not self.seeking:
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

    def seek(self, time):
        self.seeking=True
        self.player.seek(float(time))

    def init_queue(self):
        current_queue = [self.filepath]
        for song_fp in current_queue:
            try:
                song_obj = pyglet.media.load(song_fp, streaming=False)
                self.player.queue(song_obj)
            except Exception as err:
                tk.messagebox.showwarning("Can't play song", "Song cannot be played removing song from database.")
                print(err)
                self.delete_song()

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
        print(self.player.loop)

    def previous_song(self, event=None):
        print("Previous Song")

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, font: ctk.CTkFont, player_callback):
        super().__init__(master, anchor="s")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color="gray10")

        self.player_callback=player_callback
        TABS = ["Home", "Tracks", "Playlists", "Music Finder"]

        for current_tab in TABS:
            self.add(current_tab)
            self.tab(current_tab).grid_columnconfigure(0, weight=1)
            self.tab(current_tab).grid_rowconfigure(0, weight=1)

        self.home = Home(master=self.tab("Home"), font=font)
        self.home.grid(row=0, column=0, sticky="nsew")

        self.tracks = Tracks(master=self.tab("Tracks"), font=font, player_callback=self.player_callback)
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

        # Needs to be created first to pass player_callback down the chain
        self.player = Player(self)
        self.player.grid(row=1, column=0, padx=(10, 10), pady=(5, 5), sticky="ew")

        self.tab_view = MyTabView(self, font=DEFAULT_FONT, player_callback=self.player.load_song)
        self.tab_view.grid(row=0, column=0, padx=(10,10), pady=(5,5), sticky="nsew")
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)



def destroy_widgets(widgets):
    for widget in widgets:
        widget.destroy()


app = App("Balls")

app.mainloop()