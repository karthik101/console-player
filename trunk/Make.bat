@echo off
cd %~dp0src
::print os.environ['PYTHONPATH']
set PYTHONPATH=%PYTHONPATH%;C:DropboxScriptingPyModuleGlobalModulessrc
python ./ConsolePlayer.py -Wonce -debug -devmode
::python ./ConsolePlayer.py --install=home
if errorlevel 1 goto error
pause
exit
:error
echo   *** Errors Found During Compiliation
pause
