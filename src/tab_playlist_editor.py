import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

isPosix = os.name == 'posix'

from widgetLineEdit import LineEdit
from widgetLargeTable import *
from Song_Table import *
from Song_Search import *
from SystemPathMethods import * 

from App_EventManager import *

from tab_base import *
        
class Tab_PlaylistEditor(Application_Tab):

    def __init__(self,parent=None):
        super(Tab_PlaylistEditor, self).__init__(parent)
        self.parent = parent
        
        
        self.event_manager = EventManager()
        
        self.vbox = QVBoxLayout(self)     
        self.hbox_main = QHBoxLayout()             
        self.splitter = QSplitter(self)
        
        self.edit = LineEdit(self)

        self.table_library  = PLETable_library(self)
        self.table_playlist = PLETable_playlist(self)
        
        self.table_library.otable = self.table_playlist
        self.table_playlist.otable = self.table_library
        
        
        self.page_l = QWidget()
        self.page_r = QWidget()
       
        self.vbox_l = QVBoxLayout(self.page_l) # vertical manager for left and right of splitter
        self.vbox_r = QVBoxLayout(self.page_r)
        
        self.hbox_l = QHBoxLayout() #horizontal manager for buttons in left or right
        self.hbox_r = QHBoxLayout()
        
        self.btn_reload = QPushButton("Rebuild Library")
        
        self.btn_open = QPushButton("Open")
        self.btn_save = QPushButton("Save")
        self.btn_sync = QPushButton("Sync")
        self.btn_play = QPushButton("Play")
        
        self.lbl_count_l = QLabel("")
        self.lbl_count_r = QLabel("")
        
        self.hbox_l.addWidget(self.btn_reload)
        self.hbox_l.addWidget(self.lbl_count_l)
        
        self.vbox_l.addLayout(self.hbox_l)
        self.vbox_l.addWidget(self.table_library.container)
        
        self.hbox_r.addWidget(self.btn_open)
        self.hbox_r.addWidget(self.btn_save)
        self.hbox_r.addWidget(self.btn_sync)
        self.hbox_r.addWidget(self.btn_play)
        self.hbox_r.addWidget(self.lbl_count_r)
        
        self.vbox_r.addLayout(self.hbox_r)
        self.vbox_r.addWidget(self.table_playlist.container)
        
        self.splitter.addWidget(self.page_l)
        self.splitter.addWidget(self.page_r)
        
        self.hbox_main.addWidget(self.edit)
        
        self.vbox.addLayout(self.hbox_main)
        self.vbox.addWidget(self.splitter)
        
        self.vbox_l.setMargin(0)
        self.vbox_r.setMargin(0)
        self.vbox.setMargin(0)

        
        
        # -----------------------------------------
        
        self.sort_index = MpMusic.ARTIST
        self.sort_direction = 1 # 1 or -1
        
        self.library = sortLibrary(self.sort_index)
        self.library_display = self.library
        self.playlist = []
        self.playlist_display = self.playlist
        
        self.edit.textEdited.connect(self.text_edit)
        #self.btn_reload.clicked.connect()
        self.btn_open.clicked.connect(self.btn_click_playlist_load)
        self.btn_save.clicked.connect(self.btn_click_playlist_save)
        self.btn_sync.clicked.connect(self.btn_click_playlist_sync)
        self.btn_play.clicked.connect(self.btn_click_playlist_play)
        
        self.table_library.setData(self.library)
        
        self.setLabels()
  
    def setLabels(self):
        #todo on drop handle this so it does not need to be recalculated
        
        self.setFileSize()
        
        self.lbl_count_l.setText("%d/%d [%d]"%(len(self.library_display),len(self.library),len(MpGlobal.Player.library)))
        self.lbl_count_r.setText("%d/%d %dMB"%(len(self.playlist_display),len(self.playlist),self.filesize))
        
    def runSearch(self,text=None):
        """
            perform a search over the data, using the text in the textbox
            as the search term
        """
        if text == None:
            text = self.edit.displayText()
            
        if text == "" :
            self.library_display = self.library
            self.playlist_display = self.playlist
        else:
                
            so = SearchObject(text)
            
            self.library_display = so.search(self.library)
            self.playlist_display = so.search(self.playlist)
            
        self.setLabels()
        
        self.lbl_count_l.setAlignment(Qt.AlignRight)
        self.lbl_count_r.setAlignment(Qt.AlignRight)
        
        self.table_library._sbar_ver_setrange()    
        self.table_playlist._sbar_ver_setrange()    
        
        self.table_library.updateTable(0,self.library_display)
        self.table_playlist.updateTable(0,self.playlist_display)
    
    def insertData(self,data,target_1,target_2):
        """
            at any time, both the library and playlist are sorted the same
            due to this exploitable fact, data can be inserted by comparing each element in order
            then finding the element in target_1 or target_2 that i should be place after.
            once the first item in both targets is found, finding where item 2 in data should
            be place will be even easier, then each item afterwards will be just as easy

            target_1 should be either playlist or library
            target_2 should be either playlist_display or library_display
        """
    
        # get the key used to compare two elements when sorting
        key = sortKey(self.sort_index)
        
        if self.sort_direction == 1:
            # return true when the data song is smaller than target song
            sort_key = lambda data_song,target_song : key(data_song) < key(target_song)
        else:
            # return true when the data song is greater than the target song
            sort_key = lambda data_song,target_song : key(data_song) > key(target_song)
            
        save_index = self.__insertData_target(sort_key,data,target_1)
        
        if target_1 != target_2:
            return self.__insertData_target(sort_key,data,target_2)
        
        return save_index
        
    def __insertData_target(self,sort_key,data,target):
    
        # first do a binary search to find where to first start placing items:
        # this will give O(log(n)) for first insertion instead of O(N)
        
        index = 0 # should be set by a binary search
        save_index = []
        i=0    
        while index < len(target):
            if sort_key(data[i],target[index]):
                target.insert(index,data[i])
                save_index.append(index)
                i += 1
                if i == len(data):
                    return save_index
            
            index += 1
            
        # add any remaining items to the end of the data set
        if i < len(data):
            target += data[i:]  
            save_index += range(index,len(target)) # generate indexes of items for selection
        return save_index 
    
    def text_edit(self,text):
        
        self.table_library.selection = set()
        self.table_playlist.selection = set()
        
        self.runSearch(text)
            
    def setFileSize(self):
        self.filesize = 0    
        for item in self.playlist:
            self.filesize += item[MpMusic.FILESIZE]
        self.filesize /= 1024 # to mB 
    
    def playlist_load(self,path):
    
        R = MpGlobal.Player.library[:] # the resulting list with playlist removed
        
        sortList(R,self.sort_index,self.sort_direction==-1)
        
        index,S = playListLoad(path,R) # index is ignored

        for j in range(len(S)) : 

            if j%10 == 0:
                self.library = R
                self.playlist = S
                self.setLabels()
                self.runSearch()
                QThread.msleep(10)
            
            for i in range(len(R)):
                if S[j] == R[i]:
                    R.pop(i)
                    break;
            
        
        self.library = R
        self.playlist = S
        self.setLabels()
        self.runSearch()

    def btn_click_playlist_load(self,bool=False):
        
        path = QFileDialog.getOpenFileName(MpGlobal.Window,
                "Open Playlist File",
                os.path.join(MpGlobal.installPath,"playlist",self.name+'.m3u'),
                "M3U Files (*.playlist)")
        
        if path != "":
            name = fileGetName(path)
            self.setName(name)
            
            #self.playlist_load(path)
            self.event_manager.postEvent(self.playlist_load,path)
            return True
        else:
            return False
    
    def btn_click_playlist_save(self,bool=False):
    
        path = QFileDialog.getSaveFileName(MpGlobal.Window,
            "Save Playlist File",
            os.path.join(MpGlobal.installPath,"playlist",self.name+'.m3u'),
            "M3U Files (*.playlist)")
            
        if path != "":
            playListSave(path,self.playlist) 
            name = fileGetName(path)
            self.setName(name)
            return True
        else:
            return False    
    
    def btn_click_playlist_sync(self,bool=False):
        pass
        
    def btn_click_playlist_play(self,bool=False):
        registerNewListAsPlayList(self.playlist,autoStart = True)
        MpGlobal.Player.playSong(0)
    
class PLETable_base(SongTable):
    """
        base table for editing a playlist
        
        methods common to both the left and right table go here
    """
    
    def __init__(self,parent=None):
        super(PLETable_base, self).__init__(parent)
        
        self.otable = None # the other table
        
        self.showRowHeader(False)
        
        self.setAutoHideScrollbar(True,True)
        
        self.column_changed_signal.connect(self.columns_changed)
        self.column_header_resize.connect(self.columns_resized) #TODO: i should probably remove this
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("data/list") and event.source()==self.otable:
            event.accept()
        else:
            event.ignore()
            
    def sortColumn(self,col_index):
        """
            when a column is sorted both tables must be sorted and updated
            
        """
        self.parent.sort_index =  self.columns[col_index].index
        
        self.parent.sort_direction = self.setSortColumn(col_index)
        
        
        sortList(self.parent.library,self.parent.sort_index,self.parent.sort_direction==-1)
        sortList(self.parent.playlist,self.parent.sort_index,self.parent.sort_direction==-1)
        
        self.parent.runSearch()
        #self.parent.table_library.updateTable(0,self.parent.library)
        #self.parent.table_playlist.updateTable(0,self.parent.playlist)
        
    def columns_changed(self):
        """ when the table has columns hidden or restored, the effect will happen on the other table"""
        order = self.columns_getOrder()
        self.otable.columns_setOrder(order)
        
    def columns_resized(self):
        """ when ever one table resizes the col width, the effect will appear on the other table"""
        for i in range(len(self.columns)):
            self.otable.columns[i].width = self.columns[i].width
        self.otable.update()      
        
class PLETable_library(PLETable_base):        
    """
        table to display songs remaining in the library
    """

    def processDropEvent(self,source,row,data):
        if source != self.parent.table_playlist:
            return
        #self.parent.library += data
        
        #sortList(self.parent.library,self.parent.sort_index,self.parent.sort_direction==-1)
        
        
    
        sel = self.parent.insertData(data,self.parent.library,self.parent.library_display)
        
        self.parent.table_playlist.deleteSelection()
        self.selection = set(sel)
        
        self.scrollTo(sel[0],len(sel))
        
        self.parent.table_library.setData(self.parent.library_display)
        self.parent.table_library.update()
        
        self.parent.table_playlist.setData(self.parent.playlist_display)
        self.parent.table_playlist.update()
        
        self.parent.setLabels()
    
    def deleteSelection(self):
        sel = self.getSelection()
        #remove the selection from both the actual list
        # and from the display list then update this table
        for row in sel:
            self.parent.library.remove(row)
            # we only need to remove the row when the list does not equal the
            # display list, and the item is in view. this one check does both
            if row in self.parent.library_display:
                self.parent.library_display.remove(row)
         
        self.selection = set()
        self.updateTable(-1,self.parent.library_display)
    
class PLETable_playlist(PLETable_base):  
    """
        table to display songs in the playlist
    """
            
    def processDropEvent(self,source,row,data):
        if source != self.parent.table_library:
            return
        
        # dropped data is in order 
            
        #self.parent.playlist += data
        
        #sortList(self.parent.playlist,self.parent.sort_index,self.parent.sort_direction==-1)
 
        
        
        sel = self.parent.insertData(data,self.parent.playlist,self.parent.playlist_display)
        
        self.parent.table_library.deleteSelection()
        self.selection = set(sel)
        
        self.scrollTo(sel[0],len(sel))
        
        self.parent.table_library.setData(self.parent.library_display)
        self.parent.table_library.update()
        
        self.parent.table_playlist.setData(self.parent.playlist_display)
        self.parent.table_playlist.update()
        
        self.parent.setLabels()

    def deleteSelection(self):
        sel = self.getSelection()

        for row in sel:
            self.parent.playlist.remove(row)
            # we only need to remove the row when the list does not equal the
            # display list, and the item is in view. this one check does both
            if row in self.parent.playlist_display:
                self.parent.playlist_display.remove(row)
         
        self.selection = set()
        self.updateTable(-1,self.parent.playlist_display)
    
from MpSort import *
        
from MpGlobalDefines import *
from MpScripting import *        

