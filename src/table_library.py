

import math 
import sys
import os  

import widgetTable
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from MpGlobalDefines import *
from MpSong import Song
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from MpSearch import *
from MpCommands import *


class TableLibrary(widgetTable.Table):
    widthA = 100; #On Resize check these for percents, auto scaling of these regions
    widthT = 100; #sum these and divide out each for a scale  
    widthB = 100;
    brush_highlight1 = QBrush(QColor(255,255,0,32))
    brush_special = QBrush(QColor(255,0,0,32))
    
    brush_text_default  = QBrush(QColor(  0,  0,  0)) 
    brush_text_ready  = QBrush(QColor(180, 10,  5)) 
    brush_text_recent = QBrush(QColor(5, 10,  180)) 

    # the MpMusic Constant associated with each column
    
    col_id_template = [MpMusic.PLAYCOUNT, \
              MpMusic.ARTIST, \
              MpMusic.TITLE, \
              MpMusic.ALBUM, \
              MpMusic.LENGTH, \
              MpMusic.RATING, \
              MpMusic.GENRE, \
              MpMusic.FREQUENCY, \
              MpMusic.DATESTAMP, \
              MpMusic.FILESIZE, \
              MpMusic.SKIPCOUNT, \
              MpMusic.COMMENT,\
              MpMusic.SONGINDEX,\
              MpMusic.SONGID,
              MpMusic.PATH];
              
    col_id = col_id_template[:]
                                    
    col_title = {MpMusic.PLAYCOUNT: "#", \
                 MpMusic.ARTIST   : "Artist", \
                 MpMusic.TITLE    : "Title", \
                 MpMusic.ALBUM    : "Album", \
                 MpMusic.LENGTH   : "Length", \
                 MpMusic.RATING   : "Rating", \
                 MpMusic.GENRE    : "Genre", \
                 MpMusic.FREQUENCY: "Frequency", \
                 MpMusic.DATESTAMP: "Last Played", \
                 MpMusic.FILESIZE : "File Size", \
                 MpMusic.SKIPCOUNT: "Skip Count", \
                 MpMusic.COMMENT  : "Comment", \
                 MpMusic.SONGINDEX: "Album Index", \
                 MpMusic.PATH     : "File Path", \
                 MpMusic.SONGID   : "ID"};          
       
    def __init__(self,col_list=[],col_active=-1,parent=None):
      
        header = [];
        

        try: 
            # TODO this code just looks bad,
            # however the col_id comes from user input, and needs to be of type integer.
            if len(col_list) == len(self.col_id_template):
                self.col_id = col_list[:]
            for x in range(len(self.col_id)):
                if self.col_id[x] in self.col_id_template:
                    self.col_id[x] = int(self.col_id[x])
                else:
                    raise Exception("Users are always right!")
        except:
            self.col_id = self.col_id_template[:]
          
            
        if col_active < 0 or col_active > len(self.col_id):
            col_active = len(self.col_id)
            
        for i in range(col_active):
            header.append( self.col_title[ self.col_id[i] ] )    
         
        super(TableLibrary,self).__init__(parent,header)
        self.table.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDragType("dragFromLibrary")
        self.setDragReceiveType("None")
        
        h = self.table.horizontalHeader();
        h.setSortIndicatorShown(True)
        self.table.horizontalHeader().setSortIndicator(1,False) 
        
        self.resizeColumn()
        self.table.setObjectName("table_Library")

    def FillTable(self,offset=-1):    
        """fill the table with data, starting at index offset, from the Display Array"""
        R = []
        k=0;
        if offset < 0 :
            offset = self.scrollbar.value()
            
            
        #offset = max(0,offset)
        #TODO ERROR WITH READING VALUE, set signal to whatch for when offset is set
        #assert offset >= 0, "OFFSET READ ERROR m:%d M:%d v:%d"%(self.scrollbar.minimum(),self.scrollbar.maximum(),self.scrollbar.value())
        #if (selfta == None):
        #    return
        size = len(self.data) # in case size is zero, prevent any drawing to it
        #self.table.setModel(None);
        
        #print self.event_proc
        
        self.event_proc = True
        
        for i in range(self.rowCount):
            k = i+offset; # the k'th element of the data array
            
            if k < len(self.data) and size > 0:
                R = self.FillRow(k)
                brush = self.FillRowColor(k)
                
                # set a color for the current song
                qFG_text_color = self.brush_text_default;
                if self.data[k] == MpGlobal.Player.CurrentSong:
                    qFG_text_color = self.brush_text_recent;
                
                
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),R[j])
                    self.model.setData(self.model.index(i,j),qFG_text_color,Qt.ForegroundRole)   
                    self.model.setData(self.model.index(i,j),brush,Qt.BackgroundRole)
 
                date = self.data[k][MpMusic.DATEVALUE]
                
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.PLAYCOUNT)),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.LENGTH   )),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.RATING   )),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.FREQUENCY)),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.SONGINDEX)),Qt.AlignRight,Qt.TextAlignmentRole)

                datecol = self.col_id.index(MpMusic.DATESTAMP)
                
                if date < MpGlobal.LaunchEpochTime:
                    self.model.setData(self.model.index(i,datecol),self.brush_text_ready,Qt.ForegroundRole)
                elif date > MpGlobal.RecentEpochTime:
                     self.model.setData(self.model.index(i,datecol),self.brush_text_recent,Qt.ForegroundRole)
                else:
                    self.model.setData(self.model.index(i,datecol),self.brush_text_default,Qt.ForegroundRole)

            else:
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),"")
                    self.model.setData(self.model.index(i,j),self.brush_default,Qt.BackgroundRole) 
                    
        self.event_proc = False
        #highlight the current song
        
                             
                    
        #self.table.setModel(self.model);
        # TODO REMOVE THIS
        # self.table.resizeColumnToContents(self.col_id.index(MpMusic.PATH))
        
        return;
        
    def FillRow(self,index):
        R = [""]*len(self.col_id);
        R[self.col_id.index(MpMusic.PLAYCOUNT)] = self.data[index][MpMusic.PLAYCOUNT]
        R[self.col_id.index(MpMusic.ARTIST)]    = self.data[index][MpMusic.ARTIST]
        R[self.col_id.index(MpMusic.TITLE)]     = self.data[index][MpMusic.TITLE]
        R[self.col_id.index(MpMusic.ALBUM)]     = self.data[index][MpMusic.ALBUM]
        R[self.col_id.index(MpMusic.LENGTH)]    = convertTimeToString(self.data[index][MpMusic.LENGTH])
        R[self.col_id.index(MpMusic.RATING)]    = self.data[index][MpMusic.RATING]
        R[self.col_id.index(MpMusic.GENRE)]     = self.data[index][MpMusic.GENRE]
        R[self.col_id.index(MpMusic.FREQUENCY)] = self.data[index][MpMusic.FREQUENCY]
        R[self.col_id.index(MpMusic.DATESTAMP)] = self.data[index][MpMusic.DATESTAMP]
        R[self.col_id.index(MpMusic.FILESIZE)]  = self.data[index][MpMusic.FILESIZE]
        R[self.col_id.index(MpMusic.SKIPCOUNT)] = self.data[index][MpMusic.SKIPCOUNT]
        R[self.col_id.index(MpMusic.COMMENT)]   = self.data[index][MpMusic.COMMENT]
        R[self.col_id.index(MpMusic.PATH)]      = self.data[index][MpMusic.PATH]
        R[self.col_id.index(MpMusic.SONGID)]    = str(self.data[index].id)
        R[self.col_id.index(MpMusic.SONGINDEX)] = self.data[index][MpMusic.SONGINDEX]
        return R
        
    def FillRowColor(self,index):
        if index in self.selection:
            if self.table.hasFocus() :
                return self.brush_selected
            else:
                return self.brush_selectedOOF
        elif self.data[index][MpMusic.SPECIAL] :
            return self.brush_special
        elif self.data[index][MpMusic.SELECTED] :
            return self.brush_highlight1
        else:   
            return self.brush_default
   
    def columnClicked(self,col):
        # create a list of columns, selecting the clicked one.
        id = self.col_id[col]
        # sort the library by the clicked column 
   
        self.sortColumnByEXIF(id)
        # perform a search and update the table
        MpGlobal.Window.tbl_library.updateDisplay()
        
        
        #MpGlobal.Window.tbl_library.UpdateTable(0,MpGlobal.Player.libDisplay) 
        # allow alternating clicks to flip the sort direction
        # lastSortType is set in the sort functions
        return;
        
    def sortColumnByEXIF(self,exifTag):
    
        i = 1;
        
        if exifTag in (MpMusic.ARTIST, MpMusic.TITLE,MpMusic.ALBUM, MpMusic.GENRE, MpMusic.COMMENT, MpMusic.PATH, MpMusic.SONGID):
            dir = MpGlobal.Player.lastSortType==exifTag
            i = 0;
        else:
            dir = MpGlobal.Player.lastSortType!=exifTag
            i = 1;
        
        if exifTag in (MpMusic.DATESTAMP,MpMusic.DATEVALUE):
            i = 2;
        # string: #-A-Z-a, a-Z-A-#
        # number: increasing, decreasing
        # date  : Recent First | Recent Last
        
        t_txt  =    (u"#-A-Z-\u3042" , u"\u3042-Z-A-#"), \
                    (u"Increasing"   , u"Decreasing"  ), \
                    (u"Not Recent First" , u"Recent First" ), \
        
        dir_text = t_txt[i][1] if dir else t_txt[i][0]

        if exifTag in self.col_id:
            self.table.horizontalHeader().setSortIndicator(self.col_id.index(exifTag),dir)  
        
        sortLibraryInplace(exifTag,dir)   

        
        UpdateStatusWidget(3,"sorted by %s - %s"%(MpMusic.exifToString(exifTag),dir_text))
            
    def resizeColumn(self):
        self._resizeColumn(self.col_id.index(MpMusic.PLAYCOUNT), 35)
        self._resizeColumn(self.col_id.index(MpMusic.ARTIST)   ,150)
        self._resizeColumn(self.col_id.index(MpMusic.TITLE)    ,200)
        self._resizeColumn(self.col_id.index(MpMusic.ALBUM)    ,150)
        self._resizeColumn(self.col_id.index(MpMusic.LENGTH)   , 50)
        self._resizeColumn(self.col_id.index(MpMusic.RATING)   , 50)
        self._resizeColumn(self.col_id.index(MpMusic.GENRE)    ,100)
        self._resizeColumn(self.col_id.index(MpMusic.FREQUENCY), 75)
        self._resizeColumn(self.col_id.index(MpMusic.DATESTAMP),130)
        self._resizeColumn(self.col_id.index(MpMusic.FILESIZE) ,130)
        self._resizeColumn(self.col_id.index(MpMusic.SKIPCOUNT),100)
        self._resizeColumn(self.col_id.index(MpMusic.COMMENT)  ,130)
        self._resizeColumn(self.col_id.index(MpMusic.PATH)     ,500)
        
    def _resizeColumn(self,index,size):
        if index < self.colCount:
            self.table.setColumnWidth(index,size)
            
    def DoubleClick(self,item):
        R = self.getSelection()
        if len(R) > 0 :
            index = MpGlobal.Player.CurrentIndex + 1
            MpGlobal.Player.playList = MpGlobal.Player.playList[:index] + R + MpGlobal.Player.playList[index:]
            UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
            MpGlobal.Window.tbl_playlist.data = MpGlobal.Player.playList
            MpGlobal.Window.tbl_playlist.UpdateTable(MpGlobal.Window.tbl_playlist.getDisplayOffset(),MpGlobal.Player.playList)
        return
        
    def leftReleaseEvent(self,item,event):
        super(TableLibrary,self).leftReleaseEvent(item,event)

        _row = self.itemToIndex(item)
        if 0 <= _row < len(self.data):
            UpdateStatusWidget(3,self.data[_row][MpMusic.PATH])
            
    def rightClickEvent(self,event):
        
        item = self.table.indexAt(event.pos())
        row = item.row() + self.getDisplayOffset()
            
        if len(self.selection) > 0 and row < len(self.data):

            # modify the context menu based on click context
            contextMenu = QMenu(self.table)
            
            
            contextMenu.addSeparator()
            if len(self.selection) == 1:
                contextMenu.addAction("Add Song to Pool",self.__Action_addSelectionToPool)
                
                contextMenu.addAction("Edit Song",self.__Action_editSong__)
                contextMenu.addAction("DELETE Song",self.__Action_deleteSingle)
            
            else:
                contextMenu.addAction("Add Selection to Pool",self.__Action_addSelectionToPool)
                contextMenu.addAction("Edit Songs",self.__Action_editSong__)
                
            contextMenu.addAction("Explore Containing Folder",self.__Action_Explore__)
            
            contextMenu.addSeparator()
            
            contextMenu.addAction("Select Columns",self.__Action_ColumnSelect)
            
            contextMenu.addSeparator()
            contextMenu.addMenu(MpGlobal.Window.menu_Sort)
            
            
            action = contextMenu.exec_( event.globalPos() )

            info_UpdateCurrent()
    
    def keyPressEvent(self,event):
        
        _shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier
        _ctrl = event.modifiers()&Qt.ControlModifier ==  Qt.ControlModifier
        if event.key() == Qt.Key_Up:
            self.__keyboard_scroll_UP__();
            R = list(self.selection)
            if len(R) > 0:
                UpdateStatusWidget(3,self.data[R[0]][MpMusic.PATH])

        elif event.key() == Qt.Key_Down:
            self.__keyboard_scroll_DOWN__();
            R = list(self.selection)
            if len(R) > 0:
                UpdateStatusWidget(3,self.data[R[0]][MpMusic.PATH])
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            # on key press of return add to the playlist the songs found in the selection
            #TODO CALL doubleclick event 
            R = self.getSelection()
            if len(R) > 0 :
                index = MpGlobal.Player.CurrentIndex + 1
                MpGlobal.Player.playList = MpGlobal.Player.playList[:index] + R + MpGlobal.Player.playList[index:]
                UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
                MpGlobal.Window.tbl_playlist.data = MpGlobal.Player.playList
                MpGlobal.Window.tbl_playlist.UpdateTable(MpGlobal.Window.tbl_playlist.getDisplayOffset(),MpGlobal.Player.playList)
        elif _ctrl and event.key() == Qt.Key_A:
            self.selection = set(range(len(self.data)));
            self.UpdateTable(-1);         
        
        elif not _shift and not _ctrl:
            MpGlobal.Window.txt_searchBox.setFocus()
            MpGlobal.Window.txt_searchBox.keyPressEvent(event)
    
    def updateDisplay(self,string = None):
        """
            convenience method for calling a new search.
        """
        searchText = MpGlobal.Window.txt_searchBox.displayText()
        
        if string != None:
            MpGlobal.Window.txt_searchBox.setText(string)
            searchText = string
            
        txtSearch_OnTextChange(searchText);

    def setColumnIDList(self,id_list,count):
        self.col_id = id_list;
        self.setColumnCount(count); # count = number of active columns
        self.FillTable()
              
    def setColumnCount(self,count):   
    
        header = [];
        for i in range(count):
            header.append( self.col_title[ self.col_id[i] ] )
            
        self.colCount = len(header)
        
        self.model.setColumnCount(count)
        self.model.setHorizontalHeaderLabels( header );
        
        self.resizeColumn();    # for each column set default sizes

    def __Action_editSong__(self):

        dialog = dialogSongEdit.SongEditWindow(MpGlobal.Window)

        dialog.initData(self.getSelection())
        
        dialog.exec_()
        
        del dialog
        
        self.FillTable()
    def __Action_Explore__(self):
        sel = self.getSelection()
        path = fileGetPath(sel[0][MpMusic.PATH])
        MpGlobal.Window.tbl_explorer.__load_Directory__(path)
        MpGlobal.Window.tabMain.setCurrentIndex(MpGlobal.Window.tab_Explorer)
    def __Action_addSelectionToPool(self):
        R = list(self.selection)
        for i in R:
            if self.data[i][MpMusic.SELECTED] == False:
                self.data[i][MpMusic.SELECTED] = True;
                MpGlobal.Player.selCount += 1;
                
        #MpGlobal.Player.selCount = len(Global.Player.library)   
        self.UpdateTable(-1);         

                
        UpdateStatusWidget(0,MpGlobal.Player.selCount) 
    def __Action_deleteSingle(self):
        R = self.getSelection()
        if len(R) == 1:
            message = "Are you sure you want to delete this song?\n"
            message += R[0][MpMusic.ARTIST] + " - " + R[0][MpMusic.TITLE]
            
            msgBox = QMessageBox(MpGlobal.Window)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(message)
            #    "Delete Song Confirmation", message,
             #   QMessageBox.NoButton, self)
            msgBox.addButton("Delete", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            
            if msgBox.exec_() == QMessageBox.AcceptRole:            
                MpGlobal.Player.libDelete.append( R[0] )
                MpGlobal.Player.library.remove(R[0])
                MpGlobal.Window.tbl_library.updateDisplay()
                Player_set_unsaved();
    def __Action_ColumnSelect(self):

        obj = MpGlobal.Window.tbl_library
        
        R = [0]*len(obj.col_id)
        
        #translate id numbers to strings
        for i in range(len(R)):
            R[i] = MpMusic.exifToString(obj.col_id[i])
        
        # create the dialog with the new string list
        dialog = dialogColumnSelect.DialogColumnSelect(R,obj.colCount)

        if dialog.exec_():
            #print dialog.ResultList   
            #print dialog.ActiveCount
            # clear colors for the dat col, in case the date col has moved
            j=self.col_id_template.index(MpMusic.DATESTAMP);
            for i in range(self.rowCount):
                self.model.setData(self.model.index(i,j),self.brush_text_default,Qt.ForegroundRole)   
                    
            # retranslate to id numbers
            for i in range(len(R)):
                R[i] = MpMusic.stringToExif(dialog.ResultList[i])
            
            self.setColumnIDList(R,dialog.ActiveCount)
            
            self.resizeColumn()
        