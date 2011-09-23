@echo off

setLocal EnableDelayedExpansion

::str_VERSION:0.3.2.128

for /f "tokens=* delims= " %%a in (C:/Dropbox/Scripting/PyQt/ConsolePlayer/src/usr/settings.ini) do (
set /a N+=1
set item!N!=%%a
set versionid=%%a

)
::version is the last item
echo %versionid:~10%
pause