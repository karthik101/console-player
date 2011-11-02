        
        
import math 
import sys
import os    

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from MpGlobalDefines import *

import widgetTable
from MpScripting import *
from MpSort import *
from MpSearch import *
from MpCommands import *

        
class TableQuickSelect(widgetTable.Table):
    """
        Quick Selection
        
        The quick selection tab allows you to select from the list of artists in your library. It also allows you to view statistics on each artist, and sort the list by these values.
        
        \\<table\\>
        Song Count | Displays the number of songs by that artist
        Playcount  | Displays the number of plays for that artist, equal to the sum of all plays of songs by that artist.
        Play Time  | Displays how long it would take to listen to each song by an artist once.
        Listen Time| This is the sum of Playcount * Length for each song by an artist
        Frequency  | This is the average frequency for all songs by the artist
        Rating Count | The sum of rated values for each song
        Count of Ratings | the number of songs rated by an artist
        \\</table\\>
        
        By clicking "Create" a new playlist will be made from the artists selected.
        
        By default an artist only appears in the list if there are at least 2 songs by that artist.
        
        use the build command to change the minimum value of songs per artist, "build 6" will set the minimum song count to 6.
    """
    dispElement = 3
    brush_selected = QBrush(QColor(0,205,25,255)) 
    brush_selectedOOF = QBrush(QColor(0,205,25,128)) 
    
    brush_text_default  = QBrush(QColor(  0,  0,  0)) 
    brush_text_favorite = QBrush(QColor(180, 10,  5)) 
    
    cbox1 = None;
    cbox2 = None;
    cbox3 = None;
    sbox1 = None;
    
    c_size = 90

    display_policy = 3
    
    artindex = 0
    selindex = 1
    favindex = 2
    
    mrange = 25

    def __init__(self,parent):
        header = ("Data","Artist","Data","Artist","Data","Artist")
        super(TableQuickSelect,self).__init__(parent,header)
        self.table.horizontalHeader().hide()
        
        self.table.setColumnWidth(0,self.c_size)  
        self.table.setColumnWidth(2,self.c_size)  
        self.table.setColumnWidth(4,self.c_size)  
        
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.table.setDragDropMode(QAbstractItemView.DragOnly)
        self.table.setObjectName("table_Quick")
    def calc_mrange(self):
        self.mrange = math.ceil(len(self.data) / float(self.display_policy))
    
    def UpdateTable(self,offset=0,array=None):
    
        self.calc_mrange()
        self.display_policy = self.getDisplayPolicy()
        super(TableQuickSelect,self).UpdateTable(offset,array)

    def adustScrollBar(self,offset=-1):
        
        if offset == -1:
            offset = self.scrollbar.value()
        self.scroll_MaxRange = max(0,self.mrange - self.rowCount + 4) 
        self.scrollbar.setMaximum(self.scroll_MaxRange)
        self.scrollbar.setPageStep(self.rowCount)
        self.scrollbar.setValue(offset)
        
        assert self.scrollbar.value() >= 0, "OFFSET WRITE ERROR m:%d M:%d v:%d"%(self.scrollbar.minimum(),self.scrollbar.maximum(),self.scrollbar.value())
    
    
    def FillTable(self,offset=-1):    
        """fill the table with data, starting at index offset, from the Display Array"""
        # mrange is the max range for the current width
        self.calc_mrange()

        if offset < 0 :
            offset = self.scrollbar.value()
        else:
            self.scrollbar.setValue(offset)
            
        size = len(self.data) # in case size is zero, prevent any drawing to it
        
        
        
        #S = [self.data,];
        # collect the data to be displayed into rows based off of the display policy
        _size = len(self.data)/self.display_policy
        #_size = self.display_policy + len(self.data)/self.display_policy - 1;
        
        S = [None]*(_size+1)
        # initialize the display array with empty lists
        for i in range(len(S)):
           S[i] = []
        # finally, add the data to the display list
        for i in range(len(self.data)):
            S[i%(_size+1)].append(self.data[i])
            #if self.data[i][0] == u"K-On!": # debug K-on was on a fringe border case thingy
            #    print size,_size,i;
                   
        for i in range(self.rowCount):
            k = i+offset; # the k'th element of the data array
            
            if k < self.mrange+1 and 0 <= k < _size+1:
                
                self.b1 = self.brush_default
                self.b2 = self.brush_default
                self.b3 = self.brush_default
                
                self.c1 = self.brush_text_default
                self.c2 = self.brush_text_default
                self.c3 = self.brush_text_default
                
                R = self.FillRow(S,k) # returns formatted data for the table

                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),R[j])
                    
                #if self.dispElement in (4,5):
                self.model.setData(self.model.index(i,0),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,2),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,4),Qt.AlignRight,Qt.TextAlignmentRole)
                #else:
                #    self.model.setData(self.model.index(i,0),Qt.AlignLeft,Qt.TextAlignmentRole)
                #    self.model.setData(self.model.index(i,2),Qt.AlignLeft,Qt.TextAlignmentRole)
                #    self.model.setData(self.model.index(i,4),Qt.AlignLeft,Qt.TextAlignmentRole)
                
                
                self.model.setData(self.model.index(i,0),self.b1,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,1),self.b1,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,2),self.b2,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,3),self.b2,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,4),self.b3,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,5),self.b3,Qt.BackgroundRole)
                
                self.model.setData(self.model.index(i,1),self.c1,Qt.ForegroundRole)
                self.model.setData(self.model.index(i,3),self.c2,Qt.ForegroundRole)
                self.model.setData(self.model.index(i,5),self.c3,Qt.ForegroundRole)
                
            else:
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),"")
                    self.model.setData(self.model.index(i,j),self.brush_default,Qt.BackgroundRole)

    def FillRow(self,data,index):

        p = self.display_policy
        r = len(self.data)
        s = r/self.display_policy

        if index >= len(data):
            return ["","","","","",""]
            
        data = data[index]   # to confuse you
        size = len(data)
        
        if size == 0:
            return ["","","","","",""]
            
        str1 = self.itemToString(data[0])
        str2  = ""
        str3  = ""
        
        str1a = data[0][0]
        str2a = ""
        str3a = ""
        
        if data[0][self.selindex]: self.b1 = self.brushSelectionColor();
        if data[0][self.favindex]: self.c1 = self.brush_text_favorite
           
        if size > 1:
            str2 = self.itemToString(data[1])
            str2a = data[1][0]
            if data[1][self.selindex]: self.b2 = self.brushSelectionColor();
            if data[1][self.favindex]: self.c2 = self.brush_text_favorite
        if size > 2:
            str3 = self.itemToString(data[2])
            str3a = data[2][0]
            if data[2][self.selindex]: self.b3 = self.brushSelectionColor();
            if data[2][self.favindex]: self.c3 = self.brush_text_favorite
  
        return [str1,str1a,str2,str2a,str3,str3a]

    def itemToString(self,item):
        """
            convert a index in the display data
            to a formatted string for display
        """
        
        if self.dispElement in (5,6):
            return "%s"%convertTimeToString(item[self.dispElement])
        else:
            return "%d"%item[self.dispElement]
    
    def indexElementToString(self,index):
        """
            convert a index in the display data
            to a formatted string for display
        """
        
        if self.dispElement in (5,6):
            return "%s "%convertTimeToString(self.data[index][self.dispElement])
        else:
            return "%d"%self.data[index][self.dispElement]
          
    def leftPressEvent(self,item,event): 
    
        offset = self.getDisplayOffset()
        
        row = item.row()
        col = item.column()
        
        i = self.positionToIndex(col,row)

        if i < len(self.data):
            self.data[i][1] = not self.data[i][1]
        
    def leftReleaseEvent(self,item,event):
        s = self.calc_hvalue();  
        UpdateStatusWidget(3,"Playlist Length: %d. Maximum Songs per Artist: %d."%(MpGlobal.PLAYLIST_SIZE,s))
        self.FillTable()
       
    def rightClickEvent(self,event):
    
        item = self.table.indexAt(event.pos())
        
        if item.row() >= 0:
            row = item.row()
            col = item.column()
            
            i = self.positionToIndex(col,row)
            if i < len(self.data):
                R = self.data[i][:]
                if not self.data[i][self.favindex] :
                    Settings.FAVORITE_ARTIST.append(R[0])
                    self.data[i][self.favindex] = True
                else:
                    for j in range(len(Settings.FAVORITE_ARTIST)):
                        if Settings.FAVORITE_ARTIST[j] == R[0]:
                            Settings.FAVORITE_ARTIST.pop(j)
                            break
                    self.data[i][self.favindex] = False
                #string = ""
                #for artist in Settings.FAVORITE_ARTIST:
                #    string += "%s, "%artist.encode('unicode-escape')
                #debug( string )
                self.FillTable()
            
    def calc_hvalue(self):
        s = 0
        for i in self.data:
            if i[self.selindex]:
                s+=1;
                
        if (s>1):
            s = 1 + MpGlobal.PLAYLIST_SIZE/s;  
        elif s==1:
            s =  MpGlobal.PLAYLIST_SIZE/s;
        else:
            s =  MpGlobal.PLAYLIST_SIZE;
            
        return s;
    
    def clearSelection(self):
        UpdateStatusWidget(3,"");
        for data in MpGlobal.Player.quickList:
            data[1] = False
        self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.quickList)
   
    def newPushed(self):
        s = self.calc_hvalue();
            
        processTextInput("new -h %d -p" % (s)) # this is called 'efficient'
    def __CBOX_CHANGE_DISPLAY__(self,index):
        self.dispElement = index + 3
        #print self.dispElement
        self.FillTable()
    def __CBOX_SORT_DISPLAY__(self,index=-1):
        
        value = self.cbox3.checkState() == Qt.Checked
        
        if index != 0:
            index += 2
        if index not in (0,7):
            value = not value
        #print self.data[0][index]
        if index == self.artindex:
            k = lambda song: sort_parameter_str(song,index)
        else:    
            k = lambda song: song[index]

        MpGlobal.Player.quickList.sort(key = k, reverse=value )
        
        self.FillTable()
        #self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.quickList)
        
    def __CHECK_STATE_CHANGE__(self,checkState):
        self.__CBOX_SORT_DISPLAY__(self.cbox2.currentIndex())
    
    def __SBOX_Value_Changed__(self,value):
        MpGlobal.PLAYLIST_GUI_MINIMUM_RATING = value
    
    def resizeEvent(self,event):
        self.resize_Column()
        #(self.display_policy - 1) + 
        self.calc_mrange()
        
        newmax = max(0,self.mrange - int(self.rowCount-2))
        
        self.scrollbar.setMaximum(newmax)
        
    def resize_Column(self):
        #w1 = self.table.columnWidth(0)
        w2 = self.table.width()
        
        self.display_policy = self.getDisplayPolicy()
        p = self.display_policy
        
        if p == 3:
            w2 = max( (w2-(self.c_size*3))/3,self.c_size*2)
        elif p == 2:
            w2 = max( (w2-(self.c_size*2))/2,self.c_size*2)
        else:
            w2 = max( w2-self.c_size,self.c_size*2)
            
        self.table.setColumnWidth(1,w2)  
        self.table.setColumnWidth(3,w2)  
        self.table.setColumnWidth(5,w2) 
        
    def getDisplayPolicy(self):
        """
            return the number of columns to make visible
            based off of the width of the display
        """
        
        w2 = self.table.width()
        
        # the magic number here, 9 and 6 come from the following
        #   3 (or 2) data display columns at c_size width
        #   3 (or 2) columns for artist name at 2*c_size width)
        
        if w2 > (self.c_size*9):
            return 3
        elif w2 > (self.c_size*6):
            return 2
        else:
            return 1

    def positionToIndex(self,col,row):
        d = self.getDisplayOffset()
        p = self.display_policy
        r = len(self.data)
        s = r/2
        t = r/3 
        
        #print row,col
        
        c = (col / 2)
        
        i = 0
        
        if p == 3 :
            i = t * c + c
        if p == 2 :
            i = s * c + c
        #if c > 0 :
        #    i += 1

        return row + d + i
        
    def indexToPosition(self,pos):
        d = self.getDisplayOffset()
        p = self.display_policy
        r = len(self.data)
        s = r/2
        t = r/3 
        
        col = 0
        row = 0
        
        if p == 3 :
            if pos > 2*t :
                col = 2
                row = pos - 2*t - 1
            elif pos > t:
                col = 1
                row = pos - t - 1
            else:
                col = 0
                row = pos
        elif p == 2 :
            if pos > s:
                col = 1
                row = pos - s - 1
            else:
                col = 0
                row = pos
        else:
            row = pos
        
        
        return (col,row)
      