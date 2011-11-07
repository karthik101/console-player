#----------------------------------------------------------
#----------------------------------------------------------
#  ConsolePlayer.py
#----------------------------------------------------------
 
# TODO:
# imports should be fixed accross all files
#   in general, i would  like all standard lib imports first
#   then all Qt / non other imports ( including all imports in ./module/ )
#   then all imports specific to this project should be found at the end of the file.
#
# better abstraction on the application <--> data level
#   in general, i want the following:
#       [data] <-> [translator] <-> [application interface]
#   what would this get me?:
#       1. all dialogs would be standalone, 
#       2. widgets would be independant of the data they represent.
#           the library table could instead show any list of songs and be easily switched.
#
# better tables.
#   the current tables i wrote the day after i wrote "hello world" in python. i didn't know 
#   what it was i was doing. I think the idea is sound, 30 rows (or so), and revolve the data
#   through them. instead of adding/removing 1k-10k rows. do i write my own table <-> interface?
   
import os   
import sys

if __name__ != "__main__":
    print "Console Player must be started as the main script"
    sys.exit(1)

# use os.getpid()
# check  ~/session.lock for pid.
# close out if pid in ~/session.lcok still exists 
# otherwise overwrite it and continue launching this program.
# if sys.args could be considered 'empty' ( no file in it's path ) then ask if it's ok to open a new copy.
# if there is data in sys.args. send it over to the pid in ~/session.lock
 
isPosix = os.name =='posix'

# add the path to the global modules to the import path list
#path = os.getcwd().replace('\\','/');
#path = path[:path.rfind('/')+1]+'module'
#sys.path.append(path)
 
__debug   = "-debug" in sys.argv;
__devmode = "-devmode" in sys.argv;
__install = "-install" in sys.argv;  # launch with the -install flag to reinstall the application
__install_home = "--install=home" in sys.argv; # force install to home directort.
import sip

if __devmode: # use API 2, when testing
              # API2 is set by PyInstaller aftercompiled to an exe
    # For Python 2.7, PyInstaller
    # error: http://www.pyinstaller.org/ticket/159
    # if you see an error related to API already set to Version 1 edit the file:
    #   %PyInstaller%/support/rthooks/pyi_rth_qt4plugins.py
    # and add the API changing code at the top of it:
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)
        
# there are numerouse if __debug statements spread throughout this file 
# these are used for determining where a crash occured during boot
# compile a Console version (exec-c.bat) to see these messages

if __debug: print "Sip Version Set"        
#----------------------------------------------------------
#----------------------------------------------------------
        
from PyQt4.QtCore import *
from PyQt4.QtGui import *

if __debug: print "Qt Imports"    
#Modules needed to start the player
from MpGlobalDefines import *
from Song_Object import Song
from datatype_hex64 import *
if __debug: print "MpGlobalDefines Imported"    
from MpApplication import *
if __debug: print "MpApplication Imported"    
from MpScripting import *
from MpThreading import MediaPlayerThread
from MpFirstTime import startUpCheck
import MpEventHook
if __debug: print "Remaining Required Files Imported"    


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

if __debug: print MpGlobal.NAME
    

if __debug: print "Player Version Set"      
  
# ######################################
# Look for the settings, Check if required files need to be extracted
# ###################################### 
startUpCheck(install=__install); # TODO CLEAN UP WHAT THIS DOES

if __debug: print "Set Up Check Done"    

# ######################################
# initialize other settings
# ######################################
init_Settings(not __devmode)

if __debug: print "Settings Initialized"
      

import MpAutoUpdate; 
MpAutoUpdate.checkForUpdates(MpGlobal.SAVED_VERSION);

if __debug: print "Check for updates complete"

# #############################################################################################################
# #############################################################################################################
# #############################################################################################################
   
# ######################################
# Create the Main Window
# ######################################
if __debug: print "Creating Main Window..."  
  
init_preMainWindow()
MpGlobal.Window = MainWindow(MpGlobal.NAME)
MpGlobal.Window.show()
init_postMainWindow()

if __debug: print "Main Loop Starting..."    
  
# ######################################
# Start the Main Loop
# ######################################
sys.exit(MpGlobal.Application.exec_())




    