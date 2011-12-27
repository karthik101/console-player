import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

isPosix = os.name == 'posix'

from widgetLineEdit import LineEdit
from widgetLargeTable import *
from Song_Table import *
from Song_Search import *
from SystemPathMethods import * 

from App_EventManager import *

class Application_Tab(QWidget):
    """
        Base class for a tab in the main application
        
        after instantiating a new instance of the tab call:
        addTab to add the tab to the end of the tab bar
        
        then use setCloseButton to add a close button to the tab
    """
    
    icon = None
    
    def __init__(self,parent=None):
        super(Application_Tab, self).__init__(parent)
        self.parent = parent
        self.btn_close = None
        self.name = "New Tab"
    
    def addTab(self,name="New Tab"):
    
        if self.icon != None:
            index = MpGlobal.Window.tabMain.addTab( self, self.icon, name )
        else:
            index = MpGlobal.Window.tabMain.addTab( self, name )
        
        self.name = name
    
    def setIcon(self,icon):
        self.icon = icon
        #TODO: check if set and update icon
    
    def getCurrentIndex(self):
        """
            return the current index of the tab in the main tab bar
            raises index error if the tab does not exist in the bar
        """
        for i in range(MpGlobal.Window.tabMain.count()):
        
            widget = MpGlobal.Window.tabMain.widget( i )
            
            if widget == self:
                return i
                
        raise IndexError("Tab not in TabBar. index out of range.")
        
    def setCloseButton(self): 
        index = self.getCurrentIndex()
            
        if self.btn_close == None:
            self.btn_close = CloseTabButton(self)
            MpGlobal.Window.tabMain.tabBar().setTabButton(index,QTabBar.LeftSide,self.btn_close)
            self.btn_close.setCallback(self.btn_click_close)
            return True
          
    def btn_click_close(self,bool=False):
        print "close me" 

    
class CloseTabButton(QPushButton):
    """
        callBack is the function to run when clicked
    """
    def __init__(self,parent=None):
        self.callBack = None;
        super(CloseTabButton,self).__init__(parent);
        #self.setIcon(MpGlobal.icon_AutoPLO)
        self.setFixedWidth(16);
        self.setFixedWidth(16);
        self.setObjectName("MpCloseTabButton")
        
    def setCallback(self,callBack):   
        self.callBack = callBack;
        
    def mouseReleaseEvent(self,event=None):
        #super(CloseTabButton,self).mouseReleaseEvent(event)
        if self.callBack != None:
            self.callBack();
            
            
from MpSort import *
        
from MpGlobalDefines import *
from MpScripting import *        
