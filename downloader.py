import yt_dlp
import yt_dlp_ejs
import logging
import os

def progressHook(d):
    """
    Used to track what percent of the downloads are complete.
    TODO:
    Change progress and progress labal as they no longer exist
    """
    if d['status'] == 'finished':
        pass
    elif d['status'] == 'downloading':
        print(d["_percent_str"])

def download(urls: list, config: dict):
    with yt_dlp.YoutubeDL(config) as ydl:
        ydl.download(urls)

dir = str(os.path.abspath(os.getcwd())) + "\\Songs\\"

config = {
    "verbose": True,
    'format': 'm4a/mp3/wav/bestaudio',  # If needed you can create an easy bug here
    'outtmpl': {'default': f'{dir}%(title)s.%(ext)s'},
    "restrictfilenames": True,
    "windowsfilenames": True,
    'writethumbnail': True,
    'logger': logging.getLogger(__name__),
    'postprocessors': [
       {'already_have_thumbnail': False,
        'key': 'EmbedThumbnail'},
    ],
    "warn_when_outdated": True,
    'ignoreerrors': False,
    'js_runtimes': {'deno': {'path': r"C:\Users\Tanzil Chowdhury\.deno\bin\deno.exe"}},
    'ffmpeg_location': 'utils',  # Alternatively, you can also create an easy bug here.
    'progress_hooks': [progressHook],
}

download(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"], config)
