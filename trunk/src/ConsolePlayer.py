#----------------------------------------------------------
#----------------------------------------------------------
#  ConsolePlayer.py
#----------------------------------------------------------
 
# TODO:
# imports should be fixed accross all files
#   in general, i would  like all python standard lib imports first
#   then all Qt / other imports ( including all imports in ./module/ last in the list )
#   then all imports specific to this project should be found at the end of the file.
#       that is, imports of modules found in ./src/
#
# better abstraction on the application <--> data level
#   in general, i want the following:
#       [data] <-> [translator] <-> [application interface]
#   what would this get me?:
#       1. all dialogs would be standalone, 
#       2. widgets would be independant of the data they represent.
#           the library table could instead show any list of songs and be easily switched tyo new data sets.
#
# better tables.
#   the current tables i wrote the day after i wrote "hello world" in python. i didn't know 
#   what it was i was doing. I think the idea is sound, 30 rows (or so), and revolve the data
#   through them. instead of adding/removing 1k-10k rows. do i write my own table <-> interface?
#
# I now have an event Manager. I need a way to
#
# A way to load any text file as a playlist. Look for file paths, check that they are songs
#   then ask the user to add the songs either A) to the library or B) play all
#       play all automatically when no new songs would need to be added.
# Also XML support, get paths in the same way, but if it's in an itunes format grab the data using that format.
#
import os   
import sys
import sip

if __name__ != "__main__":
    print "Console Player must be started as the main script"
    sys.exit(1)
 
isPosix = os.name =='posix'
 
__debug   = "-debug" in sys.argv;
__devmode = "-devmode" in sys.argv;
__install = "-install" in sys.argv;  # launch with the -install flag to reinstall the application
__install_home = "--install=home" in sys.argv; # force install to home directort.


if __devmode: # use API 2, when testing
              # API2 is set by PyInstaller aftercompiled to an exe
    # For Python 2.7, PyInstaller
    # error: http://www.pyinstaller.org/ticket/159
    # if you see an error related to API already set to Version 1 edit the file:
    #   %PyInstaller%/support/rthooks/pyi_rth_qt4plugins.py
    # and add this API changing code at the top of it:
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)
       
# #############################################################################################################
# #############################################################################################################
# #############################################################################################################
  
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *

from MpApplication import *
from MpScripting import *
from MpPlayerThread import MediaPlayerThread
from MpStartUp import startUpCheck



# ######################################
# Create the Qt Application
# ###################################### 
MpGlobal.Application = QApplication(sys.argv)
MpGlobal.Application.setApplicationName("Console Player")
MpGlobal.Application.setQuitOnLastWindowClosed(True)  

if __debug: print "Application Created %s"%MpGlobal.Application    

# ######################################
# Set the Internal Version
# ###################################### 
import VersionController
MpGlobal.VERSION = VersionController.AutoVersion(__devmode) 
MpGlobal.NAME = "Console Player - v%s"%MpGlobal.VERSION

print MpGlobal.NAME
  
# ######################################
# Look for the settings file,
# ask the user for an install location
# load the settings if found 
# extract any files required
# ###################################### 
startUpCheck(install=__install); 

if __debug: print "Set Up Check Done\n"  

# #############################################################################################################
# #############################################################################################################
# #############################################################################################################
   
   
# ######################################
# Create the Main Window
# ######################################
if __debug: print "Creating Main Window..."  
  
init_preMainWindow()        #code to run before MainWindow.__init__()
MpGlobal.Window = MainWindow(MpGlobal.NAME)
MpGlobal.Window.show()
init_postMainWindow()       #code to run after  MainWindow.__init__(), AND after show()

if __debug: print "Main Loop Starting..."    
  
# ######################################
# Start the Main Loop
# ######################################
sys.exit(MpGlobal.Application.exec_())




    