@echo off
%~d0

cd %~dp0
set flag=-mwindows

:: -mwindows

g++  -I./ ./*.cpp -lwsock32 icon.o -o ConsoleLauncher.exe

::D:\Dropbox\Scripting\PyQt\console-player\launcher\ConsoleLauncher.exe

pause

