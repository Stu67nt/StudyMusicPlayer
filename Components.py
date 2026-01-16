from widgets import *
import customtkinter
from customtkinter import CTkFrame
import tkinter as tk

class ToDoList(customtkinter.CTkFrame):
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

        self.title_label = customtkinter.CTkLabel(self, text="To Do List:", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new", columnspan=2)

        todo_checkboxes = ["Task 1", "Task 2", "Task 3", "Task 2", "Task 2", "Task 2", "Task 2", "Task 2", "Task 2",
                           "Task 2", "Task 2", "Task 2", "Task 2", "Task 2", "Task 2"]
        self.todo = CheckboxFrame(self, values=todo_checkboxes, is_scrollable=True)
        self.todo.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")

        self.input = customtkinter.CTkEntry(self)
        self.input.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nwe")

        self.buttons = ButtonFrame(self, [["Create Task", self.balls], ["Delete Tasks", self.balls]], is_horizontal = True)
        self.buttons.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="nwe")

    def balls(self):
        print("Balls")

class TimerCreate(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure((1,2,3), weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.BUTTON = [["Start Timer", self.test]]

        self.title_label = customtkinter.CTkLabel(self, text="Timer", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new", columnspan=2)


        self.hours_label = customtkinter.CTkLabel(self, text="Enter Hours: ", fg_color="transparent", corner_radius=6)
        self.hours_label.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="w")

        self.hours_spinbox = tk.Spinbox(self, from_=0, to=23, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.hours_spinbox.grid(row=1, column=1, padx=10, pady=(10, 10), sticky="e")


        self.mins_label = customtkinter.CTkLabel(self, text="Enter Miniutes: ", fg_color="transparent", corner_radius=6)
        self.mins_label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="w")

        self.mins_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.mins_spinbox.grid(row=2, column=1, padx=10, pady=(10, 10), sticky="e")


        self.secs_label = customtkinter.CTkLabel(self, text="Enter Seconds: ", fg_color="transparent", corner_radius=6)
        self.secs_label.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="w")

        self.secs_spinbox = tk.Spinbox(self, from_=0, to=59, repeatdelay=500, repeatinterval=100,
                     font=("Arial", 20))
        self.secs_spinbox.grid(row=3, column=1, padx=10, pady=(10, 10), sticky="e")


        self.button = ButtonFrame(self, self.BUTTON, is_horizontal = True, button_sticky = "nsew")
        self.button.grid(row=4, column=0, padx=10, pady=(10, 10), sticky="nsew", columnspan=2)

    def test(self):
        print("test")

class SongFrame(customtkinter.CTkFrame):
    def __init__(self, master, track_list, is_scrollable=True):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if is_scrollable:
            self.container = customtkinter.CTkScrollableFrame(self)
        else:
            self.container = customtkinter.CTkFrame(self)

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


