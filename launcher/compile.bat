@echo off
%~d0

cd %~dp0
set flag=-mwindows

g++ %flag% -I./ ./*.cpp -lwsock32 icon.o -o ConsoleLauncher.exe

ConsoleLauncher a b c d e f