import downloader
from widgets import *
from utils import *
import customtkinter as ctk
from customtkinter import CTkFrame
import tkinter as tk
import sqlite3
import json
import os
import threading
import pyglet
from PIL import Image
import io
import tinytag as tt

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
        db = sqlite3.connect("Databases/todo.db")
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
        self.input.delete(0, "end")

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
                     font=("Cascadia Mono", 20))
        self.hours_spinbox.grid(row=1, column=1, padx=10, pady=(10, 10), sticky="e")


        self.mins_label = ctk.CTkLabel(self, text="Enter Minutes: ", fg_color="transparent", corner_radius=6, font=font)
        self.mins_label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="w")

        self.mins_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Cascadia Mono", 20))
        self.mins_spinbox.grid(row=2, column=1, padx=10, pady=(10, 10), sticky="e")


        self.secs_label = ctk.CTkLabel(self, text="Enter Seconds: ", fg_color="transparent", corner_radius=6, font=font)
        self.secs_label.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="w")

        self.secs_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Cascadia Mono", 20))
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

        self.time_text_str = "%02d:%02d:%02d" % (self.hours_remaining.get(), self.mins_remaining.get(), self.secs_remaining.get())
        self.time_text = ctk.StringVar(value=f"{self.time_text_str}")
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
        self.time_text_str = "%02d:%02d:%02d" % (self.hours_remaining.get(), self.mins_remaining.get(), self.secs_remaining.get())
        self.time_text.set(self.time_text_str)
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
        self.time_text_str = "%02d:%02d:%02d" % (self.hours_remaining.get(), self.mins_remaining.get(), self.secs_remaining.get())
        self.time_text.set(self.time_text_str)


class AddToPlaylist(ctk.CTkToplevel):
    def __init__(self, songIDs: list, font: ctk.CTkFont, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry('450x450')
        self.title("Add To Playlist")
        self.resizable(width=False, height=False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.songIDs = songIDs
        self.font = font
        self.playlists = self.retrieve_playlist_details()
        self.playlist_names = []
        for playlist in self.playlists:
            playlist_name = f"{playlist[0]} - {playlist[1]}"
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
        checked = self.playlists_checkbox.get_checkboxes()
        print(checked)
        for playlist in checked:
            playlistID = int(playlist.split(" ")[0])
            for songID in self.songIDs:
                self.add_song_to_playlist(songID, playlistID)

        self.destroy()

    def add_song_to_playlist(self, songID, playlistID):
        db = init_playlist_database()
        cursor = db.cursor()
        query = ("INSERT INTO "
                 "Playlist("
                 "PlaylistID,"
                 "songID"
                 ")"
                 "VALUES (?, ?)")
        cursor.execute(query, (playlistID, songID))
        db.commit()
        db.close()

    def retrieve_playlist_details(self):
        cursor = init_playlist_list_database().cursor()
        query = ("SELECT * FROM Playlist_List")
        cursor.execute(query)
        playlist_details = cursor.fetchall()
        configured_playlist_details = []
        for playlist in playlist_details:
            configured_playlist_details.append([playlist[0],playlist[1]])
        return configured_playlist_details



class SongFrame(ctk.CTkFrame):
    def __init__(self, master, song_ids, font: ctk.CTkFont, player_callback, is_scrollable=True):
        super().__init__(master)

        self.player_callback=player_callback

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

        self.track_list = song_ids
        self.labels = []
        i=0
        for songID in self.track_list:
            try:
                self.song_label = SongLabel(self.container,
                                            songID=songID,
                                            font=font,
                                            player_callback=self.player_callback)
                self.song_label.grid(row=i, column=0, padx=(10,10), pady=1, sticky="ew")
                self.labels.append(self.song_label)
                i+=1
            except Exception as err:
                try:
                    tk.messagebox.showerror("Missing song", err)
                    self.track_list.remove(songID)
                except:
                    pass


class PlaylistFrame(ctk.CTkFrame):
    def __init__(self,
                 master,
                 playlistIDs,
                 font: ctk.CTkFont,
                 player_callback,
                 open_playlist_callback,
                 is_scrollable=True):
        super().__init__(master)

        self.player_callback = player_callback
        self.song_ids = []
        self.font = font
        self.playlistIDs = playlistIDs
        self.widgets = []

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

        i=0
        for playlistID in self.playlistIDs:
            playlist_info = self.retrieve_playlist(playlistID)
            playlistID = playlist_info[0]
            playlist_name = playlist_info[1]
            self.playlist_label = PlaylistLabel(self.container,
                                                playlistID=playlistID,
                                                playlist_name=playlist_name,
                                                font=self.font,
                                                open_playlist_callback=open_playlist_callback,
                                                player_callback=player_callback)
            self.playlist_label.grid(row=i, column=0, padx=(10,10), pady=1, sticky="ew")
            self.widgets.append(self.playlist_label)
            i+=1

    def retrieve_playlist(self, playlistID):
        db = init_playlist_list_database()
        cursor = db.cursor()
        query = "SELECT * FROM Playlist_List WHERE PlaylistID = ?"
        cursor.execute(query, (playlistID,))
        playlist = cursor.fetchone()
        return playlist

class SearchFrame(ctk.CTkFrame):
    def __init__(self, master, font=ctk.CTkFont, progress_bar_callback=None):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.BUTTONS = [["Download Song", self.search],
                        ["Download Settings", self.download_settings]]
        self.font = font
        self.settings_screen = None
        self.progress_bar_callback = progress_bar_callback

        self.title = ctk.CTkLabel(self,
                                  text = "Download a song from YouTube",
                                  font = self.font,
                                  fg_color="transparent")
        self.title.grid(row = 0, column = 0, sticky = "new", padx=(10,10), pady=(10,10))

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter YouTube URL", font=self.font)
        self.entry.grid(row=1, column=0, sticky = "new", padx=(10,10), pady=(10,10))

        self.buttons = ButtonFrame(self, button_values=self.BUTTONS, is_horizontal=True, font=self.font)
        self.buttons.grid(row=2, column = 0, sticky = "ew", padx=(10,10), pady=(10,10))

    def search(self, event = None):
        inp = self.entry.get()
        print(f"Downloading the url {inp}")
        try:
            threading.Thread(target = downloader.download,
                             args = (inp, downloader.create_download_config(self.progress_bar_callback)),
                             daemon = False).start()
        except Exception as err:
            tk.messagebox.showerror("Download Error", err)
            print("Complete!")


    def download_settings(self, event = None):
        if self.settings_screen is None or not self.settings_screen.winfo_exists():
            self.settings_screen = DownloadSettings(self)
        if self.settings_screen is not None and self.settings_screen.winfo_exists():
            self.settings_screen.focus()  # if window exists focus it


class DownloadSettings(ctk.CTkToplevel):
    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry('500x450')
        self.title("Download Settings")
        self.resizable(width = False, height = False)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.f = open("Databases/config.json")
        self.options = json.load(self.f)
        self.f.close()

        self.TEXT_FONT = ctk.CTkFont(family="Cascadia Mono", size=18)

        self.label = ctk.CTkLabel(self,
                                  text="Download Settings",
                                  font = self.TEXT_FONT)
        self.label.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky = "ew")


        self.settings_frame = ctk.CTkScrollableFrame(self, fg_color = "transparent")
        self.settings_frame.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky = "nsew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.prefered_format_label = ctk.CTkLabel(self.settings_frame, text="Preferred Format:", font = self.TEXT_FONT)
        self.prefered_format_label.grid(row=1, column=0, padx=(10,10), sticky = "w")
        self.prefered_format_select = ctk.CTkOptionMenu(self.settings_frame,
                                                        values=['m4a', 'mp3', 'flac'],
                                                        font=self.TEXT_FONT,
                                                        )
        self.prefered_format_select.grid(row=1, column=1, padx=(10, 10), pady=(10, 10), sticky="e")

        self.add_thumbnail_select = RadioButtonFrame(self.settings_frame,
                                              values=["Yes", "No"],
                                              title="Embed Thumbnails:",
                                              font=self.TEXT_FONT,
                                              is_horizontal=True,
                                              button_sticky="e",
                                              )
        self.add_thumbnail_select.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="ew", columnspan=2)

        self.confirm_button = ctk.CTkButton(self, text="Confirm", command=self.write_config)
        self.confirm_button.grid(row=6, column=0, padx=(10, 10), pady=(10, 10))

    def write_config(self):
        prefered_format = self.prefered_format_select.get()
        add_thumbnail = self.add_thumbnail_select.get_radio_val()


        if prefered_format == "mp3":
            self.options['format'] = 'mp3/m4a/flac/bestaudio'
        elif prefered_format == "m4a":
            self.options['format'] = 'm4a/mp3/flac/bestaudio'
        elif prefered_format == "flac":
            self.options['format'] = 'flac/m4a/mp3/bestaudio'

        if add_thumbnail == "Yes":
            self.options["write_thumbnail"] = True
        elif add_thumbnail == "No":
            self.options["write_thumbnail"] = False

        with open("Databases\\config.json", "w") as f:
            json.dump(self.options, f, indent=4)
            f.close()
        self.destroy()


class QueueViewer(ctk.CTkToplevel):
    def __init__(self, event, font: ctk.CTkFont, player_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.title("Queue")
        self.geometry("500x700")
        self.font = font
        self.queue = []
        self.old_index = -1
        self.player_callback = player_callback

        self.label = ctk.CTkLabel(self,
                                  text="Queue",
                                  font=self.font)
        self.label.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")

        self.label = ctk.CTkButton(self,
                                  text="Clear Queue",
                                  font=self.font,
                                  command = self.queue_clear)
        self.label.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")

        self.queue_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.queue_frame.grid(row=1, column=0, columnspan=2, pady=(10, 10), sticky="nsew")
        self.queue_frame.grid_columnconfigure(0, weight=1)

        self.update_queue(event)

    def load_queue(self):
        with open("Databases\\queue.json", "r") as f:
            queue_settings = json.load(f)
            f.close()
        return queue_settings

    def update_queue(self, event):
        self.queue_settings = self.load_queue()
        current_index = self.queue_settings["current_index"]
        if self.queue != self.queue_settings["queue"] or self.old_index != current_index:
            self.old_index = self.queue_settings["current_index"]
            for widget in self.queue_frame.winfo_children():
                widget.destroy()
            self.queue = self.queue_settings["queue"]
            i = 0
            for songID in self.queue:
                self.song_details = self.retrieve_song(songID)
                if self.song_details != None:
                    self.songID = songID
                    self.song_name = self.song_details[2]
                    self.artist = self.song_details[4]

                    self.song_label_frame = ctk.CTkFrame(self.queue_frame, corner_radius=0, border_color="grey10", border_width=1)
                    self.song_label_frame.grid(column=0, row=i, sticky="ew", padx=(10, 10))
                    self.song_label_frame.grid_columnconfigure((1,2), weight=1)

                    if songID == event.widget.master.master.songID:
                        self.song_label_frame.configure(fg_color="grey10")

                    self.song_name_label = ctk.CTkLabel(self.song_label_frame, text=self.song_name,
                                                        font=self.font)
                    self.song_name_label.grid(row=0, column=1, padx=(5,5), pady=(5, 5), sticky="w")

                    self.artist_name_label = ctk.CTkLabel(self.song_label_frame, text=self.artist,
                                                          font=self.font)
                    self.artist_name_label.grid(row=1, column=1, padx=(5,5), pady=(5, 5), sticky="w")

                    options_button_font = ctk.CTkFont(family="Cascadia Mono", size=30, weight="bold")
                    self.remove_button = ctk.CTkLabel(self.song_label_frame, text="X", font=options_button_font)
                    self.remove_button.grid(column=2, row=0, rowspan=2, padx=(5,5), pady=(5,5), sticky="e")

                    self.song_label_frame.bind("<Button-1>",
                                             lambda event, sID=songID: self.jump_to_song(event, sID))
                    self.song_name_label.bind("<Button-1>",
                                             lambda event, sID=songID: self.jump_to_song(event, sID))
                    self.artist_name_label.bind("<Button-1>",
                                             lambda event, sID=songID: self.jump_to_song(event, sID))
                    self.remove_button.bind("<Button-1>",
                                             lambda event, sID=songID: self.remove_from_queue(event, sID))

                    i += 1

        self.after(200, lambda: self.update_queue(event))

    def retrieve_song(self, songID):
        self.db = downloader.init_database()
        cursor = self.db.cursor()
        query = "SELECT * FROM songs WHERE songID = ?"
        cursor.execute(query, (songID,))
        song_details = cursor.fetchone()
        self.db.close()
        return song_details

    def menu_trigger(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def jump_to_song(self, event, songID):
        queue_settings = self.load_queue()
        queue = queue_settings["queue"]
        current_index = queue.index(songID)
        queue_settings = {
            "current_index": current_index,
            "queue": queue
        }
        with open("Databases\\queue.json", "w") as f:
            json.dump(queue_settings, f, indent=0)
            f.close()
        self.player_callback.load_song(songID)

    def remove_from_queue(self, event, songID):
        queue_settings = self.load_queue()
        queue = queue_settings["queue"]
        current_index = queue_settings["current_index"]
        if current_index >= queue.index(songID):
            queue.remove(songID)
            current_index -= 1
        else:
            queue.remove(songID)
        if len(queue) == 0:  # Queue cannot be left blank
            queue = [-1]
            current_index = 0
        queue_settings = {
            "current_index": current_index,
            "queue": queue
        }

        with open("Databases\\queue.json", "w") as f:
            json.dump(queue_settings, f, indent=0)
            f.close()

    def queue_clear(self):
        queue_settings = {
            "current_index": 0,
            "queue": [-1]
        }
        with open("Databases\\queue.json", "w") as f:
            json.dump(queue_settings, f, indent=0)
            f.close()

def destroy_widgets(widgets):
    for widget in widgets:
        widget.destroy()
        widgets.remove(widget)
    return widgets