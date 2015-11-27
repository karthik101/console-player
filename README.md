# console-player
Automatically exported from code.google.com/p/console-player

Written in Python, using PyQt and VLC for audio playback, Console Player provides a unique way of managing you music library. Search through your library instantaneously and quickly create new playlists.

To get started simply drag and drop any music file or folder onto the application. To create a new playlist type 'new' into the console box.

Console Player now uses BASS for audio playback. BASS allows for real time DSP blocks to be added before output. support for VLC will remain for some time.
Features
Quickly Build Playlists

A tab labeled 'Quick Select' allows you to quickly build a playlist by selecting songs by artist or genre. This tab also provides interesting information, including listening statistics and number of songs under each artist or genre.
Manage Your Library

An 'Explorer' tab lets you interact with the actual files of your library. It lets you easily reorganize or rename files and folders on your files system, while maintaining them in your library. Never have the issue of the media player forgetting where you put a song again.
Current Road map

    Testing for the linux version, and inclusion of support for Media Keys on linux version. 

Introduction

Console Player is programmed with Python 2.7 (32 bit) and PyQt version 4.8.5. VLC is not required for playback, when not installed The application will fall back to a default media player installed on you system.
Required Files

    Python 2.7 32bit
    PyQt
    Mutagen - Audio Tagging library
    -P-y-L-Z-M-A- no longer used 

Windows

    http://sourceforge.net/apps/mediawiki/pyhook 

Linux

    sudo apt-get install python-qt4
    sudo apt-get install python-mutagen
    sudo apt-get install vlc 

Additional

    VLC - Using the latest version will prevent playback issues 
