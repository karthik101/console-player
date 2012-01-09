import math 
import sys
import os  

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *

from widgetLargeTable import LargeTable

class LTable_PlayList(LargeTable):

    def __init__(self,parent):
        super(LTable_PlayList,self).__init__(parent)
    
        #easy, this controls what gets displayed
        self.column(0).text_transform = lambda x,y: u"%s - %s"%(x[MpMusic.ARTIST],x[MpMusic.TITLE])
        
        self.showColumnHeader(False)
        self.setLastColumnExpanding(True)

        # enable highlighting of the current song
        self.addRowHighlightComplexRule(self.__rh_currentSong,QColor(100,0,200,255))
        self.addRowTextColorComplexRule(self.__rt_stopNext,QColor(200,30,30))
        
    def __rh_currentSong(self,row):
        """ return true when the given song is the current song playing
            use for highlighting the row
        """
        return row==MpGlobal.Player.CurrentIndex
        
    def __rt_stopNext(self,row):
        return row==MpGlobal.Player.stopIndex or (row==MpGlobal.Player.CurrentIndex and MpGlobal.Player.stopNext)
        
    def mouseDoubleClick(self,row,col):
        if col != -1:
            MpGlobal.Player.playSong(row)
        else:
            if MpGlobal.Player.stopIndex == row:
                MpGlobal.Player.stopIndex = -1
            else:
                MpGlobal.Player.stopIndex = row
                MpGlobal.Player.stopNext = False;
            
    def processDropEvent(self,source,row,data):
        
        
        
        if source == self:
            self.__dropEvent_self(row,data)
        else:
        
            for item in data: # dropped data must all be songs
                if not isinstance(item,Song):
                    return
                    
            self.data = self.data[:row] + data + self.data[row:]
            self.selection = set( range(row,row+len(data) ) )
            if row < MpGlobal.Player.CurrentIndex:  
                MpGlobal.Player.CurrentIndex += len(data)
            
        MpGlobal.Player.playList = self.data    
        info_UpdateCurrent() # update the info display
        UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
        
        self._sbar_ver_setrange()
            
    def __dropEvent_self(self,row,data): 
        sel = self.getSelection()
        sel_list = list(self.selection) # get the list of selection indexes
        sel_list.sort(reverse=True)     # sort the list in reverse order and being removing one by one
        
        for i in sel_list:
            self.data.pop(i)
            if i < row:     # update the drop row if we are removing songs from before it
                row -= 1;
            if i < MpGlobal.Player.CurrentIndex: # update the current index for similar reseaons
                MpGlobal.Player.CurrentIndex -= 1
    
        
        self.data = self.data[:row] + sel + self.data[row:]

        if row <= MpGlobal.Player.CurrentIndex: # adjust the current index + the number of songs being dropped before ti
            MpGlobal.Player.CurrentIndex += len(sel)
        
        if row > len(self.data):    # for resetting the selection, we must adjust the row
            row = len(self.data) - len(sel)
        self.selection = set( range(row,row+len(sel) ) )

        # if the current song was moved then the current index must be updated
        # TODO: this may cause a bug, where there are two copies of one song in the selection
        if MpGlobal.Player.CurrentSong in sel:
            MpGlobal.Player.CurrentIndex = row + sel.index(MpGlobal.Player.CurrentSong)
       
    def keyReleaseDelete(self,event):
        sel = self.getSelection()
        sel_list = list(self.selection) # get the list of selection indexes
        sel_list.sort(reverse=True)     # sort the list in reverse order and being removing one by one
        
        row = self.selection_last_row_added
        
        if row >= len(self.data):   
            return
        
        for i in sel_list:
            self.data.pop(i)
            if i < row:     # update the drop row if we are removing songs from before it
                row -= 1;
            if i < MpGlobal.Player.CurrentIndex: # update the current index for similar reseaons
                MpGlobal.Player.CurrentIndex -= 1
        
        if row >= len(self.data): 
            row = len(self.data)-1  # so that the last row will be selected
            
        if row >= 0:
            self.selection = {row,}
            if MpGlobal.Player.CurrentSong in sel:
                self.mouseDoubleClick(row,0)
        else:
            self.selection = set()
        self.selection_last_row_added = row
        self.selection_first_row_added = row      
        
        MpGlobal.Player.playList = self.data
            
        info_UpdateCurrent()
        
        UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
      
from Song_Object import Song
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from Song_Search import *
from MpCommands import *



from SystemPathMethods import *

from MpApplication import *        