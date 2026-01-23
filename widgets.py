import customtkinter
from customtkinter import CTkFrame
import tkinter as tk

"""
TODO: 
Allow for fg_colour and corner radius to be scaled.
Fix Sticky

Widgets exists to hold the most fundamental GUI elements which make up the program. Complex GUI elements such as 
the To Do Lists will be found in Components.py
"""

class ButtonFrame(customtkinter.CTkFrame):
    """A frame which holds buttons. Not Scrollable."""
    def __init__(self,
                 master,
                 button_values: list,
                 title: str = "",
                 is_horizontal: bool = False,
                 title_sticky: str = "nsew",
                 title_fg_color: str = "gray30",
                 title_corner_radius:int = 6,
                 button_sticky: str = "nsew"):
        super().__init__(master) # Calls/runs parent class. This is necessary so it initialises the inherited class.

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.button_values = button_values
        self.buttons = []
        self.title = title

        # Creating and positioning title in frame
        if self.title != "":
            self.title_label = customtkinter.CTkLabel(self, text=self.title, fg_color=title_fg_color,
                                                      corner_radius=title_corner_radius)
            self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=title_sticky)
            self.grid_columnconfigure(0, weight=0)
            self.grid_rowconfigure(0, weight=0)

        self.button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=0 if is_horizontal else 1,
                                   column=1 if is_horizontal else 0,
                                   padx=20,
                                   pady=20,
                                   sticky=button_sticky)


        # Iterating through each item in values and creating a button for it.
        # Each button is then added to a list of buttons so we can track their state.
        for i, value in enumerate(self.button_values):
            self.button = customtkinter.CTkButton(self.button_frame, text=value[0], command=value[1])
            if is_horizontal:
                self.button.grid(row=0, column=i, padx=20, pady=20, sticky=button_sticky)
                self.grid_columnconfigure(i, weight=1)
            else:
                self.button.grid(row=i, column=0, padx=20, pady=20, sticky=button_sticky)
                self.grid_rowconfigure(i, weight=1)

            self.buttons.append(self.button)


class CheckboxFrame(customtkinter.CTkFrame):  # Inheriting CTkFrame class
    # A frame holding Checkboxes
    def __init__(self,
                 master,
                 values: list,
                 title: str = "",
                 is_horizontal: bool = False,
                 is_scrollable: bool = False):
        super().__init__(master) # Calls/runs parent class. This is necessary so it initialises the inherited class.

        if is_scrollable:
            self.container = customtkinter.CTkScrollableFrame(self)
        else:
            self.container = customtkinter.CTkFrame(self)

        # This line below is there so the frame scales to take up the free space
        self.container.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.values = values
        self.checkboxes = []
        self.title = title

        # Creating and positioning title in frame
        if self.title != "":
            self.title_label = customtkinter.CTkLabel(self.container, text=self.title, fg_color="gray30", corner_radius=6)
            self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nwe")

        # Iterating through each item in values and creating a checkbox for it.
        # Each checkbox is then added to a list of checkboxes so we can track their state.
        for i, value in enumerate(self.values):
            self.checkbox = customtkinter.CTkCheckBox(self.container, text=value)
            if is_horizontal:
                self.checkbox.grid(row=0, column=i+1, padx=20, pady=20, sticky="w")
            else:
                self.checkbox.grid(row=i + 1, column=0, padx=20, pady=20, sticky="w")
            self.checkboxes.append(self.checkbox)

    # Returning which checkboxes have been ticked.
    def get_checkboxes(self):
        checked = []
        for box in self.checkboxes:
            if box.get() == 1:
                checked.append(box.cget("text"))
        return checked


class RadioButtonFrame(customtkinter.CTkFrame):
    def __init__(self,
                 master,
                 values: list,
                 title: str,
                 is_horizontal: bool = False,
                 is_scrollable: bool = False,
                 title_sticky: str = "nesw",
                 title_fg_color: str = "gray30",
                 title_corner_radius:int = 6,
                 button_sticky: str = "nesw"):
        super().__init__(master)  # Initilising parent class

        if is_scrollable:
            self.container = customtkinter.CTkScrollableFrame(self)
        else:
            self.container = customtkinter.CTkFrame(self)

        self.container.grid(row=0, column=0, sticky="new")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialising vars
        self.values = values
        self.title = title
        self.var = customtkinter.StringVar(value = "")

        # Creating title label
        if self.title != "":
            self.title_label = customtkinter.CTkLabel(self.container, text=self.title, fg_color=title_fg_color,
                                                corner_radius=title_corner_radius)
            self.title_label.grid(row=0, column=0, sticky=title_sticky)

        # Iterating thorugh each value
        for i, value in enumerate(self.values):
            self.radio_button = customtkinter.CTkRadioButton(self.container, text=value, variable=self.var, value=value)
            if is_horizontal:
                self.radio_button.grid(row=0, column=i+1, padx=20, pady=20, sticky=button_sticky)
            else:
                self.radio_button.grid(row=i + 1, column=0, padx=20, pady=20, sticky=button_sticky)

    def get_radio_val(self):
        return self.var.get()

class LabelFrame(customtkinter.CTkFrame):
    def __init__(self,
                 master,
                 values: list,
                 title: str = "",
                 is_horizontal: bool = False,
                 is_scrollable: bool = False,
                 title_sticky: str = "nesw",
                 title_fg_color: str = "gray30",
                 title_corner_radius: int = 6,
                 button_sticky: str = "nesw"):
        super().__init__(master)  # Calls/runs parent class. This is necessary so it initialises the inherited class.

        if is_scrollable:
            self.container = customtkinter.CTkScrollableFrame(self)
        else:
            self.container = customtkinter.CTkFrame(self)

        # This line below is there so the frame scales to take up the free space
        self.container.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.values = values
        self.labels = []
        self.title = title

        # Creating and positioning title in frame
        if self.title != "":  # As empty string is default if this is true means title is wanted.
            self.title_label = customtkinter.CTkLabel(self.container, text=self.title, fg_color=title_fg_color,
                                                      corner_radius=title_corner_radius)
            self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=title_sticky)

        # Iterating through each item in values and creating a button for it.
        # Each button is then added to a list of buttons so we can track their state.
        for i, value in enumerate(self.values):
            self.label = customtkinter.CTkLabel(self.container, text=value[0])
            if is_horizontal:
                self.label.grid(row=0, column=i + 1, padx=20, pady=20, sticky=button_sticky)
            else:
                self.label.grid(row=i + 1, column=0, padx=20, pady=20, sticky=button_sticky)
            self.labels.append(self.label)

        for i in range(len(self.labels)):
            self.labels[i].bind("<Button-1>", self.values[i][1])

class SongLabel(customtkinter.CTkFrame):
    """
    TODO: Add default thumbnail.
          Create Checkboxable version
    """
    def __init__(self,
                 master,
                 song_name,
                 duration,
                 artist,
                 thumbnail = None):
        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        if thumbnail != None:
            self.thumbnail_label = customtkinter.CTkLabel(self, image = thumbnail)
            self.thumbnail_label.grid(column=0, row=0, sticky="nw", rowspan = 2)

        self.name_label = customtkinter.CTkLabel(self, text = song_name)
        self.name_label.grid(column=1, row=0, padx=(10,10), sticky= "nw")

        self.artist_label = customtkinter.CTkLabel(self, text = artist)
        self.artist_label.grid(column=1, row=1, padx=(10, 10), sticky="nw")

        self.duration_label = customtkinter.CTkLabel(self, text=duration)
        self.duration_label.grid(column=2, row=0, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="e")

        self.options_button = customtkinter.CTkLabel(self, text = "⋮")
        self.options_button.grid(column=3, row=0, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="e")

        MENU_OPTIONS = ["Add to Playlist", "Delete Song", "Add to Queue"]

        self.menu = tk.Menu(self, tearoff=0)
        for name in MENU_OPTIONS:
            self.menu.add_command(label=name)

        self.options_button.bind("<Button-1>", self.menu_trigger)

    # ChatGPT Slop - Change it
    def menu_trigger(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

class PlaylistLabel(customtkinter.CTkFrame):
    """
    TODO: Add default thumbnail.
          Create Checkboxable version
          BInding click to relevant playlist
    """
    def __init__(self,
                 master,
                 playlist_name,
                 song_count,
                 duration):
        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.name_label = customtkinter.CTkLabel(self, text = playlist_name)
        self.name_label.grid(column=1, row=0, padx=(10,10), sticky= "nw")

        self.song_count_label = customtkinter.CTkLabel(self, text = song_count)
        self.song_count_label.grid(column=1, row=1, padx=(10, 10), sticky="nw")

        self.duration_label = customtkinter.CTkLabel(self, text=duration)
        self.duration_label.grid(column=2, row=0, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="e")

        self.options_button = customtkinter.CTkLabel(self, text = "⋮")
        self.options_button.grid(column=3, row=0, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="e")

        MENU_OPTIONS = ["Delete Playlist", "Add to Queue", "Rename Playlist", "Overwrite Queue", ""]

        self.menu = tk.Menu(self, tearoff=0)
        for name in MENU_OPTIONS:
            self.menu.add_command(label=name)

        self.options_button.bind("<Button-1>", self.menu_trigger)

    # ChatGPT Slop - Change it
    def menu_trigger(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()