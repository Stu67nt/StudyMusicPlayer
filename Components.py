from widgets import *
import customtkinter as ctk
from customtkinter import CTkFrame
import tkinter as tk
import sqlite3

class ToDoList(ctk.CTkFrame):
    def __init__(self, master, font: ctk.CTkFont):
        super().__init__(master)

        # Initialising database & font
        self.db = self.init_database()
        self.font = font

        # Configuring grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Drawing and gridding all static elements
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

        # Drawing the tasks. Redrawn after every checklist update
        self.load_tasks()

    def init_database(self):
        """
        Initialises todo.db or creates it if does not exists.
        :return: SQLite3 db object
        """
        db = sqlite3.connect("todo.db")
        cursor = db.cursor()
        query = ("CREATE TABLE IF NOT EXISTS "  # Needed as otherwise of the table is lost the program will not boot
                 "todo(" 
                 "taskID INTEGER PRIMARY KEY AUTOINCREMENT,"  # AUTOINCREMENT ensures a unique id
                 "task TEXT,"
                 "is_checked INTEGER"  # Held as int as customtkinter checkboxes hold state of being checked as int.
                 ")")
        cursor.execute(query)
        db.commit()  # Committing the query
        return db

    def retrieve_tasks(self):
        """
        Returns all current tasks in the db
        :return: 1D list with all current tasks
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * from todo")
        tasks = cursor.fetchall()
        return tasks

    def load_tasks(self):
        """
        Displays the current tasks on the todo list
        """
        # Wiping previous tasks to prevent memory leak
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        # Retireving all current tasks
        todo_tasks = self.retrieve_tasks()

        # iterating through all tasks
        for i, task in enumerate(todo_tasks):
            # Initalising variables
            task_id = task[0]
            task_name = task[1]
            is_completed = ctk.IntVar(value=task[2])

            # All checkboxes placed in decicated frame for the checkboxes inside the main todo list
            checkbox = ctk.CTkCheckBox(
                self.task_frame,
                text=task_name,
                variable=is_completed,
                # Lambda function needed to pass arguments for this specific checkbox
                command=lambda t_id=task_id, ticked = is_completed: self.toggle_task(t_id, ticked),
                font=self.font
            )
            checkbox.grid(row=i, column=0, padx=(5,5), pady=(5,5), sticky="w")

    def toggle_task(self, task_id: int, is_completed: int):
        """
        Updates state of whether a task is checked or not.
        :param task_id: Unique identifier of a specific task
        :param is_completed: 1/0 dependant on if a task should be checked or not
        :return:
        """
        cursor = self.db.cursor()
        # Query striiuctured like this to prevent SQL injection.
        cursor.execute(
            "UPDATE todo SET is_checked = ? WHERE taskID = ?",
            (is_completed.get(), task_id)
        )
        self.db.commit()

    def create_task(self):
        """
        Creates a task to add to todo list and database and updates the frame
        """
        # Getting text input adding it to list and regenerating new checkbox frame
        task = self.input.get().strip()
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO todo (task, is_checked) VALUES (?, 0)",
            (task,)
        )
        self.db.commit()
        # Reloading task frame because of update
        self.load_tasks()

    def delete_tasks(self):
        """
        Removes all checked tasks and reloads task frame
        """
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
        # Input validation
        if self.hours_spinbox.get().isdigit() and self.mins_spinbox.get().isdigit() and self.secs_spinbox.get().isdigit():
            valid = True
            self.hours = int(self.hours_spinbox.get())
            self.mins = int(self.mins_spinbox.get())
            self.secs = int(self.secs_spinbox.get())
            if self.hours > 23:
                self.hours = 23
            if self.mins > 59:
                self.mins = 59
            if self.secs > 59:
                self.secs = 59
            if (3600*self.hours)+(60*self.mins)+self.secs == 0:
                valid = False
        else:
            valid = False

        if (self.timer is None or not self.timer.winfo_exists()) and valid:
            self.timer = Timer(self,
                               hours=self.hours,
                               mins=self.mins,
                               secs=self.secs)
        if self.timer is not None and self.timer.winfo_exists():
            self.timer.focus() # if window exists focus it


class Timer(ctk.CTkToplevel):
    def __init__(self, event, hours, mins, secs, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Timer")
        self.resizable(width = False, height = False)
        self.rowconfigure((0,2), weight=1)
        self.columnconfigure(0, weight=1)

        self.TEXT_FONT = ctk.CTkFont(family="Comic Sans MS", size= 25)
        self.TIMER_FONT = ctk.CTkFont(family="Monospace", size= 50)
        self.BUTTON_FONT = ctk.CTkFont(family="Comic Sans MS", size = 20)
        self.BUTTONS = [["⏸", self.toggle_pause], ["⟳", self.reset_timer]]

        self.init_secs = (3600*hours)+(60*mins)+secs
        self.total_remaining_secs = self.init_secs
        self.hours_remaining, self.mins_remaining, self.secs_remaining = self.convert_time(self.total_remaining_secs)
        self.is_paused = False

        self.label = ctk.CTkLabel(self,
                                  text="Time Remaining",
                                  font = self.TEXT_FONT)
        self.label.grid(row=0, column=0, padx=(10,10), pady=(10,10))

        self.timer_frame = ctk.CTkFrame(self,
                                        border_color="white",
                                        border_width=5,
                                        fg_color="transparent")
        self.timer_frame.grid(row=1, column=0)

        self.time_text = ctk.StringVar(value=f"{self.hours_remaining.get()}:{self.mins_remaining.get()}:{self.secs_remaining.get()}")
        self.time_remaining_label = ctk.CTkLabel(self.timer_frame,
                                                 textvariable=self.time_text,
                                                 font=self.TIMER_FONT)
        self.time_remaining_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.buttons = ButtonFrame(self,
                                   button_values = self.BUTTONS,
                                   is_horizontal=True,
                                   button_frame_color = "transparent",
                                   font = self.BUTTON_FONT)
        self.buttons.grid(row=2, column = 0, sticky = "ew", padx=(10,10), pady=(10,10))

        # DOCUMENT BUG
        # No warning given once time finishes. Due to total_remaining_secs only being checked once at start.
        # TO recreate add the following lines to __init__():
        """
                if self.total_remaining_secs <= 0:
            print("TIMEEEE")
            self.reset_timer()
        """

        # DOCUMENT BUG
        # When spamming unpausing after spamming pause seconds sick down much faster than expected.
        # To recreate remove the self.after_cancel(self.deincrement)'s

        # And remove the code in update time
        if self.total_remaining_secs > 0:
            self.deincrement = self.update_time()

    def toggle_pause(self):
        if not self.is_paused:
            self.is_paused = True
            self.after_cancel(self.deincrement)
        else:
            self.is_paused = False
            if self.total_remaining_secs > 0:
                self.deincrement = self.update_time()

    def reset_timer(self):
        self.after_cancel(self.deincrement)
        self.total_remaining_secs = self.init_secs
        self.is_paused = True
        # DOCUMNET BUG
        # When timer reset the reset time is not immediately displayed instead only displayed after waiting a second for time to deincrement
        # Recreate by adding the 3 lines below. REmove to recreate
        """
        self.hours_remaining, self.mins_remaining, self.secs_remaining = self.convert_time(self.total_remaining_secs)
        self.time_remaining_label = ctk.CTkLabel(self.timer_frame,
                                                 text=f"{self.hours_remaining.get()}:{self.mins_remaining.get()}:{self.secs_remaining.get()}",
                                                 font=self.TIMER_FONT)
        self.time_remaining_label.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=(10, 10))
        """
        # Displaying updated time
        self.hours_remaining, self.mins_remaining, self.secs_remaining = self.convert_time(self.total_remaining_secs)
        self.time_text.set(f"{self.hours_remaining.get()}:{self.mins_remaining.get()}:{self.secs_remaining.get()}")
        pass

    def convert_time(self, secs):
        hours = ctk.IntVar(value=int(secs / 3600))
        mins = ctk.IntVar(value=int((secs % 3600) / 60))
        secs = ctk.IntVar(value=int((secs % 3600) % 60))
        return hours, mins, secs

    def update_time(self):
        self.total_remaining_secs -= 1


        if (self.total_remaining_secs >= 0) and not self.is_paused:
            self.deincrement = self.after(1000, self.update_time)  # Recursive
        if self.total_remaining_secs < 0:
            print("TIMEEEE")
            self.toggle_pause()
            return 0  # Needed so timer does not de icnrement once reset
        self.hours_remaining, self.mins_remaining, self.secs_remaining = self.convert_time(self.total_remaining_secs)
        self.time_text.set(f"{self.hours_remaining.get()}:{self.mins_remaining.get()}:{self.secs_remaining.get()}")


class AddToPlaylist(ctk.CTkToplevel):
    def __init__(self, playlists, font: ctk.CTkFont, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry('450x450')
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