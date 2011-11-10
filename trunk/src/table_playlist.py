import math 
import sys
import os  

import widgetTable
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *

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
        offset = MpGlobal.Window.tbl_playlist.getDisplayOffset()
        index = offset+item.row()
        if item.column() == 1:
            MpGlobal.Player.playSong(index)
        else:
            if MpGlobal.Player.stopIndex == index:
                MpGlobal.Player.stopIndex = -1
            else:
                MpGlobal.Player.stopIndex = index
                MpGlobal.Player.stopNext = False;
            MpGlobal.Window.tbl_playlist.FillTable()
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