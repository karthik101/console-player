#!/usr/bin/sh

cd /home/
cd nick/windows/D_DRIVE/Dropbox/Scripting/PyQt/console-player
cd src


export PYTHONPATH="/home/nick/windows/D_DRIVE/Dropbox/Scripting/PyModule/GlobalModules/src"

python /home/nick/PyPackage/pyinstaller-1.5.1/Build.py ConsolePlayer.spec
