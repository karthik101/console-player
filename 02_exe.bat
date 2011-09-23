@echo off

cd %~dp0

"C:\Python27\python.exe" "C:\Python27\Lib\site-packages\pyInstaller\Build.py" "./src/ConsolePlayer.spec"

pause