
import math 
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
from SystemDateTime import * 

from App_EventManager import *

from tab_base import *

from MpSort import *
from MpCommands import *

class Tab_Library(Application_Tab):

    def __init__(self,parent=None):
        super(Tab_Library, self).__init__(parent)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(0)
        self.vbox.setMargin(0)
        
        self.hbox_search = QHBoxLayout()
        
        self.txt_searchBox = LineEdit_Search(self)
        self.search_label = QLabel("---",self)
        
        self.table = LTable_Library(self)
        
        # -------------------------------------------------------
        self.hbox_search.addWidget(self.txt_searchBox)
        self.hbox_search.addWidget(self.search_label)
        
        
        self.vbox.addSpacing(3)
        self.vbox.addLayout(self.hbox_search)
        self.vbox.addSpacing(3)
        self.vbox.addWidget(self.table.container)
        
        # ----------------------------------
        
        self.setIcon(MpGlobal.icon_note)
        
        # set the order of the table columns from the save state
        self.table.columns_setOrder(Settings.LIB_COL_ID)
        self.txt_searchBox.textEdited.connect(txtSearch_OnTextChange)

class LTable_Library(SongTable):

    def __init__(self,parent):
        super(LTable_Library,self).__init__(parent)
   
        self.showColumnHeader(True)
        self.showRowHeader(False)
        self.setLastColumnExpanding(False)
        
        self.modify_song.connect(self.event_modifiy_song)

        # enable highlighting of the current song
        s = lambda row: self.data[row][EnumSong.SELECTED]  
        b = lambda row: self.data[row].banish
        
        # highlight songs that are selected
        self.addRowHighlightComplexRule(s,self.color_text_played_recent)
        
        # change the text color for the current song
        self.addRowTextColorComplexRule(self.__rt_currentSong,self.color_text_played_recent)

        # change text color for banished songs
        self.addRowTextColorComplexRule(b,QColor(128,128,128))
        
    def __rt_currentSong(self,row):
        """ return true when the given song is the current song playing
            use for highlighting the row
        """
        return self.data[row]==MpGlobal.Player.CurrentSong
    
    def mouseDoubleClick(self,row,col):
        sel = self.getSelection()
        sel_list = list(self.selection) # get the list of selection indexes
        sel_list.sort(reverse=True)     # sort the list in reverse order and being removing one by one
        
        if len(sel) > 0 :
            index = MpGlobal.Player.CurrentIndex + 1
            MpGlobal.Player.playList = MpGlobal.Player.playList[:index] + sel + MpGlobal.Player.playList[index:]
            info_UpdateCurrent() # update the info display
            UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
            MpGlobal.Window.tbl_playlist.data = MpGlobal.Player.playList
            MpGlobal.Window.tbl_playlist.updateTable(-1,MpGlobal.Player.playList)
        return
    
    def updateTable(self,new_row_index=-1,data=None):
        self.date_mark_1 = MpGlobal.RecentEpochTime
        self.date_mark_2 = MpGlobal.LaunchEpochTime  
        super(LTable_Library,self).updateTable(new_row_index,data)
        
    def updateDisplay(self,string = None):
        """
            convenience method for running a new search.
        """
        
        if string != None:
            MpGlobal.Window.tab_library.txt_searchBox.setText(string)
            searchText = string
        else:
            searchText = MpGlobal.Window.tab_library.txt_searchBox.displayText()
            
        txtSearch_OnTextChange(searchText);    

    def event_modifiy_song(self,song):    
        #print unicode(song)
        # signal is emitted whenever the user
        # commits to updating the rating of a song
        
        info_UpdateCurrent() # update the info display
     
    def sortColumnByExifTag(self,exif_tag):
    
        col = self.getColumn(exif_tag,True)
        
        dir = 1
        if col != None:
            dir = self.setSortColumn( col )
            
        sortLibraryInplace(exif_tag,dir==-1)  
     
        self.data = MpGlobal.Player.library;
        
        self.updateDisplay()

        if exif_tag in (MpMusic.DATESTAMP,MpMusic.DATEADDEDS):
            dir_text = u"Not Recent First" if dir==-1 else u"Recent First"
        elif exif_tag < MpMusic.STRINGTERM:
            dir_text = u"\u3042-Z-A-#" if dir==-1 else u"#-A-Z-\u3042"
        else:
            dir_text = u"Decreasing" if dir==-1 else u"Increasing"
        
        UpdateStatusWidget(3,"sorted by %s - %s"%(MpMusic.exifToString(exif_tag),dir_text))
        
    def sortColumn(self,col_index):
        """
            TODO: move MpSort to Song_Sort and
            sortLibrary to MpScripting
            
        """
        col = self.columns[col_index]
        self.sortColumnByExifTag(col.index)
        
    def mouseReleaseRight(self,event):
    
        mx = event.x()
        my = event.y()

        cx,cy = self._mousePosToCellPos(mx,my)
        row,cur_c = self.positionToRowCol(mx,my)
        
        act_res = None # retore banned songs
        act_ban = None # banish songs
        
        contextMenu = QMenu(self)
    
        if len(self.selection) > 0 and row < len(self.data):

            # item_zero is just a random selected item for testing against
            item_zero = self.data[ list(self.selection)[0] ]
            # modify the context menu based on click context

            if len(self.selection) == 1:
                contextMenu.addAction("Add Song to Pool",self.__Action_addSelectionToPool)
                
                contextMenu.addAction("Edit Song",self.__Action_editSong__)
                contextMenu.addAction("DELETE Song",self.__Action_deleteSingle)
            
                if item_zero.banish:
                    act_res = contextMenu.addAction("Restore")
                else:
                    act_ban = contextMenu.addAction("Banish")
            else:
                contextMenu.addAction("Add Selection to Pool",self.__Action_addSelectionToPool)
                contextMenu.addAction("Edit Songs",self.__Action_editSong__)
                
                if item_zero.banish:
                    act_res = contextMenu.addAction("Restore ALL")
                else:
                    act_ban = contextMenu.addAction("Banish ALL")
 
                
            contextMenu.addAction("Explore Containing Folder",self.__Action_Explore__)
            
            contextMenu.addSeparator()

        contextMenu.addMenu(MpGlobal.Window.menu_Sort)

        action = contextMenu.exec_( event.globalPos() )

        if action != None:
            if action == act_res:
                for index in self.selection:
                    self.data[index].banish = False
            if action == act_ban:
                for index in self.selection:
                    self.data[index].banish = True
                    
        info_UpdateCurrent()
     
    def mouseReleaseLeft(self,event):
        row,col = self.positionToRowCol(event.x(),event.y())
        if row < len(self.data):
            UpdateStatusWidget(3,self.data[row][MpMusic.PATH])
        
    def keyReleaseUp(self,event):
        if len(self.selection) == 1:    # return focus to the text box
            if list(self.selection)[0] == 0:
                MpGlobal.Window.tab_library.txt_searchBox.setFocus()
        super(LTable_Library,self).keyReleaseUp(event)
        if len(self.selection) > 0:
            row = list(self.selection)[0]
            UpdateStatusWidget(3,self.data[row][MpMusic.PATH])
            
    def keyReleaseDown(self,event):
        super(LTable_Library,self).keyReleaseDown(event)
        if len(self.selection) > 0:
            row = list(self.selection)[0]
            UpdateStatusWidget(3,self.data[row][MpMusic.PATH])
            
    def keyReleaseOther(self,event):
        MpGlobal.Window.tab_library.txt_searchBox.setFocus()
        MpGlobal.Window.tab_library.txt_searchBox.keyReleaseEvent(event)
     
    def __Action_editSong__(self):

        dialog = dialogSongEdit.SongEditWindow(MpGlobal.Window)

        dialog.initData(self.getSelection())
        
        dialog.exec_()
        
        del dialog

    def __Action_Explore__(self):
        sel = self.getSelection()
        path = fileGetPath(sel[0][MpMusic.PATH])
        MpGlobal.Window.tab_explorer.load_directory(path)
        MpGlobal.Window.tabMain.setCurrentIndex(MpGlobal.Window.tab_explorer.getCurrentIndex())
    
    def __Action_addSelectionToPool(self):
        R = list(self.selection)
        for i in R:
            if self.data[i][MpMusic.SELECTED] == False:
                self.data[i][MpMusic.SELECTED] = True;
                MpGlobal.Player.selCount += 1;
                
        UpdateStatusWidget(0,MpGlobal.Player.selCount) 
    
    def __Action_deleteSingle(self):
        R = self.getSelection()
        if len(R) == 1:
            
            message = "Are you sure you want to delete this song?\n"
            message += R[0][MpMusic.ARTIST] + " - " + R[0][MpMusic.TITLE]
            
            if WarningMessage(message,"Delete","Cancel"):            
                MpGlobal.Player.libDelete.append( R[0] )
                MpGlobal.Player.library.remove(R[0])
                MpGlobal.Window.tab_library.table.updateDisplay()
                Player_set_unsaved();
     
class LineEdit_Search(LineEdit):
        
    def __init__(self,parent):
        super(LineEdit_Search,self).__init__(parent)
        self.parent = parent
        
        self.setPlaceholderText(MpGlobal.SEARCH_PROMPT)
        
    def keyReleaseEvent(self,event=None):
        super(LineEdit_Search,self).keyReleaseEvent(event)
        #print ">"
        if event.key() == Qt.Key_Down:
            self.parent.table.clearSelection( )
            self.parent.table.setSelection( [0,] )
            self.parent.table.updateTable(0)
            self.parent.table.setFocus()        

def txtSearch_OnTextChange(text,update=0):
    
    
    text = MpGlobal.Window.tab_library.txt_searchBox.textUpdate(text)
    text += MpGlobal.SEARCH_AUTOAPPEND
    MpGlobal.Window.tab_library.table.clearSelection()
    
    if text == "" :
        MpGlobal.Player.libDisplay = MpGlobal.Player.library[:]
        MpGlobal.Window.tab_library.table.updateTable(update,MpGlobal.Player.libDisplay)
        MpGlobal.Window.statusWidgets[2].setToolTip(u"No Search Terms")
        UpdateStatusWidget(2,0)
    else:
        #time = datetime.datetime.now()
        #try:
        so = SearchObject(text)
        MpGlobal.Window.statusWidgets[2].setToolTip(unicode(so))
        MpGlobal.Player.libDisplay = so.search(MpGlobal.Player.library)
        MpGlobal.Window.tab_library.table.updateTable(update,MpGlobal.Player.libDisplay)
        UpdateStatusWidget(2,so.termCount)
        #except Exception as e:
        #    debug("EVAL ERROR: %s"%e.args)
            
        #end = datetime.datetime.now()
        #debug( "Search Time: %s"%(end-time) )
        
    #MpGlobal.Window.tabMain.setTabText(0,"Library (%d)"%len(MpGlobal.Player.libDisplay))
    MpGlobal.Window.tab_library.search_label.setText("%d/%d"%(len(MpGlobal.Player.libDisplay),len(MpGlobal.Player.library)))
      

import dialogSongEdit
import dialogColumnSelect


from Song_Object import Song
from datatype_hex64 import *

from MpScripting import *
from Song_Search import *


from MpGlobalDefines import *
from MpApplication import *
            
from tab_base import *

from MpSort import *
from MpCommands import *