
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
"""
definition of data being displayed
S[0] = key
S[1] = False
S[2] = key in Settings.FAVORITE_ARTIST
S[3] = D[key][c_cnt]
S[4] = D[key][c_ply]
S[5] = D[key][c_len]
S[6] = D[key][c_tme]
S[7] = D[key][c_frq] / D[key][c_cnt]
S[8] = D[key][c_rte]
S[9] = D[key][c_rct]
"""
class Tab_QuickSelect(Application_Tab):

    def __init__(self,parent=None):
        super(Tab_QuickSelect, self).__init__(parent)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setMargin(0)
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        
        self.table = Table_Quick(self)
        
        self.vbox.addSpacing(4)
        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addWidget(self.table.container)
        
        self.hbox1.addSpacing(4)
        self.hbox2.addSpacing(4)
        self.__init_status_bar()
        self.hbox1.addSpacing(4)
        self.hbox2.addSpacing(4)
        
        self.sort_index = 0 # 0 or any value larger than 3
        self.sort_direction = 1 # 1 or -1 for inverse
        self.display_index = 3 # which index in the data array to draw
        self.col_count = 2 # takes values 1,2,3
        
        self.playlist_max_artist = 0
        self.playlist_sel_artist = 0
        
        self.data = []
        
        
    
    def __init_status_bar(self):
        """
            add the comboboxes and other widgets to hbox1 and hbox 2
            
        """
        cbox_disp = QComboBox(self) # create a cbox which will choose which information to display
        cbox_sort = QComboBox(self) # create a cbox which will choose which information to sort by
        
        cbox_rev  = QCheckBox("reverse",self)
        
        btn_clear  = QPushButton("Clear",self)
        btn_create = QPushButton("Create",self)
        
        self.hbox1.addWidget(QLabel("Display:",self),alignment=Qt.AlignLeft)
        self.hbox1.addWidget(cbox_disp,stretch=1,alignment=Qt.AlignLeft)
        self.hbox1.addWidget(QLabel("Sort:",self),alignment=Qt.AlignLeft)
        self.hbox1.addWidget(cbox_sort,stretch=1,alignment=Qt.AlignLeft)
        self.hbox1.addWidget(cbox_rev,stretch=1,alignment=Qt.AlignLeft)
        self.hbox1.addWidget(btn_clear,alignment=Qt.AlignRight)
        self.hbox1.addWidget(btn_create,alignment=Qt.AlignRight)
        
        self.hbox2.addWidget(QLabel("Create a new playlist by selecting artists then clicking 'Create'.",self))
        self.lbl_status = QLabel("",self)
        self.hbox2.addWidget(self.lbl_status,alignment=Qt.AlignRight)
        
        cbox_disp.addItem("Song Count")
        cbox_disp.addItem("Play Count")
        cbox_disp.addItem("Play Time")
        cbox_disp.addItem("Listen Time")
        cbox_disp.addItem("Frequency")
        cbox_disp.addItem("Rating Count")
        cbox_disp.addItem("Count of Rated songs")
        
        cbox_sort.addItem("Artist")
        cbox_sort.addItem("Song Count")
        cbox_sort.addItem("Play Count")
        cbox_sort.addItem("Play Time")
        cbox_sort.addItem("Listen Time")
        cbox_sort.addItem("Frequency")
        cbox_sort.addItem("Rating Count")
        cbox_sort.addItem("Count of Rated songs")
        
        btn_clear.clicked.connect(self.click_clear)
        btn_create.clicked.connect(self.click_new)
        
        cbox_rev.stateChanged[int].connect(self.check_reverse)
        
        cbox_disp.currentIndexChanged[int].connect(self.chindex_disp)
        cbox_sort.currentIndexChanged[int].connect(self.chindex_sort)
     
    def switchTo(self):
        self.setStatus()
        self.getData() # sets the data directly
        self.formatData()
     
    def setStatus(self):
        self.setMaxArtist()
        text =""
        if self.playlist_sel_artist <= 1:
            text = "%d/%d selected"%(self.playlist_sel_artist,len(self.data))
        else:
            text = "%d/%d selected. %d songs max from each"%(self.playlist_sel_artist,len(self.data),self.playlist_max_artist)
        self.lbl_status.setText(text)
        
    def setMaxArtist(self):   
        c = 0
        for item in MpGlobal.Player.quickList:
            if item[1] :
                c += 1
                
        if c>1:
            h = 1 + MpGlobal.PLAYLIST_SIZE/c;  
        else:
            h =  MpGlobal.PLAYLIST_SIZE;

        self.playlist_max_artist = h
        self.playlist_sel_artist = c
            
    def sortData(self,index=-1):
        """
            sort the original artist info list using the given rule.
            after this getData, then formatData will need to be called.
        """
        if index >= 0:
            self.sort_index = index

        if self.sort_index == 0:
            g = lambda x: sort_parameter_str(x,0)
        else:
            g = lambda x:x[self.sort_index]
            
        MpGlobal.Player.quickList.sort(key=g,reverse=self.sort_direction==-1)
    
        self.getData() # update
        self.formatData()
    
    def getData(self):
        """
            update the main data table with the artist info
        """
        data = MpGlobal.Player.quickList
        if self.display_index in (5,6):
            self.data = [ (DateTime.formatTimeDelta(item[self.display_index]),item[0]) for item in data ]
        else:
            self.data = [ (item[self.display_index],item[0]) for item in data ]
    
    def formatData(self):  
        """
            using self.data format the data into one,two, or three columns,
            and place it into the table.
        """
        l = self.getDataRowCount()
        d = []
        for i in range(l):
            d.append( ["","","","","",""] )
        for i in range(len(self.data)):
            
            c = i / l # which column to place the item into
            r = i - l*c # which row to place the item into
            
            d[r][ (c*2)     ] = self.data[i][0] # the info to show
            d[r][ (c*2) + 1 ] = self.data[i][1] # the artist name
    
        self.table.setData( d )
    
    def getDataRowCount(self):
        """ the total number of rows needed to display data in columns of 1,2, or 3"""
        return (len(self.data)/self.col_count) + (1 if len(self.data)%self.col_count else 0)
    
    def indexToRowCol(self,index):
        """ for a given index in the self.data list, return the row column for where it would
            be placed in a l-row tall by 3 column grid.
            the actual grid used is l-rows by 6 columns, where each grouping of two columns
            represent the same data: a data value and then the associated artist"""
        l = self.getDataRowCount()
        
        c = index / l # which column to place the item into
        r = index - l*c # which row to place the item into
        
        return (r,c)
        
    def rowColToIndex(self,row,col):
        """
            for a given row and column return the index the item belongs to.
            column should be either 1,2, or 3. as would be returned from indexToRowCol
            dervived from indexToRowCol
        """
        l = self.getDataRowCount()
        i = col*l
        j = row + i
        if j >= len(self.data): return -1 # chance of producing an error for unbalanced lists
        return j
    
    def setSelected(self,index,bool):
        """ set whether the current row should be selected TRUE or not FALSE """
        MpGlobal.Player.quickList[index][1] = bool
        
    def getSelected(self,index):
        """ return the value of the selection for the current row"""
        return MpGlobal.Player.quickList[index][1]

    def setFavorite(self,index,bool):        
        """set whether the indeicated row should be set as a favorite artist TRUE or not FALSE """
        name = MpGlobal.Player.quickList[index][0]
        test = name in Settings.FAVORITE_ARTIST
        
        if bool and not test:
            # insert only if the name does not already exist in the setting
            Settings.FAVORITE_ARTIST.append(name)
            MpGlobal.Player.quickList[index][2] = True
        elif not bool and test:
            # remove only if the value exists
            Settings.FAVORITE_ARTIST.remove(name)
            MpGlobal.Player.quickList[index][2] = False
            
    def getFavorite(self,index):
        """ return whether the current item is favorited"""
        return MpGlobal.Player.quickList[index][2]
    
    def chindex_disp(self,index):
        self.display_index = index+3
        self.getData()
        self.formatData()
        
    def chindex_sort(self,index):

        self.sortData(index if index==0 else index+2)
            
    def click_clear(self,bool=False):
        clearSelection() # clear all selection songs
        for item in MpGlobal.Player.quickList:
            item[1] = False
        self.table.update()
        self.setStatus()
        
    def click_new(self,bool=False):
        clearSelection() # clear all selection songs
        processTextInput("new -h %d -p -t"%self.playlist_max_artist) # this is called 'efficient'
        
    def check_reverse(self,state):
        self.sort_direction = -1 if state else 1
        self.sortData()

class Table_Quick(LargeTable):
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
    def __init__(self,parent=None):
    
        super(Table_Quick, self).__init__(parent)
            
        self.color_fav = QColor(200,0,0)
        self.color_sel = QColor(0,0,200)
        
        self.setAlwaysHideScrollbar(True,False)
        
        self.showRowHeader(False)
        self.setSelectionRule(LargeTable.SELECT_NONE)
        self.showColumnHeader(False)
        
    def setData(self,data):
   
        super(Table_Quick,self).setData(data)
        
        self.color_fav = MpGlobal.Window.style_dict["text_important2"]
        self.color_sel = self.palette_brush(QPalette.Highlight).color()
    
    def resizeEvent(self,event):
        super(Table_Quick, self).resizeEvent(event)
        
        w = self.width()
        p = self.columns[0].width
        m = (QFontMetrics(self.parent.font()).width("A")*20)+4
        _p = p+m # the minimum width for one column
        
        t=1 # set t to the minimum number of columns that could be shown
        for i in range(3,0,-1):
            if w >= _p*i:
                t = i
                break;

        s = ((w/t)-p)+1  # the new width to use 
       
        self.columns[1].width = s
        self.columns[3].width = s
        self.columns[5].width = s
            
        if t != self.parent.col_count:
            self.parent.col_count = t
            self.parent.formatData()
     
    def getRow(self,col,row):
        """
            convert a column and row into an index into the main data
            array
        """
        
        if self.parent.col_count == 2:
            return self.parent.data[row]
        elif self.parent.col_count == 3:
            return self.parent.data[row]
        else:
            return self.parent.data[row]
            
    def mouseReleaseLeft(self,event):
        row,col = self.positionToRowCol(event.x(),event.y())
        index = self.parent.rowColToIndex(row,col/2)
        R = MpGlobal.Player.quickList
        debug( "L col = %d, row = %d, index = %d, artist=%s"%(col/2,row,index,R[index][0]) )
        self.parent.setSelected(index, not self.parent.getSelected(index) )
        self.parent.setStatus()
        return True
     
    def mouseReleaseRight(self,event):
        row,col = self.positionToRowCol(event.x(),event.y())
        index = self.parent.rowColToIndex(row,col/2)
        R = MpGlobal.Player.quickList
        debug( "R col = %d, row = %d, index = %d, artist=%s"%(col/2,row,index,R[index][0]) )
        self.parent.setFavorite(index, not self.parent.getFavorite(index) )
        
    def initColumns(self):
        
        self.columns.append( TableColumn_Quick(self,0, "") )
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setWidthByCharCount(13)
        self.columns.append( TableColumn_Quick(self,1, "") )
        
        self.columns.append( TableColumn_Quick(self,2, "") )
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setWidthByCharCount(13)
        self.columns.append( TableColumn_Quick(self,3, "") )

        self.columns.append( TableColumn_Quick(self,4, "") )
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setWidthByCharCount(13)
        self.columns.append( TableColumn_Quick(self,5, "") )

class TableColumn_Quick(TableColumn):
    
    def __init__(self,parent,index,name=None):
        super(TableColumn_Quick,self).__init__(parent,index,name)

    def paintItem(self,col,painter,row,item,x,y,w,h):   
        col = self.index/2
        index = self.parent.parent.rowColToIndex(row,col)
        
        sel = False
        fav = False
        if index != -1:
            sel = self.parent.parent.getSelected(index) 
            fav = self.parent.parent.getFavorite(index) 

        if sel:
            painter.fillRect(x,y,w,h,self.parent.color_sel)
            
        default_pen = painter.pen()
        
        if fav:
            painter.setPen(self.parent.color_fav)

        self.paintItem_text(col,painter,row,item,x,y,w,h)
    
        painter.setPen(default_pen)
    
    