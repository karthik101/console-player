import math 
import sys
import os  

import widgetTable
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
 
class TablePlayList(widgetTable.Table):
    """
        Play Lists.
        
        Playlists are genereated from the selection pool. The pool can be manipulated by using the commands 'find' and 'remove' however, it is a better idea to use presets.
        
        
        Getting Started
        
        
        \\<b\\> Presets\\</b\\>
            Customize your presets in the settings menu.
            
            In the bottom right of the playlist table, there is a little green 'A' icon. The number next to indicates the preset to use. When the current playlist finishes a new playlist will automatically be made from that preset.
    
    """
    brush_highlight1 = QBrush(QColor(150,50,100,128))
    brush_highlight2 = QBrush(QColor(255,5,5,128))
    brush_selected = QBrush(QColor(25,50,150,255))
    def __init__(self,parent=None):
        header = ["#","Data"]
        super(TablePlayList,self).__init__(parent,header)
        self.table.horizontalHeader().hide()
        self.table.setColumnWidth(0,20)
        self.table.setColumnWidth(1,MpGlobal.SplitterWidthMax)
        self.table.setDragDropMode(QAbstractItemView.DragDrop)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setDragType("dragFromPlayList")
        self.setDragReceiveType("dragFromPlayList")
        self.addDragReceiveType("dragFromLibrary")
        self.addDragReceiveType("dragTableEditor_Left")
        self.addDragReceiveType("dragTableEditor_Right")
        #self.table.resizeColumnToContents(1)
        self.table.setObjectName("table_Playlist")
    def FillTable(self,offset=-1):  
        super(TablePlayList,self).FillTable(offset)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
    def FillRow(self,index):
        i = "%s - %s"%(self.data[index][MpMusic.ARTIST],self.data[index][MpMusic.TITLE])
        R = [index+1,i]
        return R
    def FillRowColor(self,index):
    
        # b1 provides a bg-color for the numbered
        # when the given index has a special state and is selected.
        b1 = self.brush_selected;
        if index == MpGlobal.Player.CurrentIndex:
            b1 = self.brush_highlight1;
        elif index == MpGlobal.Player.stopIndex:
            b1 = self.brush_highlight2;
        
        elif not self.table.hasFocus():
            b1 = self.brush_selectedOOF;
            
        if index in self.selection:
            if self.table.hasFocus() :
                return (b1,self.brush_selected)
            else:
                return (b1,self.brush_selectedOOF)
        elif index == MpGlobal.Player.stopIndex:
            return (b1,self.brush_highlight2)
            
        elif index == MpGlobal.Player.CurrentIndex:
            if MpGlobal.Player.stopNext :
                return (b1,self.brush_highlight2)
            elif MpGlobal.Player.CurrentIndex < len(self.data) and not MpGlobal.INPUT_PLAY_GOTO_ZERO:
                return self.brush_highlight1 
                    
        return self.brush_default
            
    def DoubleClick(self,item):
        offset = 0# MpGlobal.Window.tbl_playlist.getDisplayOffset() # TODO - DUMMY LARGETABLE
        index = offset+item.row()
        if item.column() == 1:
            MpGlobal.Player.playSong(index)
        else:
            if MpGlobal.Player.stopIndex == index:
                MpGlobal.Player.stopIndex = -1
            else:
                MpGlobal.Player.stopIndex = index
                MpGlobal.Player.stopNext = False;
            MpGlobal.Window.tbl_playlist.updateTable()
    def dropEvent(self,event,row):
        dragType = event.mimeData().text()
        if event.mimeData().hasText == False :
            return;
        if dragType not in self.dragReceive :
            return; # make sure that the drag is of valid type
            
        srcSelf = (event.source() == self.table)
        
        R = [] #list of indexes of songs in an array

        data = None;
        
        # determine which data the drag is coming from
        if srcSelf :
            R = list(self.selection)
            data = MpGlobal.Player.playList
        else:
            if dragType == "dragFromLibrary":
                R = list(MpGlobal.Window.tbl_library.selection)
                data = MpGlobal.Player.libDisplay
            elif dragType == "dragTableEditor_Left":
                tab   = MpGlobal.Window.tabMain
                index = tab.currentIndex()
                text  = tab.tabText(index)
                table = None
                for item in MpGlobal.Window.editorTabs:
                    if item[0] == text:
                        table = item[2]
                if table == None:
                    debug("Table Error")
                    return;
                R = list(table.selection)
                data = table.data
            elif dragType == "dragTableEditor_Right":
                tab   = MpGlobal.Window.tabMain
                index = tab.currentIndex()
                text  = tab.tabText(index)
                table = None
                for item in MpGlobal.Window.editorTabs:
                    if item[0] == text:
                        table = item[3]
                if table == None:
                    debug("Table Error")
                    return;
                R = list(table.selection)
                data = table.data
        
        if len(R) > 0:
            R.sort() # sort the index values from low to high    
             
            cindex_flag = False # if true, magic must be done to find the current index again
            
            tempsong = MpGlobal.Player.CurrentSong
            # with a list of row indexes, convert them to a list of songs
            S = []
            index = row + self.getDisplayOffset()
            
            if index > len(MpGlobal.Player.playList):
                # if drop position is outside list range,
                # this will drop the item after the last element
                index = len(MpGlobal.Player.playList)
            
            # save the relative location of the stop index, when compared to the current song
            save_stop_index = MpGlobal.Player.stopIndex - MpGlobal.Player.CurrentIndex;
            
            for x in range(len(R)):
                if x < len(data):
                    S.append(data[R[x]])
            if len(S) == 0:
                return
            # S is now an array of songs ready to be spliced into the play list
            if srcSelf :
                # we are moving elements within the array
                # sort and remove them one at a time
                # update the insert index if needed
                R.reverse()
                for x in R:
                    MpGlobal.Player.playList.pop(x)
                    if x == MpGlobal.Player.CurrentIndex :
                        cindex_flag = True
                    if x < MpGlobal.Player.CurrentIndex :
                        MpGlobal.Player.CurrentIndex -= 1
                    if x < index:
                        index -= 1
            # splice in the drop list of songs into the playlist
            MpGlobal.Player.playList = MpGlobal.Player.playList[:index] + S + MpGlobal.Player.playList[index:]
            if index <= MpGlobal.Player.CurrentIndex :
                MpGlobal.Player.CurrentIndex += len(S)
            if cindex_flag :
                # this takes care if the same song is in the list twice
                # however if the same song is in the selection twice then user is dumb
                for x in range(index,index+1+len(S)):
                    if MpGlobal.Player.playList[x] == tempsong :
                        MpGlobal.Player.CurrentIndex = x;
                        break;
                        
            if MpGlobal.Player.stopIndex >= 0 :
                MpGlobal.Player.stopIndex = MpGlobal.Player.CurrentIndex + save_stop_index;
                # stop_index cannot be beyond the length of the playlist
                if MpGlobal.Player.stopIndex >= len(MpGlobal.Player.playList):
                    MpGlobal.Player.stopIndex = len(MpGlobal.Player.playList)-1;
                    
            self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.playList)
            # create a list of all the moved elements
            R = range(index,index+len(R))
            # use this list to form a new selection
            self.selection = set(R)
            # highlight the selected items
            UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
            self.FillTable()
            MpGlobal.Player.updateDisplayIndex()
        #else:
        #    debug("Drop Received Empty Selection")
        # if srcSelf is true, the drop operation came from self.
        # otherwise some magic needs to be done to get the selection from elseware
    def keyReleaseEvent(self,event):
    
        _ctrl = event.modifiers()&Qt.ControlModifier ==  Qt.ControlModifier
        
        if event.key() == Qt.Key_Up:
            self.__keyboard_scroll_UP__(); 
        elif event.key() == Qt.Key_Down:
            self.__keyboard_scroll_DOWN__();
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            #index = 0;
            if len(self.selection) > 0:
                R = list(self.selection)
                R.sort()
                index = R[0]
                MpGlobal.Player.playSong(index);
            
        elif event.key() == Qt.Key_Delete :
            R = list(self.selection)
            R.sort(reverse = True)
            cindex_flag = False
            for x in R:
                MpGlobal.Player.playList.pop(x)
                if x == MpGlobal.Player.CurrentIndex :
                    cindex_flag = True
                if x < MpGlobal.Player.CurrentIndex :
                    MpGlobal.Player.CurrentIndex -= 1
            self.selection = set()
            if cindex_flag :
                MpGlobal.Player.playSong(MpGlobal.Player.CurrentIndex)
            MpGlobal.Player.updateDisplayIndex()
            
            # there is a odd jump relative to the mouse if this is not done
            offset = self.getDisplayOffset()
            if offset == self.scroll_MaxRange:
                offset -= 1
                
            self.UpdateTable(offset,MpGlobal.Player.playList)
            UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
        elif _ctrl and event.key() == Qt.Key_A:
            self.selection = set(range(len(self.data)));
            self.UpdateTable(-1);       
            
    def minimumSize(self):
        return QtCore.QSize(200, 200)
        
        
        
from Song_Object import Song
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from Song_Search import *
from MpCommands import *



from SystemPathMethods import *

from MpApplication import *        