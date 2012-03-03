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
        
    def mouseReleaseRight(self,event):
        
        if len(self.selection) > 0:
            
            row = list(self.selection)[0]
            
            contextMenu = QMenu(MpGlobal.Window)
            
            if MpGlobal.Player.stopNext or \
                MpGlobal.Player.stopIndex == MpGlobal.Player.CurrentIndex or \
                MpGlobal.Player.stopIndex == row:
                contextMenu.addAction("Clear Stop Marker",self.__Action_CanStop__)
            else:
                contextMenu.addAction("Stop After This",self.__Action_StopHere__)
            
            contextMenu.addSeparator()
            contextMenu.addAction("Find Lyrics",self.__Action__GoTo_Lyrics__)
            contextMenu.addAction("Artist Wiki Page",self.__Action__GoTo_Wiki__)
            contextMenu.addAction("Explore Containing Folder",self.__Action__EXPLORE__)
            contextMenu.addAction("Search for Artist",self.__Action_searchARTIST__)
            contextMenu.addAction("Search for Album",self.__Action_searchALBUM__)
            
            contextMenu.exec_( event.globalPos() )
             
    def mouseDoubleClick(self,row,col):
        #print row,col
        if col != -1:
            MpGlobal.Player.playSong(row)
        else:
            # set stop next if the double click is on the current song.
            # otherwise toggle the value of the stop Index
            if row == MpGlobal.Player.CurrentIndex:
                MpGlobal.Player.setStopNext( not MpGlobal.Player.stopNext );
                MpGlobal.Player.stopIndex = -1
                
            elif MpGlobal.Player.stopIndex == row:
                MpGlobal.Player.stopIndex = -1
                MpGlobal.Player.setStopNext( False );
            else:
                MpGlobal.Player.stopIndex = row
                MpGlobal.Player.setStopNext( False );
            
    def processDropEvent(self,source,row,data):
        
        if source == self:
            sel = self.getSelection()
            # get the list of currently selected song, these are the indices of the songs in 'data'
            sel_list = list(self.selection) # get the list of selection indexes
            # get the updated list of indices after the move
            sel_list = MpGlobal.Player.playlist_reinsertIndexList(sel_list,row)
            # update the selection
            self.setSelection( sel_list )
        else:
            # dropped data from other source must all be songs
            if not all( [ isinstance(item,Song) for item in data ] ):
                return
            # insert the songs at the drop index
            MpGlobal.Player.playlist_insertSongList(row,data)
            # set the selection to the dropped songs
            self.setSelection( range(row,row+len(data) ) )
            
        # update the data for this table
        #self.setData( MpGlobal.Player.get_playlist() )

    def keyPressDelete(self,event):
        sel = self.getSelection()
        sel_list = list(self.selection) # get the list of selection indexes

        if len(sel_list) > 0:
            MpGlobal.Player.playlist_removeIndexList(sel_list)
            
            row = min(sel_list)
            
            if row >= MpGlobal.Player.len_playlist():
                row = MpGlobal.Player.len_playlist() - 1
                
            if row >= 0:
                self.setSelection([row,])
            else:
                self.clearSelection()
            
            #self.setData( MpGlobal.Player.get_playlist() )
      
    def __Action_StopHere__(self):
        row = list(self.selection)[0]
        
        if row == MpGlobal.Player.CurrentIndex:
            MpGlobal.Player.setStopNext( True );
            MpGlobal.Player.stopIndex = -1
        else:
            MpGlobal.Player.stopIndex = row
            MpGlobal.Player.setStopNext( False );
    
    def __Action_CanStop__(self):
        MpGlobal.Player.stopIndex = -1
        MpGlobal.Player.setStopNext( False );
    
    def __Action__GoTo_Wiki__(self):
        if len(self.selection) > 0:
            song = self.getSelection()[0]
            s = "http://en.wikipedia.org/w/index.php?search="
            s += song[MpMusic.ARTIST].replace(" ","+")
            explorerOpen(s)
    
    def __Action__GoTo_Lyrics__(self):
        if len(self.selection) > 0:
            song = self.getSelection()[0]
            s = "http://www.songmeanings.net/query/?q="
            s += song[MpMusic.ARTIST].replace(" ","+")
            s += "&type=artists"
            explorerOpen(s)
        
    def __Action__EXPLORE__(self):
        if len(self.selection) > 0:
            song = self.getSelection()[0]
            
            path = fileGetPath(song[MpMusic.PATH])
            MpGlobal.Window.tab_explorer.load_directory(path)
            MpGlobal.Window.tabMain.setCurrentIndex(MpGlobal.Window.tab_explorer.getCurrentIndex())
        
    def __Action_searchARTIST__(self):
        if len(self.selection) > 0:
            song = self.getSelection()[0]
            s = u".art \""+song[MpMusic.ARTIST]+"\""
            
            MpGlobal.Window.tab_library.table.updateDisplay(s);
            
    def __Action_searchALBUM__(self):
        if len(self.selection) > 0:
            song = self.getSelection()[0]
            s = u".art \""+song[MpMusic.ARTIST][:]+u"\""
            s += u"; .abm \""+song[MpMusic.ALBUM][:]+u"\""
            
            MpGlobal.Window.tab_library.table.updateDisplay(s);  
      
      
from Song_Object import Song
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from Song_Search import *
from MpCommands import *



from SystemPathMethods import *

from MpApplication import *        