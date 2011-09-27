
:: this file will create a standalone exe file in the --onefile configuration

@echo off
:: change to current drive
%~d0
:: change to current directory
cd %~dp0
:: build using pyInstaller
"C:\Python27\python.exe" "C:\Python27\Lib\site-packages\pyInstaller\Build.py" "./src/ConsolePlayer.spec"
:: you can remove the pause
pause

:: new executabl will be saved to ./bin