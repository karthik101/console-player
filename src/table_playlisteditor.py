
import math 
import sys
import os  

import widgetTable
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *

class TablePLEditor(widgetTable.HPageTable):
    """ a table element that is linked with another similar table"""
    oTable = None
    oDataSrc = None # the other array of data
    DataSrc = None  # source for data
                    # data is therefore the display array
    DataSize = 0;
    objectList = None
    textEdit = None
    
    isRight = False
    
    lastSearch = 0;
    
    def __init__(self,parent,dragType="Unkown",DragReceive="None"):
        header = ("Artist","Title","Album")
        super(TablePLEditor,self).__init__(parent,header)
        self.setDragType("dragTableEditor_"+dragType)
        self.setDragReceiveType("dragTableEditor_"+DragReceive)
        
    def setTables(self,o):
        self.oTable = o # the other table in the set of 2
    def setTextEdit(self,o):
        self.textEdit = o # the text editor
    def setDataSrc(self,o):
        self.DataSrc = o # the array of data.
    def setOtherDataSrc(self,o):
        self.oDataSrc = o # the array of data.
    def setObjectList(self,o):
        self.objectList = o # the array of data.
        
    def dropEvent(self,event,row):
        if event.mimeData().hasText == False :
            return;
        if event.mimeData().text() not in self.dragReceive :
            return; # make sure that the drag is of valid type
          
        self.moveDataFromSibling()
        
        offset = self.oTable.getDisplayOffset()
        if offset == self.oTable.scroll_MaxRange:
            offset -= 1
                
        self.oTable.UpdateTable(offset)
            
        
    def keyReleaseEvent(self,event):
        if self.isRight :
            if event.key() == Qt.Key_Delete :
                self.oTable.moveDataFromSibling()
                
                offset = self.getDisplayOffset()
                if offset == self.scroll_MaxRange:
                    offset -= 1
                        
                self.UpdateTable(offset)
                
    
    def columnClicked(self,col):
        # create a list of columns, selecting the clicked one.
        id = (
             MpMusic.ARTIST, \
             MpMusic.TITLE, \
             MpMusic.ALBUM )[col]
             
        dir = self.lastSearch == col   

        self.table.horizontalHeader().setSortIndicator(col,dir)  
        
        sortList(self.DataSrc,id,dir)
        # perform a search and update the table

        if self.lastSearch == col:
            self.lastSearch = -1;
        else:
            self.lastSearch = col
        
        self.runSearchUpdate(self.objectList[1].text())

    
    def moveDataFromSibling(self):
        """
            Take the selected elements from the sibling table 
            remove them from that table and add them to the data in this table
            Sort this tables data, and redisplay both tables
        """
        sel = self.oTable.getSelection()
        listRemoveElements(self.oTable.DataSrc,sel)
        self.DataSrc += sel
        
        sortList(self.data,MpMusic.ARTIST)
        
        self.oTable.selection = set()
        self.selection = set()
        
        self.runSearchUpdate(self.textEdit.displayText())
        self.oTable.runSearchUpdate(self.textEdit.displayText())

        tl = self.objectList[2] 
        tr = self.objectList[3] 

        tr.DataSize = 0    
        for item in tr.DataSrc:
            tr.DataSize += item[MpMusic.FILESIZE]
        tr.DataSize /= 1024 # to mB 
        
        UpdateStatusWidget(3,"%s %s FileSize: %dMB"%(len(tl.data),len(tr.data),tr.DataSize))
        
    def FillRow(self,index):
        R = [""]*self.colCount;
        R[0] = self.data[index][MpMusic.ARTIST]
        R[1] = self.data[index][MpMusic.TITLE]
        R[2] = self.data[index][MpMusic.ALBUM]
        return R
    
    def runSearch(self,text):
        if text == "" :
            self.data = self.DataSrc
        else:
            so = SearchObject(text)
            self.data = so.search(self.DataSrc)
            
           
        
    def runSearchUpdate(self,text):
        self.runSearch(text)
        self.UpdateTable(self.getDisplayOffset(),self.data)
    
    """
        The Following are private methods and act as a place for a new tab
        to contain functions.
    """
    
    def __text_edit__(self,text):
        """ private method
            this acts as the only place that a text edit box can be hooked up to
            this table, and the other table. Because there are two tables
            the lineedit needs to be hooked up to one of the copies of this function
        """
        # clear the selection
        self.selection = set()
        self.oTable.selection = set()
        # reset the view to the top
        self.setDisplayOffset(0)
        self.oTable.setDisplayOffset(0)
        
        self.runSearchUpdate(text)
        self.oTable.runSearchUpdate(text)
        
        tl = self.objectList[2] 
        tr = self.objectList[3]  
        
        tr.DataSize = 0    
        for item in tr.DataSrc:
            tr.DataSize += item[MpMusic.FILESIZE]
        tr.DataSize /= 1024 # to mB 
        
        UpdateStatusWidget(3,"%s %s FileSize: %dMB"%(len(tl.data),len(tr.data),tr.DataSize))
        
    def __btn_load__(self,bool=False):
        
        tab   = MpGlobal.Window.tabMain
        index = tab.currentIndex()
        
        path = QFileDialog.getOpenFileName(MpGlobal.Window,
                "Open Playlist File",
                MpGlobal.installPath+"playlist/",
                "M3U Files (*.playlist)")
                
        tl = self.objectList[2] 
        tr = self.objectList[3] 
        
        R = MpGlobal.Player.library[:]
        # get the list of songs
        # remove those songs from the left display list
        if path != "":
            index,S = playListLoad(path,R) # index is ignored
            listRemoveElements(R,S)
            # update the data pools
            tl.DataSrc = R
            tr.DataSrc = S
            
            # set the name of the tab

            self.objectList[0] = fileGetName(path)
            MpGlobal.Window.tabMain.setTabText(index,self.objectList[0])
            tl.runSearchUpdate("")
            tr.runSearchUpdate("")
            return True
        else:
            return False
            
        UpdateStatusWidget(3,"%s %s FileSize: %dMB"%(len(tl.data),len(tr.data),tr.DataSize))

    def __btn_save__(self,bool=False):
        
        tab   = MpGlobal.Window.tabMain
        index = tab.currentIndex()
        
        path = QFileDialog.getSaveFileName(MpGlobal.Window,
                "Save Playlist File",
                MpGlobal.installPath+"playlist/",
                "M3U Files (*.playlist)")
                
        tl = self.objectList[2] 
        tr = self.objectList[3] 
        if path != "":
            playListSave(path,tr.DataSrc) 
            self.objectList[0] = fileGetName(path)
            MpGlobal.Window.tabMain.setTabText(index,self.objectList[0])
            return True
        else:
            return False
    
    def __btn_close__(self,bool=False):
        tab   = MpGlobal.Window.tabMain
        tabbar = tab.tabBar();
        #index = tab.currentIndex()
        index = -1;
        for i in range(tab.count()):
            if tabbar.tabData(i) == self:

                index = i;
        if index == -1:
            return;
        #index = self.objectList[4]
        #object = [name,edit,tbl_left,tbl_rite,index,pagem,splitter]
        # remove self from the list of open editors
        for x in range(len(MpGlobal.Window.editorTabs)):
            if MpGlobal.Window.editorTabs[x] == self.objectList:
                MpGlobal.Window.editorTabs.pop(x)
                break
        
        del self.objectList[0]
        del self.objectList[1]
        del self.objectList[2]
        del self.objectList[3]
        #del self.objectList[5]
        #del self.objectList[6]
                
        del self.DataSrc
        del self.data
        self.objectList  = None;
        
        del self.oTable.DataSrc
        del self.oTable.data
        self.oTable.objectList = None
        
        MpGlobal.Window.tabMain.removeTab(index)

    def __btn_play__(self,bool=False):
        
        for song in self.objectList[3].DataSrc:
            if song[MpMusic.SELECTED] == False :
                MpGlobal.Player.selCount += 1
                song[MpMusic.SELECTED] = True
        UpdateStatusWidget(0,MpGlobal.Player.selCount)    
        registerNewListAsPlayList(self.objectList[3].DataSrc,autoLoad = True)




from Song_Object import Song
from Song_PlaylistFormat import *
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from MpSearch import *
from MpCommands import *

from MpApplication import *        