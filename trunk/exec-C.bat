
:: this file will create a console application, the command prompt will be opened when
:: the program is executed.
:: use this if the exe fails to launch, or unexpectedly crashes

:: how to use
:: create the exe, and move it to the location where you normally run the application
:: open the command prompt
:: cd to the location of the exe
:: type 'console.exe' to launch this executable

:: wait for the crash, or do what is needed to cause the crash, and debug info will be printed 
:: 	to the screen


@echo off

"C:\Python27\python.exe" "C:\Python27\Lib\site-packages\pyInstaller\Build.py" "D:\Dropbox\Scripting\PyQt\ConsolePlayer\src\Console.spec"
