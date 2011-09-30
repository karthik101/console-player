
"""
    There are two places that need to be checked for updates:
    this code will be run after settings have been loaded, after library has been loaded
    and before the main window is shown.
    
    1. software version string.
        a certain minimum software version will be hard coded
        if the value in settings.ini is less than this, an update will be forced
        Updates are not allowed to delete files
        New external files will be dumped out
        and existing files will be overwritten.
        user confirmation before forcing an update
        if the user requests cancel force quit the application
    2. library version
        library contains a version for when loading
        each new version has a different meta data format
        if a new format is added and it requires getting that data from each song
        the updater will need to run getting that data
        for example if the version be loaded is less than 4 do a get on md5 for all songs
        this will take a very long time to update
"""
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from MpGlobalDefines import *
from widgetProgressBar import ProgressBar
from MpFileAccess import *
from MpScripting import *
from MpScriptingAdvanced import *

class LibraryUpdateDialog(QDialog):

    def __init__(self,parent=None):
        super(LibraryUpdateDialog, self).__init__(parent)
        self.setWindowTitle("Console Player Update")
        self.setFixedWidth(250)
        self.container = QVBoxLayout(self)
        self.label = QLabel("Updateing Library...")
        self.pbar = ProgressBar(self)
        self.pbar.setText("")
        self.container.addWidget(self.label)
        self.container.addWidget(self.pbar)
           
def checkForUpdates(cversion):
    """
        cversion as a value read from settings file
    """
    
    # set a list of constant versions
    
    if MpGlobal.SAVED_VERSION == "0.0.0.0" :
        return;
    
    v1 = "0.4.2.0" # update songs in library to contain index values.
    
    # if any version compares are less than 0 then updates are required.
    update = versionCompare(cversion,v1) < 0;
    
    
    
    if update:
        print "updates are required"
        runUpdater(cversion);
    
def runUpdater(cindex):
    """
        cindex as index for which version updates to run
        e.g. if the index is 1, run all updates that i have defined
        to be greater than or equal to 1.
        
        the first index is 0
    """
    #-----------------------------------------------------  
    # create the widget
    progress = LibraryUpdateDialog()
    
   
    # init values
    stallTime=1 #TODO: remove this when updater is live
    rangeHi = len(MpGlobal.Player.library)
    value   = 0
    
    progress.pbar.setRange(0,rangeHi)
    progress.show()
    #-----------------------------------------------------  
    # run updater
    for song in MpGlobal.Player.library:
        songUpdate(song,0)
        value += 1;
        progress.pbar.setValue(value)
        MpGlobal.Application.processEvents()
        #QThread.msleep(stallTime)
        
    #-----------------------------------------------------  
    # clean up, display done, wait a second then close 
    progress.pbar.setValue(rangeHi)
    progress.label.setText("Done") 
    MpGlobal.Application.processEvents()
    for i in range(25):
        MpGlobal.Application.processEvents()
        QThread.msleep(20)
        
    progress.accept()

def songUpdate(song,cindex):
    """
        what needs to be done on a per song basis for the given version
        cindex as an integer level of updates to run, so version compare
        does not have to be calculated for each song
        
        cindex as index for which version updates to run
        e.g. if the index is 1, run all updates that i have defined
        to be greater than or equal to 1.
        
        the first index is 0
    """
    if cindex == 0:
        song[MpMusic.SONGINDEX] = songGetAlbumIndex(song);
    return 0;
    
