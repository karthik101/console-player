import os
import sys
import shutil

isPosix = os.name == 'posix'

#import e32 #TODO is e32 Win only?
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from MpGlobalDefines import *
from Song_Object import Song
from Song_LibraryFormat import *
from datatype_hex64 import *

from datatype_hex64 import *



from SystemPathMethods import *
from SystemDateTime import DateTime
import widgetProgressBar

if not isPosix:
    import win32api

from MpScripting import *


if isPosix:
    def GetShortPathName(path):
        return path
else:
    GetShortPathName = win32api.GetShortPathName;

class SyncSongs(QDialog):

    data = []
    thread = None
    dir =""
    initdir = "F:\\Music\\"
    
    show_warning_message = pyqtSignal("QString","QString","QString")
    
    def __init__(self,parent):

        super(SyncSongs, self).__init__(parent)
        
        self.setWindowIcon(QIcon('icon.png'))
        
        self.cbox = QComboBox(self)
        self.edit = QComboBox(self)
        self.sbtn = QPushButton("Sync",self)
        self.ebtn = QPushButton("Stop",self)
        
        self.edit.setEditable(True);
        
        self.pbar = widgetProgressBar.ProgressBar(self)

        self.hbox = QHBoxLayout()
        self.hbox.setSpacing(3)
        self.vbox = QVBoxLayout(self)
        
        self.txt_debug = QPlainTextEdit("",self)
        
        self.hbox.addWidget(self.cbox)
        self.hbox.addWidget(self.edit)
        self.hbox.addWidget(self.sbtn)
        self.hbox.addWidget(self.ebtn)
        
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.pbar)
        self.vbox.addWidget(self.txt_debug)
        
        # ##############################
        # Set Parameters
        
        
        #self.cbox.setFixedWidth(128)
        self.edit.setFixedWidth(256)
        #self.sbtn.setFixedWidth(128)
        #self.ebtn.setFixedWidth(128)
        
        self.cbox.setEditable(False)
        
        self.cbox.addItem("One")
        self.cbox.addItem("Two")
        self.cbox.addItem("Three")
        
        #self.pbar.setTextVisible(False)
        self.populateFolderList()
        # ##############################
        # Connect Signals
        
        self.sbtn.clicked.connect(self.sync)
        self.ebtn.clicked.connect(self.btn_stop)
        
        self.show_warning_message.connect(self.WarningMessage);
        self.message_result = -1;   # used when returning from the message
        
        QObject.connect(self, SIGNAL("UPDATE_SYNC_DIALOG"),updateSyncDialogEvent, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("DONE_SYNC_DIALOG"),updateSyncDialogDoneEvent, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("SYNC_SET_RANGE"),sync_setRange, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("SYNC_SET_VALUE"),sync_setValue, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("SYNC_SET_TEXT"),sync_setText, Qt.QueuedConnection)

    def Renew(self):
        while self.cbox.count() > 0:
            self.cbox.removeItem(0)
        # add items from MpGlobal.Window.editTabs[x] 
        #for x in range(len(MpGlobal.Window.editorTabs)):
        #    self.cbox.addItem(MpGlobal.Window.editorTabs[x][0])
        for i in range(MpGlobal.Window.tabMain.count()):
        
            widget = MpGlobal.Window.tabMain.widget( i )
            
            if isinstance(widget,Tab_PlaylistEditor):
                    self.cbox.addItem(widget.name)
                    
        self.setWindowTitle("Sync Songs to Folder")
        
        self.sbtn.setDisabled(False)
        self.ebtn.setDisabled(True)
        self.edit.setDisabled(False) 
        self.cbox.setDisabled(False)    
        #if len(MpGlobal.Window.editorTabs) == 0 :
        #    self.sbtn.setDisabled(True)
        #else:
        self.sbtn.setDisabled(False)
            
        self.pbar.setValue(0)
        
        # playlists open
        self.show()
        
    def sizeHint(self):
        return QSize(600, 32)
    def btn_stop(self):
        if self.thread != None :
            if self.thread.isRunning() :
                self.thread.alive = False
                self.sbtn.setDisabled(False)
                self.ebtn.setDisabled(True)
    def reject(self):
        # close the dialog window
        # wait for the thread to end early if needed
        if self.thread == None :
            self.data = None
            super(SyncSongs, self).reject()
        else:
            if self.thread.isRunning() :
                self.thread.alive = False
                # wait for the thread to finish
            else:
                self.thread = None # remove the thread from memory
                self.data = None
                MpGlobal.Window.syncDialogObj = None; # last reference to self
                super(SyncSongs, self).reject()
    
    def accept(self):
        MpGlobal.Window.syncDialogObj = None;
        super(SyncSongs,self).accept();
        
    def sync(self): 
        # ###########################
        # get data 
        
        dir = unicode(self.edit.currentText())
        dir = dir.replace("\\","/")
        # make sure the given directory terminates with a back slash
        if dir[-1] != "/":
            dir += "/"
        if not os.path.exists(dir):
            return; # return if it is an invalid path
            
        index = self.cbox.currentIndex()
        #obj = None # obj is the list of objects in editorTabs
        self.data = []
        pl_name = self.cbox.itemText(index)
        self.playlist_name = pl_name
        for i in range(MpGlobal.Window.tabMain.count()):
        
            widget = MpGlobal.Window.tabMain.widget( i )
            
            if isinstance(widget,Tab_PlaylistEditor):
                if widget.name == pl_name:
                    self.data = widget.playlist
                    
        #for x in MpGlobal.Window.editorTabs:
        #    if x[0] == self.cbox.itemText(index):
        #        obj = x
        #        break      
        #self.data = obj[3].DataSrc[:]
        
        if len(self.data) > 0 :
            self.sbtn.setDisabled(True)
            self.ebtn.setDisabled(False)
            self.edit.setDisabled(True) 
            self.cbox.setDisabled(True)
            if self.thread == None:
                
                self.dir = dir
                self.thread = SyncFiles(self,dir)
                self.thread.start()
            else:
                self.thread.alive = True
                self.thread.start()
            self.pbar.setRange(0,0)    
            self.setWindowTitle("Syncing...")      
    
    def populateFolderList(self):
        drives = systemDriveList()
        sub1 = ['%smusic\\' % d for d in drives if os.path.exists('%s/music/' % d)]
        #sub2 = ['%splayer\\' % d for d in drives if os.path.exists('%s/player/' % d)]
        
        R = drives+sub1#+sub2
        
        def rem(R,x):
            #for p in R:
            #    if p.lower().startswith(x.lower())
            #        R.
            if x in R:
                R.remove(x);
            if x.lower() in R:
                R.remove(x.lower());    
                
        rem(R,"C:\\")
        rem(R,"D:\\")
        rem(R,"D:\\Music\\")
        rem(R,"D:\\music\\")
        rem(R,"D:\\Player\\")
        rem(R,"D:\\player\\")
        
        R.sort()

        for item in R:
            self.edit.addItem(item)
            
        if "F:\\music\\" in R:
            self.edit.setCurrentIndex(R.index("F:\\music\\"))
        elif len(R) > 0:
            self.edit.setCurrentIndex(0)
     
    def WarningMessage(self,message,btn1="Ok",btn2="",icon=QMessageBox.Warning):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        #    "Delete Song Confirmation", message,
         #   QMessageBox.NoButton, self)
        msgBox.addButton(btn1, QMessageBox.AcceptRole)
        if btn2 !="":
            msgBox.addButton(btn2, QMessageBox.RejectRole)

        self.message_result =  msgBox.exec_() == QMessageBox.AcceptRole
        
        return self.message_result
    
    def debug(self,msg):
        pass
        # move the cursor to the end of the text buffer
        #self.txt_debug.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
        # insert the text
        #self.txt_debug.insertPlainText("%s\n"%msg)
        # move the cursor again to ensure new text is visible
        #self.txt_debug.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
            
def sync_setRange(obj,min,max):
    obj.pbar.setRange(min,max)
    
def sync_setValue(obj,value):
    obj.pbar.setValue(value)

def sync_setText(obj,str):
    obj.pbar.setText(str)

def updateSyncDialogEvent(obj,value):
            
    obj.pbar.setValue(value)
    obj.setWindowTitle("Syncing... %d/%d"%(value,len(obj.data)))
    
def updateSyncDialogDoneEvent(obj,bool): 
    obj.pbar.setValue(obj.pbar.maximum())# oops control
    print "fsync"
    if bool:
        obj.setWindowTitle("Syncing Done")
        obj.sbtn.setDisabled(True)
        obj.ebtn.setDisabled(True) 
        obj.pbar.setText("Finished")
        obj.pbar.setRange(0,100)
        obj.pbar.setValue(100)
        obj.pbar.update()
        btn = QPushButton("Quit");
        btn.clicked.connect(obj.accept)
        btn.setFocus()
        btn.setMaximumWidth(64);
        obj.vbox.addWidget(btn,alignment=Qt.AlignHCenter)
        print "finished sync"
    else:
        obj.setWindowTitle("Syncing Stopped")
           
class SyncFiles(QThread):
    index = 0
    dindex = 0
    alive = True
    dir = ""
    
    filelist = []
    listc = []
    listd = []
    listdir = []
    flag_search = True
    flag_gather = True
    flag_delete = True
    
    illegal_directory = False # if the target directory is illegal
    
    def __init__(self,parent,dir):
        super(SyncFiles, self).__init__()
        # use parent to reference objects in the dialog
        
        self.parent = parent # parent is the dialog controlling the sync
        self.dir = dir
        
        if len(self.parent.data) > 0:
            s=fileGetDrive(self.parent.data[0][MpMusic.PATH]) # source drive
            d=fileGetDrive(dir) # destination drive
            if s==d :
                self.illegal_directory = True
                
    def showWarningMessage(self,message,btn1="0k",btn2=""):
        """
            a message box cannot be started outside of the main thread
            i want to be able to show the user warnings during the sync process
            
            solution, this method emits a signal back to the sync dialog which message
            properties. then waits for a variable to be set
            
            that variable is set when the main thread is done showing the blocking message
        """
        
        self.parent.message_result = -1;
        self.parent.show_warning_message.emit(message,btn1,btn2)
        
        while self.parent.message_result == -1:
            QThread.msleep(20)
            
        print "message result = %d"% self.parent.message_result
        
        return self.parent.message_result
        
    def _get_FileList(self):
        self.filelist = []           # list of files on the drive
        
        # ###########################################################
        # Search Directory

        pathlist = [self.dir]   # list of folders pending search
        self.filelist = []
        # set the range to indicate we are calculating stuff
        
        self.parent.emit(SIGNAL("SYNC_SET_TEXT"),self.parent,"Searching Directory...")

        while len(pathlist) > 0:
            tempdir = pathlist.pop(0)
            R = os.listdir(tempdir)
            for fname in R:
                path = os.path.join(tempdir,fname)
                # append new folders to the pathlist
                # append files to the file list
                if os.path.isdir(path) == True:
                    pathlist.append(path)
                elif pathMatchExt(path) :
                    self.filelist.append(path)
            
        # if we finish succesfully set the search flag to false
        #if len(pathlist) == 0:
        #    self.flag_search = False
            
        print "Files: %d"%len(self.filelist) 
    
    def __get_FileList__(self):
        _filelist = "./sync_filelist.txt"
        self.filelist = []
        rf = open(_filelist,"r")
        line = True
        while line:
            line = rf.readline().strip()
            if line :
                self.filelist.append(line)
        rf.close()
        print "File: <%s>"%self.filelist[0]
    
    def _get_CD_lists(self):
        # set the range of the bar for this mode
        r = len(self.filelist) - 1
        if r < 0:
            r = 0
        self.parent.emit(SIGNAL("SYNC_SET_RANGE"),self.parent,0,r)

        self.listc = [] # list of tuples, format : (src path,dest path)
        self.listd = [] # list of paths from filelist to delete
        
        # ###########################################################
        # create the initial copy list, a list of src dst pairs for files
        self.listc = []
        for s in range(len(self.parent.data)):
            path = self.parent.data[s].shortPath()
            path = os.path.join(self.dir,path)
            self.parent.debug(path);
            self.listc.append( (self.parent.data[s][MpMusic.PATH],path) )
 
        # ###########################################################
        # using this list create two lists,
        # c list, files that will need to be transfered
        # d list, files that will need to be removed
        
        value = 0 # value to give to the progress bar
        self.parent.debug(len(self.listc));
        for file in self.filelist:
            flag_found = False
            value += 1
            self.parent.emit(SIGNAL("SYNC_SET_VALUE"),self.parent,value)
            
            # if the path on the device is found, remove it from the clist
            # this way the remaining items in the clist will be items to copy
            for x in range(len(self.listc)):
                # remove this song from the copy list, if it already exists
                if comparePath(file,self.listc[x][1]):
                    self.listc.pop(x)
                    flag_found = True
                    break
                    
            #if the item is not found in the clist, the user no longer wants it
            # add it to a pending list of files to delete.
            if not flag_found :
                self.listd.append(file)
            
            s = "Index: %d Del: %d Data: %d"
            p = (value,len(self.listd),len(self.listc))
            self.parent.emit(SIGNAL("SYNC_SET_TEXT"),self.parent,s%p)
            
        print "Del : %d"%len(self.listd)
        print "Copy: %d"%len(self.listc)    
    
    def _get_Dir_List(self):
        
        self.listdir = []   
        
        for item in self.listc:
            fpath = item[1];
            pdir = fileGetParentDir(fpath)
            
            if pdir not in self.listdir:
                if os.path.exists(pdir) == False :
                    self.listdir.append(pdir)
            
    def __savelists__(self):        
        _dellist  = MpGlobal.installPath+"sync_dellist.bat"
        _cpylist = MpGlobal.installPath+"sync_copylist.bat"
        
        _filelist = MpGlobal.installPath+"sync_filelist.txt"
        
        # sorting the lists makes it easier to manually compare them
        k = lambda record: record[1]
        self.listc.sort(key = k)
        self.listd.sort()
        
        #self.filelist.sort()
        #wf = open("./test_externalfilelist.txt","w")
        #for item in self.filelist:
        #    wf.write( "%s\n"%item )
        #wf.close()
        
        wf = open(_dellist,"w")
        wf.write( "@echo off\n" )
        for item in self.listd:
            wf.write( "DEL \"%s\"\n"%item )
        wf.close()
        
        wf = open(_cpylist,"w")
        wf.write( "@echo off\n" )
        for item in self.listdir:
            wf.write( "md \"%s\"\n"%item )
        for item in self.listc:
            
            s0 = "\"%s\""%win32api.GetShortPathName(item[0].replace('/','\\'))
            s1 = "\"%s\""%item[1]
            
            wf.write( "copy %-70s %s\n"%(s0,s1) )
            #wf.write( "%s\n"%(item[0]) )
            #wf.write( "%s\n"%(item[1]) )
        wf.close()
    
    def _del_files(self):
    
        r = len(self.listd) - 1
        if r < 0:
            return True
            
            
        message = "Delete %d Songs from:\n%s?"%(r,self.dir)    
        if not self.showWarningMessage(message,"Delete","Cancel"):
            return False
        
        self.parent.emit(SIGNAL("SYNC_SET_RANGE"),self.parent,0,r)
        # ###########################################################
        # Delete Songs from dir
        self.parent.emit(SIGNAL("SYNC_SET_TEXT"),self.parent,"Removing Files...")
        value = 0;
        #if self.alive:
            # delete songs in listd
            # this pop method is used to allow me to cancel the whole opperation mid way thru
            # then resume where we left off
        while len(self.listd) > 0:
            file = self.listd.pop(0)
            os.remove(file)
            #MpTest.fdelete(file)
            #print file
            value += 1
            self.parent.emit(SIGNAL("SYNC_SET_VALUE"),self.parent,value)
        
            #if len(self.listd) == 0:
            #    self.flag_delete = False
        self.parent.emit(SIGNAL("SYNC_SET_TEXT"),self.parent,"Removing - Done")  
        return;
                
    def _cpy_files(self):
        
        dt = DateTime();
        r = len(self.listc) - 1
        if r < 0:
            return True
        self.parent.emit(SIGNAL("SYNC_SET_RANGE"),self.parent,0,r)
        self.parent.emit(SIGNAL("SYNC_SET_VALUE"),self.parent,0)
        
        # ###########################################################
        # Copy Songs
        self.index = 0
        rTime = 0
        byteAvg = 0
        time_remaining=0
        stime = None
        dt.timer_start();
        while self.alive and self.index < len(self.listc):

            free = driveGetFreeSpace(self.dir)
            MBfree = free[2]
            if MBfree < 75:
                self.alive = False
                print " *** Out Of Free Space. Error."
                break;
            
            createDirStructure(self.listc[self.index][1])
            
            # ----------------------------------------------
            s = "Copying %d/%d - %s - %d MB free"
            p = (self.index,len(self.listc),DateTime.formatTimeDeltams(time_remaining),MBfree)
            self.parent.emit(SIGNAL("SYNC_SET_TEXT"),self.parent,s%p)
                        
            # ----------------------------------------------
            bytes=0
            try:
                src = self.listc[self.index][0]
                dst = self.listc[self.index][1]
                self.parent.debug("src:%s"%src);
                self.parent.debug("dst:%s"%dst);
                if os.path.exists(src) == False:    
                    self.parent.debug("Cannot Find Source File");
                elif os.path.exists(dst) == False:
                    #e32.file_copy(self.listc[self.index][0],self.listc[self.index][1])
                    bytes = os.path.getsize(self.listc[self.index][0])
                    
                    #MpTest.fcopy(src,dst)
                    PYCOPY (src, dst)
                    #copy(self.listc[self.index][0],self.listc[self.index][1])
            except:
                self.parent.debug( "*** ERROR: %s"%self.listc[self.index][1] )
                
            # get the end time right before the next update
            dt.timer_end();
            try:
                if bytes > 0:
                    delta = dt.usdelta
                    #print delta, float(delta)/bytes, bytes/delta
                    delta = float(delta)/float(bytes)
                    if rTime > 0: rTime = (rTime*9 + delta)/10
                    else:         rTime = delta
                    if byteAvg > 0: byteAvg = (byteAvg*9 + bytes)/10
                    else:           byteAvg = bytes
                    time_remaining = byteAvg*rTime #average microseconds per song
                    time_remaining *= (r-self.index) # times the total songs remaining
                    time_remaining /= 1000 # to milliseconds
            except:
                pass
            finally:
                dt.timer_start();
                
                
            self.parent.emit(SIGNAL("UPDATE_SYNC_DIALOG"),self.parent,self.index)
            # get the next start time immediatley after updating.
            
            
            self.index += 1  
            
        self.parent.emit(SIGNAL("SYNC_SET_TEXT"),self.parent,"Copying - Done")   
        return;
    
    def _build_library_(self):
        data = self.parent.data
        lib = []
        for song in data:
            path = song.shortPath()
            path = os.path.join(self.dir,path)
            copy = Song(song)
            copy[MpMusic.PATH] = path
            lib.append(copy)
             
        # if the drive we are syncing to contains a copy of the media
        # player, update its library file.
        player_path = os.path.join(self.dir[:2]+"\\","Player","user","");

        if (os.path.exists(player_path)):
            musicSave_LIBZ(os.path.join(player_path,"music.libz"),lib,typ=2)
        else:
            _path = os.path.join(self.dir,self.parent.playlist_name+".libz")
            musicSave_LIBZ(path,lib,typ=2)
    
    def run(self): 
        # ###########################################################
        # build self.filelist from file
        
        
        
        if not self.illegal_directory:
        
            self.showWarningMessage("Sync Start")
            
            self._get_FileList()
            
            self._get_CD_lists() #  generate list of songs to copy and delete
        
            self._get_Dir_List() # generate list of directories to make
            
            #self.__savelists__() # save text copies

            self._del_files() 
            
            self._cpy_files()
            
            self._build_library_() # save the playlist as a lbrary to ~/Player/user
            
            self.parent.emit(SIGNAL("SYNC_SET_TEXT"),self.parent,"Finished")  
        
            self.parent.emit(SIGNAL("DONE_SYNC_DIALOG"),self.parent,self.alive)
        
        else:
            self.showWarningMessage("Cannot Use Same Source and Destination Directories")
        
def PYCOPY(src,dst):
    b = 1<<17;
    with open(src,"rb") as rf:
        with open(dst,"wb") as wf:
            buffer = rf.read(b);
            while buffer:
                wf.write(buffer)
                buffer = rf.read(b);

    
from tab_playlist_editor import *        
     
if __name__ == '__main__':
    import sys
    
    #app = QApplication(sys.argv)
    #app.setApplicationName("Console Player")
    #app.setQuitOnLastWindowClosed(True)
    # create a window with no parent at 200 200 and data
    #window = SyncSongs(None)
    #window.data = [[]]*50
    #window.Renew()


    print "can not be run as __main__"
    #sys.exit(app.exec_())
    sys.exit(0)
        
        
        
        