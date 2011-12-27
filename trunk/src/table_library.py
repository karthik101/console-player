

import math 
import sys
import os  

import widgetTable
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *
from MpApplication import *

import dialogSongEdit
import dialogColumnSelect

from SystemDateTime import DateTime
from widgetLargeTable import LargeTable,TableColumn

from Song_Table import *

#TODO-LIB - flag used for stuff to do

class LTable_Library(SongTable):

    def __init__(self,parent):
        super(LTable_Library,self).__init__(parent)
   
        self.showColumnHeader(True)
        self.showRowHeader(False)
        self.setLastColumnExpanding(False)
        
        self.modify_song.connect(self.event_modifiy_song)
        # enable highlighting of the current song
        
        # highlight songs that are selected to be in the pool
        self.addRowHighlightComplexRule(self.__rh_Selected,self.color_text_played_recent)
        # change the text color for the current song
        self.addRowTextColorComplexRule(self.__rt_currentSong,self.color_text_played_recent)
        
    def __rh_Selected(self,row):
        """ return true when the given song is the current song playing
            use for highlighting the row
        """
        return self.data[row][EnumSong.SELECTED]  
        
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
            MpGlobal.Window.txt_searchBox.setText(string)
            searchText = string
        else:
            searchText = MpGlobal.Window.txt_searchBox.displayText()
            
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
        
        contextMenu = QMenu(self)
    
        if len(self.selection) > 0 and row < len(self.data):

            # modify the context menu based on click context

            if len(self.selection) == 1:
                contextMenu.addAction("Add Song to Pool",self.__Action_addSelectionToPool)
                
                contextMenu.addAction("Edit Song",self.__Action_editSong__)
                contextMenu.addAction("DELETE Song",self.__Action_deleteSingle)
            
            else:
                contextMenu.addAction("Add Selection to Pool",self.__Action_addSelectionToPool)
                contextMenu.addAction("Edit Songs",self.__Action_editSong__)
                
            contextMenu.addAction("Explore Containing Folder",self.__Action_Explore__)
            
            contextMenu.addSeparator()

        contextMenu.addMenu(MpGlobal.Window.menu_Sort)

        action = contextMenu.exec_( event.globalPos() )

        info_UpdateCurrent()
     
    def mouseReleaseLeft(self,event):
        row,col = self.positionToRowCol(event.x(),event.y())
        if row < len(self.data):
            UpdateStatusWidget(3,self.data[row][MpMusic.PATH])
        
    def keyReleaseUp(self,event):
        if len(self.selection) == 1:    # return focus to the text box
            if list(self.selection)[0] == 0:
                MpGlobal.Window.txt_searchBox.setFocus()
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
        MpGlobal.Window.txt_searchBox.setFocus()
        MpGlobal.Window.txt_searchBox.keyPressEvent(event)
     
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
                MpGlobal.Window.tbl_library.updateDisplay()
                Player_set_unsaved();
             
def txtSearch_OnTextChange(text,update=0):
    
    
    text = MpGlobal.Window.txt_searchBox.textUpdate(text)
    text += MpGlobal.SEARCH_AUTOAPPEND
    MpGlobal.Window.tbl_library.selection = set() 
    
    if text == "" :
        MpGlobal.Player.libDisplay = MpGlobal.Player.library[:]
        MpGlobal.Window.tbl_library.updateTable(update,MpGlobal.Player.libDisplay)
        MpGlobal.Window.statusWidgets[2].setToolTip(u"No Search Terms")
        UpdateStatusWidget(2,0)
    else:
        #time = datetime.datetime.now()
        #try:
        so = SearchObject(text)
        MpGlobal.Window.statusWidgets[2].setToolTip(unicode(so))
        MpGlobal.Player.libDisplay = so.search(MpGlobal.Player.library)
        MpGlobal.Window.tbl_library.updateTable(update,MpGlobal.Player.libDisplay)
        UpdateStatusWidget(2,so.termCount)
        #except Exception as e:
        #    debug("EVAL ERROR: %s"%e.args)
            
        #end = datetime.datetime.now()
        #debug( "Search Time: %s"%(end-time) )
        
    #MpGlobal.Window.tabMain.setTabText(0,"Library (%d)"%len(MpGlobal.Player.libDisplay))
    MpGlobal.Window.search_label.setText("%d/%d"%(len(MpGlobal.Player.libDisplay),len(MpGlobal.Player.library)))
        
        
from Song_Object import Song
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from Song_Search import *
from MpCommands import *

        