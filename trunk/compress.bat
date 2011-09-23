
@echo off


set H=%TIME:~0,2%
::format hours to zero-pad the first index
if "%H:~0,1%"==" " set H=0%H:~1%
set M=%TIME:~3,2%
set S=%TIME:~6,2%
set DATETIME=%DATE%-%H%-%M%


setLocal EnableDelayedExpansion
::str_VERSION:0.3.2.128
for /f "tokens=* delims= " %%a in (D:/Dropbox/Scripting/PyQt/ConsolePlayer/src/user/settings.ini) do (set versionstr=%%a)
::version is the last item
set version=%versionstr:~12%



set ARCHIVEPATH=D:/Nick/SourceBackUp/ConsolePlayer/
set ARCHIVE=[%DATETIME%-%version%]_ConsolePlayer.7z
echo %ARCHIVE%
set ARCHIVE="%ARCHIVEPATH%%ARCHIVE%"

:: add all py pyw, txt files, and all files in the user folder
:: no need to get pyc, dll etc
set file="./src/*.py"
set file=%file% "./src/*.pyw"
set file=%file% "./src/CHANGELOG.txt"
set file=%file% "./src/COMMANDS.txt"
set file=%file% "./src/INTERFACE.txt"
set file=%file% "./src/ConsolePlayer.spec"
set file=%file% "./src/README"
set file=%file% "./src/icon.ico"
set file=%file% "./src/user/icon.png"
set file=%file% "D:\Dropbox\Scripting\PyModule\GlobalModules\src\*.py"
set file=%file% "D:\Dropbox\ConsolePlayer\user\music.library"
::set file=%file% "./src/user"



"C:\Program Files\7-Zip\7z.exe" a %ARCHIVE% %file%

echo %file%
