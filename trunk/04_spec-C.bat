@echo off

:: file paths
set fname=ConsolePlayer

set path=C:\Dropbox\Scripting\PyQt\ConsolePlayer\src\
set path2=C:\pyinstaller-1.5-rc1\%fname%\%fname%.spec

set pyInstpath=C:\pyinstaller-1.5-rc1\
set make = "C:\pyinstaller-1.5-rc1\Makespec.py"
set build = "C:\pyinstaller-1.5-rc1\Build.py"

set projName=Console
set icon=%path%icon.ico

echo.
echo Generating Spec File
echo.

"C:\Python27\python.exe" "%pyInstpath%Makespec.py" -F -o %path% -n %projName% --icon=%icon% "%path%%fname%.py" 

echo.


pause
exit

