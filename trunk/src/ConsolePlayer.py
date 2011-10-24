#----------------------------------------------------------
#----------------------------------------------------------
#  ConsolePlayer.py
#----------------------------------------------------------
   
   
# todo
#
#   themes
#       the %IMAGE% tag should get thefile name supplied.
#       it should then test for the existance of that file in the themes location
#       failing that, it should test for location in ./images/
#       failing that, it should be given blank.png instead
#
#
#   
   
import sys
import os   

if __name__ != "__main__":
    print "Console Player must be started as the main script"
    sys.exit(1)
 
isPosix = os.name =='posix'

# add the path to the global modules to the import path list
#path = os.getcwd().replace('\\','/');
#path = path[:path.rfind('/')+1]+'module'
#sys.path.append(path)
 
__debug   = "-debug" in sys.argv;
__devmode = "-devmode" in sys.argv;
__install = "-install" in sys.argv;  # launch with the -install flag to reinstall the application
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
del VersionController
print MpGlobal.NAME
    

if __debug: print "Player Version Set"      
  
# ######################################
# Look for the settings, Check if required files need to be extracted
# ###################################### 
startUpCheck(install=__install); # load the settings or install if never been run before

if __debug: print "Set Up Check Done"    

# ######################################
# initialize other settings
# ######################################
init_Settings(not __devmode)

if __debug: print "Settings Initialized"
    
init_preMainWindow()

if __debug: print "Player Components initialized"    

import MpAutoUpdate; 
MpAutoUpdate.checkForUpdates(MpGlobal.SAVED_VERSION);
del MpAutoUpdate

if __debug: print "Check for updates complete"   
# ######################################
# Create the Form
# ######################################
MpGlobal.Window = MainWindow(MpGlobal.NAME)

if __debug: print "Main Window Created %s"%MpGlobal.Window    
# ######################################
# Create the Player
# ######################################
MpGlobal.PlayerThread = MediaPlayerThread(MpGlobal.Window)
MpGlobal.PlayerThread.start()

if __debug: print "Player Thread Created %s"%MpGlobal.PlayerThread  
  
# ######################################
# Set Keyboard Hook
# ######################################

if not __devmode and Settings.MEDIAKEYS_ENABLE:
    MpEventHook.initHook()
    debugPreboot("KeyBoard Hook Enabled")

# ######################################
# Finish initializing....
# ######################################
MpGlobal.Window.txt_debug.setPlainText(MpGlobal.debug_preboot_string)
MpGlobal.debug_preboot_string = ""

MpGlobal.Window.show()

if __debug: print "Window Show"    

init_postMainWindow()

if __debug: print "Post Main Window initilizers done"    

# ######################################
# Start the Main Loop
# ######################################
sys.exit(MpGlobal.Application.exec_())




    