import yt_dlp
import logging
import os
import time
import sqlite3
import tinytag as tt
import shutil
import tkinter as tk
import json

def createConsoleLog():
    """
    Creates a file for storing logs of console.
    :returns: file path of the created txt file
    """
    print("Creating Console Log")
    timestr = time.strftime("%Y.%m.%d-%H%M%S")
    filePath = os.path.join("Console Logs/", timestr + ".txt")
    print("Created Console Log")
    return str(filePath)

def progressHook(d):
    """
    Used to track what percent of the downloads are complete.
    """
    if d['status'] == 'finished':
        pass
    elif d['status'] == 'downloading':
        print(d["_percent_str"])

def init_database():
    """
    Initialises music_ops.db and songs table or creates them if they don't exist.
    :return: SQLite3 db object
    """
    db = sqlite3.connect("Databases/music_ops.db")
    cursor = db.cursor()
    query = ("CREATE TABLE IF NOT EXISTS "  # Needed as otherwise if the table is lost the program will not boot
             "songs(" 
             "songID INTEGER PRIMARY KEY AUTOINCREMENT,"  # AUTOINCREMENT ensures a unique id
             "file_path TEXT,"
             "song_name TEXT,"
             "song_duration INTEGER,"
             "artist TEXT,"
             "publish_date TEXT"
             ")")
    cursor.execute(query)
    db.commit()  # Committing the query
    return db

def add_song(db, song_file_name):
    file_path = str(os.path.abspath(os.getcwd())) + "\\Temp Downloads\\" + song_file_name
    song = tt.TinyTag.get(file_path)  # Extracting the metadata
    # Gives title of song if held in metadata otherise we use file name
    song_name = song.title if song.title != None else song_file_name
    song_duration = int(round(song.duration))  # Gives length of songs as seconds
    artist = song.artist if song.artist != None else "Unknown"  # Gives artist name
    publish_date = song.year if song.artist != None else "Unknown"  # song.year givees the exact date

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO "
        "songs("
        "file_path,"
        "song_name,"
        "song_duration,"
        "artist,"
        "publish_date"
        ") "
        "VALUES (?, ?, ?, ?, ?)",
        (file_path, song_name, song_duration, artist, publish_date))
    db.commit()

def move_file(file_name:str, current_dir:str, target_dir:str):
    """Moves files using shutil.move"""
    if file_name not in os.listdir(path=target_dir):
        shutil.move(current_dir, target_dir)
    else:
        tk.messagebox.showwarning("Clashing file found in Songs. Keeping in Temp Downloads folder.")
        return -1
    return 0

def download(url: list, config: dict):
    """
    Downloads all urls in given list and adds them to songs.db
    :param url:
    :param config:
    :return:
    """
    file_path = createConsoleLog()
    logging.basicConfig(level=logging.NOTSET, filename=file_path)
    with yt_dlp.YoutubeDL(config) as ydl:
        ydl.download(url)
        db = init_database()
        for file in os.listdir("Temp Downloads"):
            # Try except for catching valid files
            try:
                tt.TinyTag.get(fr"Temp Downloads\{file}")
                print(f"{file} is an valid file")
                add_song(db, file)
                move_file(file, fr"Temp Downloads\{file}", str(os.path.abspath(os.getcwd()))+"\\Songs")
            except Exception as err:
                print(f"{file} is not an audio file")  # Means file is not an audio file
                print(err)

def create_download_config():
    dir = str(os.path.abspath(os.getcwd())) + r"\\Temp Downloads\\"
    f = open("Databases\\config.json")
    settings = json.load(f)
    f.close()
    download_config = {
        # Used for detailed error logs
        "verbose": True,
        # Configures the file format of the video downloaded
        'format': settings['format'],  # If needed you can create an easy bug here
        # Configures the file name of the output
        'outtmpl': {'default': f'{dir}%(title)s.%(ext)s'},  # Allow user configure
        # Used so invalid file name not created.
        "restrictfilenames": True,
        "windowsfilenames": True,
        # Used for thumbnails
        'writethumbnail': settings['write_thumbnail'],
        # Used for creating error logs
        'logger': logging.getLogger(__name__),
        # Does embedding stuff
        'postprocessors': [
           # Embeds Thumbnail
           {'already_have_thumbnail': False,
            'key': 'EmbedThumbnail'},
           # Embeds Metadata
           {'add_chapters': True,
            'add_infojson': 'if_exists',
            'add_metadata': True,
            'key': 'FFmpegMetadata'},
        ],
        # Module needs to be frequently updated to ensure function
        "warn_when_outdated": True,
        # Any errors will always be logged
        'ignoreerrors': False,
        # Needed by yt-dlp for full Youtube Support
        'js_runtimes': {'deno': {'path': settings['deno_path']}}, # User needs to set
        # Dependancy location Required for any embedding
        'ffmpeg_location': settings['ffmpeg_path'],  # Alternatively, you can also create an easy bug here.
        # Used for tracking download progress
        'progress_hooks': [progressHook],
    }
    return download_config

if __name__ == "__main__":
    download_config = create_download_config()
    download("https://www.youtube.com/playlist?list=PLETosy7ETA_uKsH9Zi8WazVPMtHuri4gQ", download_config)
    print(str(os.path.abspath(os.getcwd()))+"\\Songs")

"""
TEST CASE:
Only adding to db and moving to songs valid files out of (mp4, m4a, part, webp, txt) valid ones are (mp4, m4a) 
"""