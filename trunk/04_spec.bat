@echo off

:: file paths
set fname=ConsolePlayer

set path=C:\Dropbox\Scripting\PyQt\ConsolePlayer\src\
set path2=C:\pyinstaller-1.5-rc1\%fname%\%fname%.spec

set pyInstpath=C:\pyinstaller-1.5-rc1\
set make = "C:\pyinstaller-1.5-rc1\Makespec.py"
set build = "C:\pyinstaller-1.5-rc1\Build.py"

set projName=ConsolePlayer
set icon=%path%icon.ico

echo.
echo Generating Spec File
echo.

::"C:\Python27\python.exe" "%pyInstpath%Makespec.py" -o %path% -n %projName% --icon=%icon% "%path%%fname%.py" 
::"C:\Python27\python.exe" "%pyInstpath%Makespec.py" -F -o %path% -n %projName% --icon=%icon% "%path%%fname%.py" 

::"C:\Python27\python.exe" "%pyInstpath%Makespec.py" -F -o %path% -n %projName% --icon=%icon% -w "%path%%fname%.py" 
echo Custom Spec now in use, do not overwrite ConsolePlayer.spec
echo.

::C:\Dropbox\Scripting\PyQt\ConsolePlayer\src\ConsolePlayer.spec
::echo "C:\Python27\python.exe" "%pyInstpath%Build.py" "%path%%projName%.spec"
::"C:\Python27\python.exe" "C:\pyinstaller-1.5-rc1\Build.py" "C:\Dropbox\Scripting\PyQt\ConsolePlayer\src\ConsolePlayer.spec"

::02_exe.bat

pause
exit

