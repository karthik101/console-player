      
# this file is no longer used
	  
import math 
import sys
import os    

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from MpGlobalDefines import *

import widgetTable
from MpScripting import *
from MpScriptingAdvanced import *
from MpCommands import *
   
class TableExternal(widgetTable.Table):
    def __init__(self,parent):
        header = ("Path",)
        super(TableExternal,self).__init__(parent,header)
        #self.table.setDragDropMode(QAbstractItemView.DragOnly)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    def FillRow(self,index):
        return [self.data[index],]
    def keyReleaseEvent(self,event):
        """
            Delete selected songs from the list of songs
            to load, when the delete key is pressed
        """
        if event.key() == Qt.Key_Delete :
            R = list(self.selection)
            R.sort(reverse = True)
            cindex_flag = False
            for x in R:
                MpGlobal.Player.external.pop(x)
            self.selection = set()
            self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.external)

    def resizeEvent(self,event):
        self.resize_Column()
        
    def resize_Column(self):
        #w1 = self.table.columnWidth(0)
        w2 = self.table.width()
        self.table.setColumnWidth(0,w2-1) 
  