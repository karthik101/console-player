
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

class LibraryUpdateDialog(QDialog):

    def __init__(self,parent=None):
        super(VerifyInstallDialog, self).__init__(parent)
        self.setWindowTitle("Console Player Install")
        self.setFixedWidth(250)
        self.container = QVBoxLayout(self)
        self.label = QLabel("Installing...")
        self.pbar = ProgressBar(self)
        self.pbar.setText("")
        self.container.addWidget(self.label)
        self.container.addWidget(self.pbar)
        
def checkForUpdates():
    print "checking for updates"
    
    
def runUpdater():
    #-----------------------------------------------------  
    # create the widget
    progress = VerifyInstallDialog()
    
   
    # init values
    stallTime=5
    rangeHi = len(MpGlobal.Player.library)
    value   = 0
    
    progress.pbar.setRange(0,rangeHi)
    progress.show()
    #-----------------------------------------------------  
    # run updater
    for song in MpGlobal.Player.library:
        songUpdate(song)
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

def songUpdate(song):

    
    return 0;
    
