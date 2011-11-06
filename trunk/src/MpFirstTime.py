# #########################################################
# #########################################################
# File: MpFirstTime
# Description:
#       This file controls what happens before anything
# is loaded by the Appication. A certain set of external
# files are required to style and provide icons. 
#   This files asks the user the first time the application
# is started where to extract files to, local or AppData
# each time after this program checks to see if all of these files
# still exist in that location.
#   A verify dialog is shown as a progressbar indication the
# progress as files are extracted.
# #########################################################
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

                    
from MpGlobalDefines import *
from ReadableDictionary_FileFormat import *
from Song_Object import Song
from datatype_hex64 import *
from widgetProgressBar import ProgressBar
from MpFileAccess import *
from SystemPathMethods import *
from MpScripting import *
from MpSocket import *                   
                    



isPosix = os.name == 'posix'
__devmode = "-devmode" in sys.argv;

PathLocal   = 1; # install to Local
PathAppData = 2; # install to AppData
checkState  = 0; 

_localname_ = "user"    # the folder name when this is a local installation
_appdataname_ = "ConsolePlayer" # the folder name when installed to the APPDATA folder

class FirstTimeDialog(QDialog): 

    def __init__(self,parent=None):

        super(FirstTimeDialog, self).__init__(parent)
        self.container = QVBoxLayout(self)
        self.setWindowTitle("Console Player Install")
        message = "Choose an installation Directory"
        label = QLabel(message)
        
        
        self.rad1 = QRadioButton("Current User - Recommended",self)
        #self.rad3 = QRadioButton("All Users",self)
        self.rad2 = QRadioButton("Current Directory",self)
        
        self.hbox = QHBoxLayout()
        self.btn1 = QPushButton("Confirm",self)
        self.btn2 = QPushButton("Cancel",self)
        
        
        self.container.addWidget(label)
        self.container.addWidget(self.rad1)
        self.container.addWidget(self.rad2)
        
        self.container.addLayout(self.hbox)
        self.hbox.addWidget(self.btn1)
        self.hbox.addWidget(self.btn2)
        
        self.rad1.setChecked(True)
        
        self.setFixedWidth(250)
        
        # conect buttons to duplicate the accept/rejext nature of a dialog
        self.btn1.clicked.connect(self.accept)
        self.btn2.clicked.connect(self.reject)
        self.btn1.setDefault(True)

    def accept(self):
        global checkState
        if self.rad1.isChecked():
            checkState = PathAppData;
        else:
            checkState = PathLocal;
        super(FirstTimeDialog, self).accept()
        
class VerifyInstallDialog(QDialog):

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

def startUpCheck(install=False):
    # check to make sure that the required files are installed
    # if not install them to the location the user gave.
    
    installPath = getInstallPath()
    
    if not os.path.exists(installPath) or install: # ask the user to (re)install
        print "Running First Time Installation"
        
        if "--install=home" in sys.argv:
            installPath = createInstallLocation();
        else:        
            installPath = getNewInstallLocation();
        
        if not os.path.exists(installPath):
            sys.exit(1) # quit because we were given a bad path
            
        MpGlobal.updatePaths(installPath) # update file locations to the new path 
        
        verifyInstallation(installPath) # extract files
        
    else: # settings file already exists read it.
        # perform a quick check that all needed files are there
        # TODO: evalutate, should i load settings here, renaming this functionto something better?
        print "Running Start up Checks"
        
        MpGlobal.updatePaths(installPath) # update file locations to the new path
        
        # ######################################
        # Check Session Lock
        # ######################################
        # we now have the install path, and this is the earliest we can check it.
        port = session_lock_exists();
        if port >= 0:
            if len(sys.argv) == 1:
                pass # do something?
            else:
                session_send_arguments(port);
                exit(0);
        else:
            # start the socket thread
            MpGlobal.SocketThread = LocalSocket_Thread();
            MpGlobal.SocketThread.start();
    
        
        init_Settings_default(Settings);
        ReadableDict_Load(MpGlobal.FILEPATH_SETTINGS,Settings)
        update_StrToDec_Dict();

        MpGlobal.SAVED_VERSION = Settings.VERSION # store the version str for later
        
        # compare the read settings value with the minimum required version
        value = versionCompare(MpGlobal.SAVED_VERSION,MpGlobal.MINIMUM_VERSION)
        
        #extract any missing files
        quickVerifyCheck(installPath,value >= 0) # quick verify when >= 0, otherwise do a  full replace

def getNewInstallLocation():
    """
        display a dialog and let the user
        select a directory
        Create that directory if it does not exist
    """
    # for a release version that has never been used before, prompt
    # the user for an install directory
    if not __devmode:
        check = FirstTimeDialog()
        code = check.exec_()
    else:
        code = QDialog.Accepted
    
    # ------------------------
    if code == QDialog.Accepted:
        if checkState == PathLocal or __devmode:
            path = os.getcwd()
            if os.path.exists(path):
                root = os.path.join(path,_localname_,"")
                if not os.path.exists(root):
                    os.mkdir(root)
                return root;
        elif checkState == PathAppData:

            # getenv('USERPROFILE') returns C:/Users/Nick/ or /home/nick/
            return createInstallLocation();
            if isPosix: # get a global directory to save to
                home = os.getenv("HOME")
            else:
                home = os.getenv("APPDATA")
        
            if home != None:
                root = os.path.join(home,_appdataname_,"")
                #create the directory if it 
                if not os.path.exists(root):
                    os.mkdir(root)
                return root
    return ""
def createInstallLocation():
    if isPosix: # get a global directory to save to
        home = os.getenv("HOME")
    else:
        home = os.getenv("APPDATA")

    if home != None:
        root = os.path.join(home,_appdataname_,"")
        #create the directory if it 
        if not os.path.exists(root):
            os.mkdir(root)
        return root
    return ""

def verifyInstallation(dir,quick=False):
    """
        extracts all files from MpUnpack to the directory 'dir'
        if quick is true only the missing files will be unpacked
    """
    import MpUnPack
    # set a stall count so that the progress bar updates more smoothly.
    itemCount = MpUnPack.count()
    stallCount=10
    maxSeconds=5  # how many seconds it should take YES THIS SLOWS IT DOWN
    stallTime=int(float(maxSeconds*1000.0)/float(stallCount*itemCount)) # quarter second per item
    stallTime=max(stallTime,15)
    rangeHi = MpUnPack.count()*stallCount

    #-----------------------------------------------------  
    # check for other folders:
    temp = os.path.join(dir,"playlist","")
    if not os.path.exists(temp):
        os.mkdir(temp)
    
    #-----------------------------------------------------  
    # create the widget
    progress = VerifyInstallDialog()
    progress.pbar.setRange(0,rangeHi)
    progress.show()
    
    #-----------------------------------------------------  
    # unpack the files to target directory
    _value = 0;
    for item in MpUnPack.UnPackFiles():
        obj = item(dir);
        filepath = os.path.join(dir,obj.fname)
        progress.label.setText(fileGetFileName(obj.fname))
        if quick and os.path.exists(filepath):
            _value += stallCount
            MpGlobal.Application.processEvents()
        else:
            obj.verify()
            if quick: print obj.fname
            # stall update the progress bar
            # smaller burts of sleep create a smoother update
            for i in range(stallCount):
                _value += 1
                progress.pbar.setValue(_value)
                MpGlobal.Application.processEvents()
                QThread.msleep(stallTime)
    #-----------------------------------------------------        
    progress.pbar.setValue(rangeHi) # incase of rounding error
    progress.label.setText("Done") 
    MpGlobal.Application.processEvents()
    
    for i in range(stallCount*10):
        MpGlobal.Application.processEvents()
        QThread.msleep(stallTime/2)
        
    progress.accept()

def quickVerifyCheck(dir,quick=True):
    """
        Check that all the files exist
        if any are missing run a quick verify
    """
    import MpUnPack
    R = MpUnPack.files()
    runVerify = False;
    
    for item in R:
        path = os.path.join(dir,item)
        if not os.path.exists(path):
            runVerify = True
            print path
            break;
            
    if runVerify or quick == False:
        verifyInstallation(dir,quick)
        #verifyRemoveUnwanted(dir)
    return;

    
def verifyRemoveUnwanted(dir):
    # NOT USED CURRENTLY
    # RETHINK THIS
    # you do not want to randmoly delete files on someones computer
    """
        if there are any files not wanted
        remove them
    """
    path1 = os.path.join(dir,"styles","default","")
    path2 = os.path.join(dir,"styles","No Theme","")
    folders = [path1,path2]
    
    files = MpUnPack.files()
    
    for folder in folders:
        R = os.listdir(folder)
        for item in R:
            path = folder+item
            if not os.path.isdir(path):
                path = path.replace("./","");
                path = path.replace("\\","/");
                if path not in files:
                    print "DEL:"+path
                    #os.remove(path)
                    
                    
                    

                    