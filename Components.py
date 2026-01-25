from widgets import *
import customtkinter as ctk
from customtkinter import CTkFrame
import tkinter as tk

class ToDoList(ctk.CTkFrame):
    """
    TODO:
        Tie todo_checkboxes list to the db
        Create the to_do db
        Pretty much make the thing functional
    """
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="To Do List:", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new", columnspan=2)

        todo_checkboxes = ["Task 1", "Task 2", "Task 3", "Task 2", "Task 2", "Task 2", "Task 2", "Task 2", "Task 2",
                           "Task 2", "Task 2", "Task 2", "Task 2", "Task 2", "Task 2"]
        self.todo = CheckboxFrame(self, values=todo_checkboxes, is_scrollable=True)
        self.todo.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")

        self.input = ctk.CTkEntry(self)
        self.input.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nwe")

        self.buttons = ButtonFrame(self, [["Create Task", self.create_task], ["Delete Tasks", self.delete_tasks]], is_horizontal = True, button_sticky = "ew")
        self.buttons.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="ew")

    def create_task(self):
        print("Create task")
    def delete_tasks(self):
        print("Delete Tasks")


class TimerCreate(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure((1,2,3), weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.BUTTON = [["Start Timer", self.start_timer]]
        self.timer = None

        self.title_label = ctk.CTkLabel(self, text="Timer", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new", columnspan=2)


        self.hours_label = ctk.CTkLabel(self, text="Enter Hours: ", fg_color="transparent", corner_radius=6)
        self.hours_label.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="w")

        self.hours_spinbox = tk.Spinbox(self, from_=0, to=23, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.hours_spinbox.grid(row=1, column=1, padx=10, pady=(10, 10), sticky="e")


        self.mins_label = ctk.CTkLabel(self, text="Enter Miniutes: ", fg_color="transparent", corner_radius=6)
        self.mins_label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="w")

        self.mins_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.mins_spinbox.grid(row=2, column=1, padx=10, pady=(10, 10), sticky="e")


        self.secs_label = ctk.CTkLabel(self, text="Enter Seconds: ", fg_color="transparent", corner_radius=6)
        self.secs_label.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="w")

        self.secs_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.secs_spinbox.grid(row=3, column=1, padx=10, pady=(10, 10), sticky="e")


        self.button = ButtonFrame(self, self.BUTTON, is_horizontal = True, button_sticky = "ew")
        self.button.grid(row=4, column=0, padx=10, pady=(10, 10), sticky="ew", columnspan=2)


    def start_timer(self, event=None):
        if self.timer is None or not self.time.winfo_exists():
            self.timer = Timer(self)  # create window if its None or destroyed
        self.timer.focus()
        self.timer.focus() # if window exists focus it


class Timer(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="ToplevelWindow")
        self.label.pack(padx=20, pady=20)


class SongFrame(ctk.CTkFrame):
    def __init__(self, master, track_list, is_scrollable=True):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if is_scrollable:
            self.container = ctk.CTkScrollableFrame(self)
        else:
            self.container = ctk.CTkFrame(self)

        # This line below is there so the frame scales to take up the free space
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.track_list = track_list
        self.labels = []
        i=0
        for song_info in self.track_list:
            song_name = song_info[0]
            song_artist = song_info[1]
            song_duration = song_info[2]
            song_thumbnail = song_info[3]
            self.song_label = SongLabel(self.container, song_name=song_name, artist=song_artist,
                                            duration=song_duration, thumbnail=song_thumbnail)
            self.song_label.grid(row=i, column=0, padx=(10,10), pady=1, sticky="ew")
            self.labels.append(self.song_label)
            i+=1


class PlaylistFrame(ctk.CTkFrame):
    def __init__(self, master, playlist_list, is_scrollable=True):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if is_scrollable:
            self.container = ctk.CTkScrollableFrame(self)
        else:
            self.container = ctk.CTkFrame(self)

        # This line below is there so the frame scales to take up the free space
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.playlist_list = playlist_list
        self.labels = []
        i=0
        for playlist_info in self.playlist_list:
            playlist_name = playlist_info[0]
            playlist_song_count = playlist_info[1]
            playlist_duration = playlist_info[2]
            self.playlist_label = PlaylistLabel(self.container, playlist_name=playlist_name,
                                                song_count=playlist_song_count, duration=playlist_duration)
            self.playlist_label.grid(row=i, column=0, padx=(10,10), pady=1, sticky="ew")
            self.labels.append(self.playlist_label)
            i+=1


class SearchFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        RADIO_BUTTONS = [["Keyword"], ["Direct"]]
        BUTTONS = [["Search" ,self.search],["Downloads", self.downloads],["Download Settings", self.download_settings]]

        self.mode_radio_buttons = RadioButtonFrame(self,
                                                   values = RADIO_BUTTONS,
                                                   title = "Search for a song on Youtube",
                                                   is_horizontal = True)
        self.mode_radio_buttons.grid(row = 0, column = 0, sticky = "new", padx=(10,10), pady=(10,10))

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter song URL/Keyword")
        self.entry.grid(row=1, column=0, sticky = "new", padx=(10,10), pady=(10,10))

        self.buttons = ButtonFrame(self, button_values=BUTTONS, is_horizontal=True)
        self.buttons.grid(row=2, column = 0, sticky = "ew", padx=(10,10), pady=(10,10))

    def search(self, event = None):
        print("Search")

    def downloads(self, event = None):
        print("Downloads")

    def download_settings(self, event = None):
        print("Download Settings")