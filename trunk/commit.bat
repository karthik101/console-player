@echo off

%~d0

cd %~dp0

echo Recent Changes:

svn st

set /P input=Enter a commit message:

svn commit -m %input%
if errorlevel 1 goto error
exit
:error
pause