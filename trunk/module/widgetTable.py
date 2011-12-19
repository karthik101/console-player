
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgetPage import HPage

from Qt_CustomStyle import *
#Qt.Key_MediaPlay

class CustomTableView(QTableView):
    parent = None;
    lastIndex = None;
    drag = None;
    disable_drag = False;
    def __init__(self,parent1,parent2=None):
        # there are 2 parents because:
        # this element needs a reference to the table object that will control it
        # also Qt widgets need a reference to their parent for color
        # inheritance, this is the second parent, which should be viewed as the
        # same type of parent that normal Qt widgets would have
        super(CustomTableView, self).__init__(parent2)
        self.parent = parent1;
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        

        self.setDropIndicatorShown (True)
        #DragOnly
        #DropOnly
        
        self.setAlternatingRowColors(True)

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            item = self.indexAt(event.pos())
            self.parent.leftPressEvent(item,event)
            self.disable_drag = False
        else:
            # select the item if there is no selection
            if len(self.parent.selection) == 0:
                item = self.indexAt(event.pos())
                index = self.parent.getDisplayOffset() + item.row()
                self.parent.selection.add(index)
            self.disable_drag = True
        self.drag = None
        
    def mouseMoveEvent(self,event):   
        if self.drag == None and len(self.parent.selection) > 0 and self.disable_drag == False:
            self.drag = QDrag(self)
            self.mime = QMimeData()
            #print str(self.parent.selection)
            self.mime.setText(self.parent.dragSend)
            #self.mime.setData("object/parent",self.parent)
            self.drag.setMimeData(self.mime)
            if self.parent.pixmap_drag != None:
                self.drag.setPixmap(self.parent.pixmap_drag)
                self.drag.setHotSpot(QPoint(32,-8))
            self.drag.start()
    def dragEnterEvent(self,event):
        if event.mimeData().hasText():
            if event.mimeData().text() in self.parent.dragReceive:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore() 
    def dragMoveEvent(self,event):
        event.accept()  # allows the widget to accept drop for some reason
        
    def dropEvent(self,event):
        item = self.indexAt(event.pos())
        row = item.row()
        self.parent.dropEvent(event,row)
        event.accept()
     
    def mouseReleaseEvent(self,event):
        if event.button() == Qt.LeftButton:
            item = self.indexAt(event.pos())
            if item.row() >= 0:
                self.parent.leftReleaseEvent(item,event)
            event.accept();
            
        elif event.button() == Qt.RightButton:
            self.parent.rightClickEvent(event)
            event.accept();
        else:
            event.ignore();
    def mouseDoubleClickEvent(self,event):
        item = self.indexAt(event.pos())
        self.parent.DoubleClick(item)
    def wheelEvent(self,event):
        velocity = (event.delta()/120)*-1
        value = self.parent.scrollbar.value();
        value += velocity;
        # bind value to min or max
        value = max(0,value)
        value = min(self.parent.scrollbar.maximum(),value)
        
        self.parent.scrollbar.setValue(value)
    
    def keyPressEvent(self,event):
        self.parent.keyPressEvent(event)
        
    def keyReleaseEvent(self,event):
        self.parent.keyReleaseEvent(event)
        
    def resizeEvent(self,event):
        """Add/Remove Rows from the table as the height of the table changes"""
        # get the height for the font, then set the height of the rows to this value
        self.parent.rowHeight = QFontMetrics(self.font()).height() + self.parent.rowSpacing
        
        height = self.height()# total height of the table
        self.parent.rowCount = (height/self.parent.rowHeight) + 1
        # set the row count to the calculated value
        self.parent.model.setRowCount(self.parent.rowCount)
        self.parent.FillTable(self.parent.getDisplayOffset())
        
        # force the row height of all rows
        for x in range(self.parent.rowCount):
            self.setRowHeight(x,self.parent.rowHeight)
            
      
        self.parent.resizeEvent(event)
        self.parent.adustScrollBar()
        # call super after overloaded resizeEvent 
        # in case the overloaded version can mess with some sizes
        # the super-version will take care of setting the lower scrollbar
        # and resizing the table
        super(CustomTableView, self).resizeEvent(event)
      
    def focusInEvent(self,event):
        super(CustomTableView,self).focusInEvent(event)
        self.parent.FillTable() # or FillTableColor
    def focusOutEvent(self,event):
        super(CustomTableView,self).focusOutEvent(event)
        self.parent.FillTable() # or FillTableColor
  
class Table(object):
    container = None
    table = None
    model = None
    scrollbar = None;
    parent = None;
    pixmap_drag = None;
    # Table Data Elements
    data = []
    colCount = 0;
    rowCount = 0;
    rowHeight = 15; # current row height ( this value calculated at run time )
    rowSpacing = 2; # set to change padding between rows
    selection = set()
    selLastRow = -1

    dragSend = "MpTableDrag"    # the type of drag that is sent from this widget
    dragReceive = [dragSend,]   # the type of drag that can be received
    
    brush_default  = QBrush(QColor(0,0,0,0))                # transparent
    brush_selected = QBrush(QColor(51,153,255,255))         # Blue
    brush_selectedOOF = QBrush(QColor(51,153,255,128))       # out of focuse        # Blue
    brush_selectedText = QBrush(QColor(255,255,255,255))    # white

    flag_MLClick = 0; # 0,1,2, are used as values to control what happens on mouse release
    
    event_proc = False
    
    def __init__(self,parent,header):
        
        self.parent = parent
        self.colCount = len(header)
        self.rowCount = 6;          # set to a temporary, non zero value
        
        self.container = QHBoxLayout()
        self.table = CustomTableView(self,parent) # needs a parent referance to this object
        self.scrollbar = QScrollBar(Qt.Vertical,self.table)
        self.model = QStandardItemModel(self.table)
        
        self.model.setHorizontalHeaderLabels( header );
        self.model.setRowCount(self.rowCount);


        self.table.verticalHeader().hide() # hides a number count of each row
        #self.table.setCornerButtonEnabled(False)

        self.table.setModel(self.model)
        self.table.setWordWrap(True)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        #self.table.setSelectionModel(QAbstractItemView.NoUpdate)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.cellPressed.connect(self.tableClicked)
        #self.table.cellPressed.connect(self.updateSelection)
        
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(100)
        self.scrollbar.setSingleStep(1)
        self.scrollbar.setPageStep(10)
        
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        #self.table.setVerticalScrollMode(-1)
        #self.table.setVerticalScrollBar(self.scrollbar)
        # set up the container widget for the table and scroll bar
        
        self.container.addWidget(self.table)
        self.container.addWidget(self.scrollbar)
        self.container.setSpacing(0)
        
        QObject.connect(self.scrollbar,SIGNAL("valueChanged(int)"),self.FillTable)
        self.table.doubleClicked.connect(self.DoubleClick)
        self.table.pressed.connect(self.MouseDown)
        self.table.horizontalHeader().sectionClicked.connect(self.columnClicked)

    def UpdateTable(self,offset=0,array=None):
        """Update the data array, and then refresh the table"""
        # array is referance to an array.
        # offset is the first index in array 'data' to display in a table
        #assert self.scrollbar.value() >= 0, "OFFSET PREFIX ERROR m:%d M:%d v:%d"%(self.scrollbar.minimum(),self.scrollbar.maximum(),self.scrollbar.value())

        if array != None :
            self.data = array;
        
        self.adustScrollBar(offset)
        
        self.FillTable(offset);

        
    def adustScrollBar(self,offset=-1):
        
        if offset == -1:
            offset = self.scrollbar.value()
        self.scroll_MaxRange = max(0,len(self.data) - self.rowCount + 4) 
        self.scrollbar.setMaximum(self.scroll_MaxRange)
        self.scrollbar.setPageStep(self.rowCount)
        self.scrollbar.setValue(offset)
        
        assert self.scrollbar.value() >= 0, "OFFSET WRITE ERROR m:%d M:%d v:%d"%(self.scrollbar.minimum(),self.scrollbar.maximum(),self.scrollbar.value())
    
        
    def FillTable(self,offset=-1):    
        """fill the table with data, starting at index offset, from the Display Array"""
        R = []
        k=0;
        if offset < 0 :
            offset = self.scrollbar.value()
        else:
            self.scrollbar.setValue(offset)
        #offset = max(0,offset)
        #TODO ERROR WITH READING VALUE, set signal to whatch for when offset is set
        #assert offset >= 0, "OFFSET READ ERROR m:%d M:%d v:%d"%(self.scrollbar.minimum(),self.scrollbar.maximum(),self.scrollbar.value())
        #if (self.data == None):
        #    return
        size = len(self.data) # in case size is zero, prevent any drawing to it
        for i in range(self.rowCount):
            k = i+offset; # the k'th element of the data array
            
            if k < len(self.data) and size > 0:
                R = self.FillRow(k)
                brush = self.FillRowColor(k)
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),R[j])
                    if type(brush) == tuple:
                        self.model.setData(self.model.index(i,j),brush[j%len(brush)],Qt.BackgroundRole)
                    else:
                        self.model.setData(self.model.index(i,j),brush,Qt.BackgroundRole)
            else:
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),"")
                    self.model.setData(self.model.index(i,j),self.brush_default,Qt.BackgroundRole)
        
    def getSelection(self):
        if len(self.selection) == 0:
            return []
        array = [[]]*len(self.selection)
        index = 0
        for x in self.selection:
            array[index] = self.data[x]
            index += 1
        return array
        
    def clearSelection(self):
        self.selection = set()
        self.FillTable()
        
    def MouseDown(self,item):
        print "mouse down"
        
    def DoubleClick(self,item):
        pass
    
    def dropEvent(self,event,row):
        pass
    # Overload this function in a sub class to fill rows with data
    # this function should return an element for each column, with col 0
    # at index zero in the array. The index, i, is the i'th element of the table
    def FillRow(self,i):
        return ["--"]*self.colCount
    
    def FillRowColor(self,i):
        if i in self.selection:
            return self.brushSelectionColor()
        return self.brush_default
    
    def brushSelectionColor(self):
        if self.table.hasFocus() :
            return self.brush_selected
        else:
            return self.brush_selectedOOF
    
    # semi-private functions. These should not really be needed  
    def setDisplayOffset(self,value):
        if value < 0:
            value = 0
        if value >= self.scrollbar.maximum():
            value = self.scrollbar.maximum()
        
        self.scrollbar.setValue(value)
        
    def getDisplayOffset(self):
        return self.scrollbar.value()

    def columnClicked(self,col):
        print col

    def resizeEvent(self,event):
        pass
    
    def leftPressEvent(self,item,event):    
        self.flag_MLClick = 0;
        
        _shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier
        _ctrl = event.modifiers()&Qt.ControlModifier ==  Qt.ControlModifier
        _offset = self.scrollbar.value()
        _row = item.row() + _offset
        l = min(self.selLastRow,_row)
        m = max(self.selLastRow,_row) + 1
        
        if _row < len(self.data):
            if _shift and self.selLastRow >= 0:
                if not _ctrl :
                    self.selection = set()
                for x in range(l,m):
                    self.selection.add(x) 
            else:
                if _ctrl :
                    if _row in self.selection :
                        self.flag_MLClick = 1
                        #self.selection.remove(_row) 
                    else:
                        self.selection.add(_row) 
                else:
                    if _row in self.selection :
                        self.flag_MLClick = 2
                    else:
                        self.selection = set()
                        self.selection.add(_row) 
                
        self.FillTable()
        if not _shift:
            self.selLastRow = _row
        #if item.row() not in self.selection :
        #    self.selection.add(item.row())
        #    self.FillTable()
    def leftReleaseEvent(self,item,event):
        #self.parent.addToSelection(item)
        
        _offset = self.scrollbar.value()
        _row = item.row() + _offset
        if _row < len(self.data):
            
            
            if self.flag_MLClick == 1 and len(self.selection) > 0 :
                self.selection.remove(_row)
                self.FillTable()
            elif self.flag_MLClick == 2:
                self.selection = set()
                self.selection.add(_row)
                self.FillTable()
           
                
        self.flag_MLClick == 0

    def rightClickEvent(self,event):
        pass
    

    def keyPressEvent(self,event):
        pass;
        #if event.key() == Qt.Key_Up:
        #    pass; self.__keyboard_scroll_UP__();
        #elif event.key() == Qt.Key_Down:
        #    pass; self.__keyboard_scroll_DOWN__();
        #elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
        #    pass;
        #elif event.key() == Qt.Key_Delete :
        #    pass
            
    def keyReleaseEvent(self,event):
        pass
        #print event.key()
    # drag type is the type of drags that this widget can send
    # drag recieve is the list of types that it will except
    def setDragType(self,str):
        self.dragSend = str
    def setDragReceiveType(self,str):
        self.dragReceive = [str,]
    def addDragReceiveType(self,str):   
        self.dragReceive.append(str)
        
    def itemToIndex(self,item):
        _offset = self.scrollbar.value()
        _row = item.row() + _offset
        return _row
     
    def __keyboard_scroll_UP__(self):
        x = self.getDisplayOffset()
        if len(self.selection) > 0:
            R = list(self.selection)
            R.sort()
            y = R[0] - 1
            if y < x or y > x+self.rowCount-5:
                self.setDisplayOffset(y)

            if y >= 0 and y < len(self.data):
                self.selection = set()
                self.selection.add(y)
                self.FillTable()
    def __keyboard_scroll_DOWN__(self):
        offset = 5; # offset for when scrolling down
                    # choose an offset value such that when scrolling down
                    # you always see the highlighted item
        x = self.getDisplayOffset()
        if len(self.selection) > 0:
            R = list(self.selection)
            R.sort()
            y = R[0] + 1
            if y < x:
                self.setDisplayOffset(y)
            elif y > x+self.rowCount-offset:    # subtract here, add there, and if the offst is the same
                self.setDisplayOffset(y-self.rowCount+offset) # the scrolling will be smooth
                
            if y >= 0 and y < len(self.data): 
            
                self.selection = set()
                self.selection.add(y)
                self.FillTable()
                
    def __del__(self):
        del self.container
        del self.table
        del self.model
        del self.scrollbar
        
class HPageTable(Table):
    def __init__(self,parent,header):
    
        self.colCount = len(header)
        self.rowCount = 6;          # set to a temporary, non zero value
        
        self.container = HPage()
        self.table = CustomTableView(self,parent) # needs a parent referance to this object
        self.scrollbar = QScrollBar(Qt.Vertical,self.table)
        self.model = QStandardItemModel(self.table)
        
        self.model.setHorizontalHeaderLabels( header );
        self.model.setRowCount(self.rowCount);


        self.table.verticalHeader().hide() # hides a number count of each row
        #self.table.setCornerButtonEnabled(False)

        self.table.setModel(self.model)
        self.table.setWordWrap(True)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.cellPressed.connect(self.tableClicked)
        #self.table.cellPressed.connect(self.updateSelection)
        
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(100)
        self.scrollbar.setSingleStep(1)
        self.scrollbar.setPageStep(10)
        
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        
        # set up the container widget for the table and scroll bar
        
        self.container.addWidget(self.table)
        self.container.addWidget(self.scrollbar)
        
        QObject.connect(self.scrollbar,SIGNAL("valueChanged(int)"),self.FillTable)
        self.table.doubleClicked.connect(self.DoubleClick)
        self.table.pressed.connect(self.MouseDown)
        self.table.horizontalHeader().sectionClicked.connect(self.columnClicked)

if __name__ == '__main__':
    import sys
    # ######################################
    # Example polymorphism of my custom table
    # this is all that is needed to define a table
    # ######################################
    class testTable(Table):
        def FillRow(self,index):
            #print len(self.data), " ", index
            R = [""]*self.colCount
            R[0] = self.data[index][0]
            R[1] = self.data[index][1]
            R[2] = self.data[index][2]
            R[3] = "%s"%self.selection
            return R
    # ######################################
    # define a Qt Window for running an example in
    # ######################################
    class MainWindow(QMainWindow):
        """Instantiate a new main window"""
        table=None;
        window = None;
        
        def __init__(self,title):
            super(QMainWindow, self).__init__()
            
            headers = ("Title", "Artist", "Album", "Year")
            
            self.window = QWidget()
            self.table = testTable(self.window,headers)
            self.window.setLayout(self.table.container)
            
            self.setCentralWidget(self.window)
            self.setWindowTitle(title)
        def sizeHint(self):
            return QSize(660, 305)
    
    # start a new Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Music Player")
    app.setQuitOnLastWindowClosed(True)
    # create and display the main window 
    
    window = MainWindow("Table Example")
    window.table.pixmap_drag = QPixmap("./drag.png")
    window.show()

    # ######################################
    # make a dummy array of data to display in the table
    # ######################################
    R=[[]]*20   # make a dummy array of data to fill
    for i in range(len(R)):
        R[i] = [">>%d"%i,"2","3","4"]
    window.table.UpdateTable(0,R)
    
    # ######################################
    # Main Loop
    # ######################################
      
    sys.exit(app.exec_())
    
# ######################################
# #    
# ######################################