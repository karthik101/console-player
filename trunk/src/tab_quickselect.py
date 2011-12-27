
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

from App_EventManager import *

from tab_base import *

class Tab_QuickSelect(Application_Tab):

    def __init__(self,parent=None):
        super(Tab_QuickSelect, self).__init__(parent)
        
        self.vbox = QVBoxLayout(self)
        
        self.hbox = QHBoxLayout()
        
        self.table = Table_Explorer(self)
        
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.table)
        
        
        
class Table_Explorer(LargeTable):


    def initColumns(self):
        
        self.columns.append( TableColumn_Quick_Data() )
        self.columns.append( TableColumn() )
        
        self.columns.append( TableColumn_Quick_Data() )
        self.columns.append( TableColumn() )
        
        self.columns.append( TableColumn_Quick_Data() )
        self.columns.append( TableColumn() )
    
    
    
class TableColumn_Quick_Data(TableColumn):
    pass
    