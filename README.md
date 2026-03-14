# Study Music Player

A Python music player with some study features such as a to do list and a timer. As well as the ability to download songs from Youtube! 

---

## Features

- To do list to track your tasks.
- Timer up to 24 hours.
- Inifnite Queue system.
- Downloading songs from YouTube.

## Usage Tutorial
Download and extract the zip.  
Open the extracted zip and run main.exe  
OR  
Download from the source as explained later on.

THEN

EITHER:  
Go to Music Finder
Paste in the URL of a Youtube Video  
Click Download Video  
Once downloaded, go to tracks and click on a song for it to start playing.

OR:  
Move any songs you wish to listen to, into the Songs folder.  
Inside the program, go to Tracks.  
Hit refresh.  

## Dependencies
FFmpeg (Pretty much required) [https://www.ffmpeg.org/download.html]  
Deno (Pretty much required for using downloader) [https://deno.com/]

## Build & Run
NOTE: CURRENT COMPILED RELEASE IS OUTDATED. USE BUILD FROM SOURCE FOR THE UPDATED VERSION.
This program has only been compiled for Windows 11.
#### Windows
Download the main.zip in the latest release.  
Extract folder.  
Run main.exe

#### Running from Source Code
When building from the source code the Music Finder will fail to embed any metadata to the song as it relies on some dependancies to do so.
Build from source commnds

    pip install git+https://github.com/Stu67nt/StudyMusicPlayer
    studymusicplayer

## AI Usage
Used for assistance with debugging, assisting with some GUI stuff and in line code suggestions as well as helping with compiling the project. 
