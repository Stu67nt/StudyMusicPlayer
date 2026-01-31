from widgets import *
import customtkinter as ctk
from customtkinter import CTkFrame
import tkinter as tk
import sqlite3

class ToDoList(ctk.CTkFrame):
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master)

        self.db = self.init_database()
        self.font = font

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="To Do List:", fg_color="gray30", corner_radius=6, font=font)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new", columnspan=2)

        self.task_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.task_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.input = ctk.CTkEntry(self, font=self.font)
        self.input.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nwe")

        self.buttons = ButtonFrame(self,
                                   button_values=[["Create Task",self.create_task],
                                    ["Delete Tasks", self.delete_tasks]],
                                   is_horizontal = True,
                                   button_sticky = "ew",
                                   font = self.font)
        self.buttons.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="ew")

        self.load_tasks()

    def init_database(self):
        db = sqlite3.connect("todo.db")
        cursor = db.cursor()
        query = ("CREATE TABLE IF NOT EXISTS "
                 "todo(" 
                 "taskID INTEGER PRIMARY KEY AUTOINCREMENT," 
                 "task TEXT,"
                 "is_checked INTEGER"
                 ")")
        cursor.execute(query)
        db.commit()
        return db

    def retrieve_tasks(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * from todo")
        tasks = cursor.fetchall()
        return tasks

    def load_tasks(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        todo_tasks = self.retrieve_tasks()

        for i, task in enumerate(todo_tasks):
            task_id = task[0]
            task_name = task[1]
            is_completed = ctk.IntVar(value=task[2])

            checkbox = ctk.CTkCheckBox(
                self.task_frame,
                text=task_name,
                variable=is_completed,
                command=lambda t_id=task_id, ticked = is_completed: self.toggle_task(t_id, ticked),
                font=self.font
            )
            checkbox.grid(row=i, column=0, padx=(5,5), pady=(5,5), sticky="w")

    def toggle_task(self, task_id, is_completed):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE todo SET is_checked = ? WHERE taskID = ?",
            (is_completed.get(), task_id)
        )
        self.db.commit()

    def create_task(self):
        # Getting text input adding it to list and regenerating new checkbox frame
        task = self.input.get().strip()
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO todo (task, is_checked) VALUES (?, 0)",
            (task,)
        )
        self.db.commit()
        self.load_tasks()

    def delete_tasks(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM todo WHERE is_checked=1")
        self.db.commit()
        self.load_tasks()

class TimerCreate(ctk.CTkFrame):
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master)

        self.grid_rowconfigure((1,2,3), weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.BUTTON = [["Start Timer", self.start_timer]]
        self.timer = None

        self.title_label = ctk.CTkLabel(self, text="Timer", fg_color="gray30", corner_radius=6, font = font)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new", columnspan=2)


        self.hours_label = ctk.CTkLabel(self, text="Enter Hours: ", fg_color="transparent", corner_radius=6, font=font)
        self.hours_label.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="w")

        self.hours_spinbox = tk.Spinbox(self, from_=0, to=23, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.hours_spinbox.grid(row=1, column=1, padx=10, pady=(10, 10), sticky="e")


        self.mins_label = ctk.CTkLabel(self, text="Enter Miniutes: ", fg_color="transparent", corner_radius=6, font=font)
        self.mins_label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="w")

        self.mins_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.mins_spinbox.grid(row=2, column=1, padx=10, pady=(10, 10), sticky="e")


        self.secs_label = ctk.CTkLabel(self, text="Enter Seconds: ", fg_color="transparent", corner_radius=6, font=font)
        self.secs_label.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="w")

        self.secs_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.secs_spinbox.grid(row=3, column=1, padx=10, pady=(10, 10), sticky="e")


        self.button = ButtonFrame(self, self.BUTTON, is_horizontal = True, button_sticky = "ew", font=font)
        self.button.grid(row=4, column=0, padx=10, pady=(10, 10), sticky="ew", columnspan=2)


    def start_timer(self, event=None):
        if self.timer is None or not self.timer.winfo_exists():
            self.timer = Timer(self)  # create window if its None or destroyed
        self.timer.focus()
        self.timer.focus() # if window exists focus it


class Timer(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Timer")
        self.resizable(width = False, height = False)
        self.rowconfigure((0,2), weight=1)
        self.columnconfigure(0, weight=1)

        TEXT_FONT = ctk.CTkFont(family="Comic Sans MS", size= 25)
        TIMER_FONT = ctk.CTkFont(family="Comic Sans MS", size= 50)
        BUTTON_FONT = ctk.CTkFont(family="Comic Sans MS", size = 20)
        BUTTONS = [["⏸", self.toggle_pause], ["⟳", self.reset_timer]]


        self.hours_remaining = tk.IntVar(value=23)
        self.mins_remaining = tk.IntVar(value=59)
        self.secs_remaining = tk.IntVar(value=59)

        self.label = ctk.CTkLabel(self,
                                  text="Time Remaining",
                                  font = TEXT_FONT)
        self.label.grid(row=0, column=0, padx=(10,10), pady=(10,10))

        self.timer_frame = ctk.CTkFrame(self,
                                        border_color="white",
                                        border_width=5,
                                        fg_color="transparent")
        self.timer_frame.grid(row=1, column=0)

        self.time_remaining = ctk.CTkLabel(self.timer_frame,
                                           text = f"{self.hours_remaining.get()}:{self.mins_remaining.get()}:{self.secs_remaining.get()}",
                                           font = TIMER_FONT)
        self.time_remaining.grid(row=0, column=0, sticky="nsew", padx=(10,10), pady=(10,10))

        self.buttons = ButtonFrame(self,
                                   button_values = BUTTONS,
                                   is_horizontal=True,
                                   button_frame_color = "transparent",
                                   font = BUTTON_FONT)
        self.buttons.grid(row=2, column = 0, sticky = "ew", padx=(10,10), pady=(10,10))

    def toggle_pause(self):
        print("Toggle Pause")

    def reset_timer(self):
        print("Reset Timer")

class AddToPlaylist(ctk.CTkToplevel):
    def __init__(self, playlists, font: ctk.CTkFont, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry('450x600')
        self.title("Add To Playlist")
        self.resizable(width=False, height=False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.font = font
        self.playlists = playlists
        self.playlist_names = []
        for playlist in self.playlists:
            playlist_name = playlist[0]
            self.playlist_names.append(playlist_name)

        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.grid(row=0, column=0, padx = (10,10), pady=(10,10), sticky="nsew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.playlists_checkbox = CheckboxFrame(master=self.frame,
                                                values=self.playlist_names,
                                                font=self.font,
                                                is_scrollable=True,
                                                title="Select Playlists:")
        self.playlists_checkbox.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky="nsew")

        self.submit = ctk.CTkButton(self.frame,
                                    text="Confirm",
                                    font=self.font,
                                    command=self.submit_playlists)
        self.submit.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky = "ew")

    def submit_playlists(self):
        print(self.playlists_checkbox.get_checkboxes())
        self.destroy()


class SongFrame(ctk.CTkFrame):
    def __init__(self, master, track_list, font: ctk.CTkFont, is_scrollable=True):
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
            self.song_label = SongLabel(self.container,
                                        song_name=song_name,
                                        artist=song_artist,
                                        duration=song_duration,
                                        thumbnail=song_thumbnail,
                                        font=font)
            self.song_label.grid(row=i, column=0, padx=(10,10), pady=1, sticky="ew")
            self.labels.append(self.song_label)
            i+=1


class PlaylistFrame(ctk.CTkFrame):
    def __init__(self, master, playlist_list, font: ctk.CTkFont, is_scrollable=True):
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
            self.playlist_label = PlaylistLabel(self.container,
                                                playlist_name=playlist_name,
                                                song_count=playlist_song_count,
                                                duration=playlist_duration,
                                                font=font)
            self.playlist_label.grid(row=i, column=0, padx=(10,10), pady=1, sticky="ew")
            self.labels.append(self.playlist_label)
            i+=1


class SearchFrame(ctk.CTkFrame):
    def __init__(self, master, font=ctk.CTkFont):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        RADIO_BUTTONS = [["Keyword"], ["Direct"]]
        BUTTONS = [["Search" ,self.search],["Downloads", self.downloads],["Download Settings", self.download_settings]]

        self.mode_radio_buttons = RadioButtonFrame(self,
                                                   values = RADIO_BUTTONS,
                                                   title = "Search for a song on Youtube",
                                                   is_horizontal = True,
                                                   font = font)
        self.mode_radio_buttons.grid(row = 0, column = 0, sticky = "new", padx=(10,10), pady=(10,10))

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter song URL/Keyword", font=font)
        self.entry.grid(row=1, column=0, sticky = "new", padx=(10,10), pady=(10,10))

        self.buttons = ButtonFrame(self, button_values=BUTTONS, is_horizontal=True, font=font)
        self.buttons.grid(row=2, column = 0, sticky = "ew", padx=(10,10), pady=(10,10))

    def search(self, event = None):
        print("Search")

    def downloads(self, event = None):
        print("Downloads")

    def download_settings(self, event = None):
        print("Download Settings")