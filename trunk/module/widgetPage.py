from PyQt4.QtCore import *
from PyQt4.QtGui import *


class AbstractPage(QWidget):
    """
        Abstract Page serves as a page element when creating
        the application. A common event i have run into is
        creating a widget type object, and then also creating
        a vbox or hbox as the only child of that object
        This class intends to clean this portion of writing code
        so that it can be easier to read and maintain
        
        Page objects are of type QWidget, contain a child QLayout, and
        all normal QLayout functions are associated instead with 
        an object that is of type QWidget
    """
    layout = None

    
    def addWidget(self,widget):
        self.layout.addWidget(widget)
        
    def addLayout(self,layout):
        self.layout.addLayout(layout)
        
    def insertWidget(self,i,widget):
        self.layout.insertWidget(i,widget)
        
    def insertLayout(self,i,layout):
        self.layout.insertLayout(i,layout) 

        
class HPage(AbstractPage):
    def __init__(self,parent=None):
        super(HPage,self).__init__(parent);
        self.layout = QHBoxLayout(self)
        self.layout.setMargin(3)

class VPage(AbstractPage):
    def __init__(self,parent=None):
        super(VPage,self).__init__(parent);  
        self.layout = QVBoxLayout(self)     
        self.layout.setMargin(3)        