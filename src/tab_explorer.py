
import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

isPosix = os.name == 'posix'

from widgetLineEdit import LineEdit
from widgetLargeTable import *
from Song_Table import *
from Song_Search import *
from Song_FileManager import *
from Song_MutagenWrapper import *
from SystemPathMethods import * 

from App_EventManager import *

from tab_base import *

class Item_Base(list):
    """
        A LargeTable expects a 2D list of data
        
        in the explorer window each item will be
    """
    index_icon = 0
    index_name = 1
    index_song = 2
    def __init__(self,name,icon,path,song=None):
    
        super(Item_Base,self).__init__([icon,name,song]) 
        
        self.path = path
        self.type = ""

    def __getattr__(self,attr):
        if attr == "name":
            return self[self.index_name]
        elif attr == "icon":
            return self[self.index_icon]
        elif attr == "song":
            return self[self.index_song]
        else:
            raise AttributeError("%r object has no attribute %r" % (type(self).__name__, attr))

    def __unicode__(self):
        return unicode(self.name)
    
class Item_File(Item_Base):

    def __init__(self,name,path,song=None):
    
        icon = MpGlobal.icon_None
        super(Item_File,self).__init__(name,icon,path,song) 
        
    def __unicode__(self):
        return u"2.file: %s"%self.name

class Item_Folder(Item_Base):

    def __init__(self,name,path):
    
        icon = MpGlobal.icon_Folder
        super(Item_Folder,self).__init__(name,icon,path) 
        
    def __unicode__(self):
        return u"1.folder: %s"%self.name

class Tab_Explorer(Application_Tab):

    def __init__(self,parent=None):
        super(Tab_Explorer, self).__init__(parent)
        self.parent = parent
        
        self.event_manager = EventManager()
        self.file_manager = Song_File_Manager()
        
        self.vbox = QVBoxLayout(self)  
        self.hbox = QHBoxLayout()  
        
        self.edit = QComboBox(self)
        
        self.btn_back = QPushButton("Back")
        self.btn_open = QPushButton("Open")
        
        self.btn_back.setFixedWidth(30)#setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.btn_open.setFixedWidth(30)#setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        
        self.table = Table_Explorer(self)
        
        self.hbox.addWidget(self.btn_back)
        self.hbox.addWidget(self.edit)
        self.hbox.addWidget(self.btn_open)
        
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.table.container)
        
        self.edit.setEditable(True)
        
        self.directory = "C:\\"
        
        self.chdir_lock = False
        
        self.manageDriveList()
        
        self.edit.activated.connect(self.edit_change_index)
        self.btn_back.clicked.connect(self.btn_clicked_back)
        self.btn_open.clicked.connect(self.btn_clicked_open)
    
    def lock(self):
        """ prevent directory change"""
        self.chdir_lock = True
        print "lock"
    
    def isLocked(self):
        return self.chdir_lock
    
    def unlock(self):
        self.chdir_lock = False
        print "unlock"
    
    def load_directory(self, dir=""):
        
        self.table.selection = []
        
        if dir == "..":
            self.directory = fileGetParentDir(self.directory)
        elif dir != "":    
            self.directory = dir
        
        self.edit.setEditText(self.directory)
        
        self.event_manager.postEvent( self.load_directory_manager, self.directory )
        
    def load_directory_manager(self,path):    
        """
            load the current directory
            
            called from the event manager
        """
        g = lambda item: unicode(item)
        
        #set default item to '..' to enable going up one level or empty string
        default_item = [Item_Folder("..",".."),] if path != fileGetParentDir(path) else []

        data = []
           
        self.table.updateTable(0)        
        
        try:
            
            
            R = os.listdir(path)
            
        except:
            pass
            
        else:
            count = 0;
            for fname in R:
                temppath = os.path.join(self.directory,fname)
                
                if os.path.isdir(temppath) :
                    data.append( Item_Folder(fname,temppath) )
                else:
                    song = None
                    if pathMatchExt(temppath):
                        for s in MpGlobal.Player.library:
                            if comparePath(temppath,s[MpMusic.PATH]):
                                song = s
                    data.append( Item_File(fname,temppath,song) )
                    
                count += 1
                if count%5==0:
                    data.sort(key=g)
                    self.table.updateTable(-1,default_item + data)
                    
                    #QThread.msleep(20)
        finally:   
            data.sort(key=g)
            self.table.updateTable(-1,default_item + data)
    
    def manageDriveList(self):
    
        drives = systemDriveList()
        #sub1 = ['%s/music/' % d for d in drives if os.path.exists('%s/music/' % d)]
        #sub2 = ['%s/player/' % d for d in drives if os.path.exists('%s/player/' % d)]
        # add some custom paths to the default list of drives
        # most of these are convenient for me, no one else has my file system
        sub =  [os.path.join(d,'music'      ,'') for d in drives if os.path.exists(os.path.join(d,'music'      ,''))]
        sub += [os.path.join(d,'Player'     ,'') for d in drives if os.path.exists(os.path.join(d,'Player'     ,''))]
        sub += [os.path.join(d,'Discography','') for d in drives if os.path.exists(os.path.join(d,'Discography',''))]
        sub += [os.path.join(d,'Japanese'   ,'') for d in drives if os.path.exists(os.path.join(d,'Japanese'   ,''))]
        sub += [os.path.join(d,'Misc'       ,'') for d in drives if os.path.exists(os.path.join(d,'Misc'       ,''))]
    
    
        R = drives+sub
        
        R.sort()
        self.edit.clear()
            
        for item in R:
            self.edit.addItem(item)

        self.edit.setEditText(self.directory)

    def edit_change_index(self,index):
        path = self.edit.itemText(index);
        if os.path.isdir(path):
            self.load_directory(path)
            
    def btn_clicked_back(self,bool):
        path = fileGetParentDir(self.directory)
        if os.path.isdir(path) and not self.isLocked():
            self.load_directory(path)
            
    def btn_clicked_open(self,bool):
        path = self.edit.currentText();
        if os.path.isdir(path) and not self.isLocked():
            self.load_directory(path)
          
    def act_play_song(self,path):
    
        MpGlobal.Player.playState = MpMusic.PL_NO_PLAYLIST
        
        temp = id3_createSongFromPath(path)
        
        if MpGlobal.Player.load(temp) :
            MpGlobal.Player.play()
                
    def act_load_song(self,item_list):
        """ path_list as path or list-of-paths """

        self.lock()    
        
        for item in item_list:
            MpGlobal.EventHandler.postEvent(self.__act_load_song,item)

        #self.event_manager.postEvent(self.load_directory_manager,self.directory)
        self.event_manager.postEvent(self.unlock)
        
        Player_set_unsaved();    
     
    def __act_load_song(self,row_item):
        """ perform the actual load and update the display"""
        row_item.song = event_load_song(row_item.path)
        self.update();

     
class Table_Explorer(LargeTable):
    
    def __init__(self,parent):
        super(Table_Explorer, self).__init__(parent)
        
        self.showColumnHeader(False)
        self.showRowHeader(False)
        
        self.setLastColumnExpanding(True)
        
        self.addRowHighlightComplexRule(self.__rh_song,QColor(200,0,0))
        
        
    def __rh_song(self,row):
        """ return true when the given song is the current song playing
            use for highlighting the row
        """
        return self.data[row].song != None     
        
    def initColumns(self):
        c1 = TableColumnImage(self,0)
        c2 = TableColumn(self,1)
        
        g = lambda row,item: u"%r"%item
        
        c1.setTextTransform( g )
        c1.width = 18
        
        self.columns.append(c1)
        self.columns.append(c2)
        
    def mouseDoubleClick(self,row,col):
        if self.parent.isLocked():
            return
            
        if row < len(self.data):
            
            item = self.data[row]
            #print item.path
            
            if isinstance(item,Item_Folder):
                self.parent.load_directory(item.path)
            elif pathMatchExt(item.path):
                #TODO: play the actual song if it is loaded alreadty
                self.parent.act_play_song(item.path)
              
    def mouseReleaseRight(self,event):

        mx = event.x()
        my = event.y()

        cx,cy = self._mousePosToCellPos(mx,my)
        row,cur_c = self.positionToRowCol(mx,my)
        
        contextMenu = QMenu(self)
    
        act_cut = None
        act_paste = None
        act_load_song = None
        act_play_song = None
        act_open_dir = None
        act_new_folder = None
        act_rename_song = None
        act_rename_file_folder = None
        
        selection = self.getSelection()
        
        act_open_dir = contextMenu.addAction("Open Folder")
        act_new_folder = contextMenu.addAction("New Folder")
        
        contextMenu.addSeparator()
        # grab a list of songs
        song_list = [ row.path for row in selection if pathMatchExt(row.path) and row.song==None ]
        list_of_loaded_songs = [ row.song for row in selection if row.song!=None ]
        
        sl_len = len(song_list)

        if sl_len == 1:
                act_play_song = contextMenu.addAction("Play Song")
                
        if sl_len == len(selection) and sl_len > 0:
            act_load_song = contextMenu.addAction("Load Song%s"%('s' if sl_len>1 else ''))
        
        if len(list_of_loaded_songs) == len(selection) and len(list_of_loaded_songs) > 0:
            act_rename_song = contextMenu.addAction("Rename Song%s"%('s' if len(list_of_loaded_songs)>1 else ''))
        elif len(list_of_loaded_songs) == 0 and len(selection) == 1:
            act_rename_file_folder = contextMenu.addAction("Rename")
            
        # add cut and paste rules
        if not self.parent.isLocked():
            contextMenu.addSeparator()
            
            if self.parent.file_manager.count() > 0:
                act_paste = contextMenu.addAction("Paste-%d"%self.parent.file_manager.count())
                
            if len(self.selection) > 0:# and row < len(self.data):
            
                act_cut = contextMenu.addAction("Cut Selection")
                  
                contextMenu.addSeparator()

        #contextMenu.addMenu(MpGlobal.Window.menu_Sort)

        action = contextMenu.exec_( event.globalPos() )

        if action != None:
            if action == act_cut:
                self.parent.file_manager.clear()
                print len(self.getSelection())
                for item in self.getSelection():
                    if item.song != None:
                        self.parent.file_manager.setSong(item.song)
                    elif isinstance(item,Item_File):
                        self.parent.file_manager.setFile(item.path)
                    else:
                        self.parent.file_manager.setFolder(item.path)
            elif action == act_paste:
                self.parent.lock()
                self.parent.file_manager.setLibrary(MpGlobal.Player.library)
                self.parent.event_manager.postEvent(self.parent.file_manager.move,self.parent.directory)
                self.parent.event_manager.postEvent(self.parent.load_directory_manager,self.parent.directory)
                self.parent.event_manager.postEvent(self.parent.unlock)
                
            elif action == act_load_song:
                self.parent.act_load_song(selection)
                
            elif action == act_play_song:
                self.parent.act_play_song(song_list[0])
                
            elif action == act_open_dir:
                try:
                    explorerOpen(self.parent.directory)
                except:
                    pass
                    
            elif action == act_new_folder:
                self.__Action_NewFolder()
                
            elif action == act_rename_song:
                self.__Action_Rename_Song(selection)
                
            elif action == act_rename_file_folder:
                if selection[0].path != '..':
                    self.__Action_Rename_FileFolder(selection[0])
            
    def __Action_NewFolder(self):
        """
            create a new folder with the given name
        """
        dialog = dialogRename("New Folder","Create Folder")
        
        if not dialog.exec_():
            print "Folder Creation Reject"
            return;

        name = dialog.edit.displayText();
        
        name = OS_FileName_Correct(name).strip() 

        path = os.path.join(self.parent.directory,name);
        
        if not os.path.exists(path):
            try: #TODO OS ERROR - will not work on MAC
                os.mkdir(path);
            except:
                pass
            else:    
                # insert and skip the ".." item in the list
                self.data.insert(1, Item_Folder(name,path)) 
                self.update()
    
    def __Action_Rename_Song(self,selection):
        """ rename one or many songs"""
    
        fprompt = fileGetName(selection[0].name)
        
        prompt = 'Pattern Rename songs:\ne.g. $art => artist_name\nAll standard search terms apply except dates.'
        
        dialog = dialogRename(fprompt,'Rename File',prompt)  
        
        #get the new file name
        if dialog.exec_():
            new_name = dialog.edit.displayText();
            
            self.parent.lock()
            
            songs = [ row.song for row in selection if row.song != None ]
            self.parent.file_manager.clear()
            self.parent.file_manager.setSong(songs)    
            self.parent.file_manager.setRenameDict(MpMusic.D_StrToDec) 
            
            path = fileGetPath(songs[0][MpMusic.PATH])
            path = os.path.join(path,new_name)
            
            self.parent.event_manager.postEvent(self.parent.file_manager.renameSong,path)
            self.parent.event_manager.postEvent(self.parent.load_directory_manager,self.parent.directory)
            self.parent.event_manager.postEvent(self.parent.unlock)

        else: 
            debug("User canceled rename request")
            return;   
            
    def __Action_Rename_FileFolder(self,item):
        """
            Rename a single file or a group of files.
        """
        dialog = dialogRename(item.name,'Rename File')  

        if dialog.exec_():
            new_name = dialog.edit.displayText();
            
            path = item.path
            
            self.parent.lock()
            self.parent.file_manager.clear()
            if isinstance(item,Item_File):
                self.parent.file_manager.setFile(item.path) 
                path = fileGetPath(path)
                path = os.path.join(path,new_name)
                self.parent.event_manager.postEvent(self.parent.file_manager.renameFile,path)
            else:
                self.parent.file_manager.setFolder(item.path) 
                self.parent.file_manager.setLibrary(MpGlobal.Player.library)
                path = fileGetParentDir(path)
                path = os.path.join(path,new_name)
                self.parent.event_manager.postEvent(self.parent.file_manager.renameFolder,path)

            self.parent.event_manager.postEvent(self.parent.load_directory_manager,self.parent.directory)
            self.parent.event_manager.postEvent(self.parent.unlock)
            
        else: 
            print "User canceled rename request"
            return; 
  
        
class dialogRename(QDialog):

    def __init__(self,text='',title='Rename', prompt='', parent=None):
    
        super(dialogRename,self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 50)
        
        hbox = QHBoxLayout();
        vbox = QVBoxLayout(self);
        self.edit = LineEdit()

        self.btna = QPushButton("Accept")
        self.btnc = QPushButton("Cancel")
        
        hbox.addWidget(self.btnc)
        hbox.addWidget(self.btna)
        
        vbox.addWidget(self.edit)
        
        
        if len(prompt) > 0:
            vbox.addWidget(QLabel(prompt))
            
        vbox.addLayout(hbox)
        
        self.btna.clicked.connect(self.accept)
        self.btnc.clicked.connect(self.reject)
        self.edit.returnPressed.connect(self.accept)
        
        self.edit.setText(text)
        
from MpSort import *
        
from MpEventMethods import *         
from MpGlobalDefines import *
from MpScripting import *        

