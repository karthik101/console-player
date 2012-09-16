#! python $this
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgetLargeTable import *
import os,sys
import time

__LAST_ALERT_TIME=0
def _alert_(value):
    # makes a system beep, but no more than 3 per second.
    global __LAST_ALERT_TIME
    if value:
        new_time = time.time()
        if new_time > __LAST_ALERT_TIME+.3:
            os.system("echo \a")
            __LAST_ALERT_TIME = new_time
    return value    

class CellEditor(QObject):
    INSERT_TOKEN = u"\u00A6"
    
    def __init__(self,default_text=""):
        self.buffer = default_text
        self.insert_index = len(default_text)
    
        self.selection_start = 0# range of selection self.buffer[self.selection_start:self.selection_end]
        self.__selection_end   = 0
    @property
    def selection(self):
        return self.buffer[self.selection_start:self.selection_end]
    @property
    def selection_end(self):
        return self.__selection_end
    @selection_end.setter
    def selection_end(self,value):   
        self.__selection_end = max(value,self.selection_start,self.__selection_end)
        self.selection_start = min(value,self.selection_start)
    def selection_all(self):
        self.selection_start = 0
        self.__selection_end = len(self.buffer)   
    def selection_clear(self):
        self.selection_start = 0
        self.__selection_end = 0
    def index_left(self):
        # move the insertion index to the left
        if self.insert_index  > 0:
            self.insert_index -= 1
        if self.insert_index >= len(self.buffer):
            self.insert_index = len(self.buffer) - 1
    def index_right(self):
        # move the insertion index to the right
        if self.insert_index < len(self.buffer):
            self.insert_index += 1
      
    def delete(self):
        # the delete key is pressed
        if _alert_(len(self.buffer) == 0 or self.insert_index >= len(self.buffer)): return;
        sel = self.selection
        if sel:
            self.buffer = self.buffer[:self.selection_start] +  self.buffer[self.selection_end:]
            self.insert_index = self.selection_start
            self.selection_clear()
        elif self.insert_index < len(self.buffer):
            self.buffer = self.buffer[:self.insert_index] + self.buffer[self.insert_index+1:]
    def backspace(self):
        # the backspace key is pressed
        if _alert_(len(self.buffer) == 0 or self.insert_index==0): return;
        sel = self.selection
        if sel:
            self.buffer = self.buffer[:self.selection_start] +  self.buffer[self.selection_end:]
            self.insert_index = self.selection_start
            self.selection_clear()
        elif self.insert_index > 0:
            self.buffer = self.buffer[:self.insert_index-1] + self.buffer[self.insert_index:]
            self.insert_index -= 1
    def insert(self,text):
    
        sel = self.selection
        if sel:
            self.buffer = self.buffer[:self.selection_start] + text +  self.buffer[self.selection_end:]
            self.insert_index = self.selection_start + len(text)
            self.selection_clear()
        else:    
            self.buffer = self.buffer[:self.insert_index] + text +  self.buffer[self.insert_index:]
            self.insert_index += len(text)
    def key_pressed(self,qkeyevent):
        pass

    def format_string(self):
        return self.buffer[:self.insert_index] + CellEditor.INSERT_TOKEN +  self.buffer[self.insert_index:]
        
class _sigmanager(QObject):
    """ small bug in my implementation, columns are not QObjects
    and therefor cannot have signals bound to them
    """
    cell_modified = pyqtSignal( set, unicode )        
        
class EditColumn(TableColumn):
    #cell_modified = pyqtSignal(set,unicode)
    def __init__(self,parent,index,name=None):
        super(EditColumn,self).__init__(parent,index,name)
        
        self.editor = None
        self.open_editors = set() #  set of row indices to be editing
        
        self.sigmng = _sigmanager()
         
    @property
    def cell_modified(self):
        return self.sigmng.cell_modified
        
    def paintItem(self,col,painter,row,item,x,y,w,h):
        
        if self.editor != None and row in self.open_editors:
            painter.fillRect(x,y,w,h,self.parent.palette_brush(QPalette.Base))
            item = self.editor.format_string()
            sel = self.editor.selection
            if sel: # if there is a selection to highlight
                #palette_brush(QPalette.Highlight)
                
                w1 = painter.fontMetrics().width(self.editor.buffer[:self.editor.selection_start])
                w2 = painter.fontMetrics().width(sel)
                
                #if self.editor.selection_start <= self.editor.insert_index < self.editor.selection_end:
                #    w2 += painter.fontMetrics().width(CellEditor.INSERT_TOKEN)
                if self.editor.insert_index < self.editor.selection_start :
                    w1 += painter.fontMetrics().width(CellEditor.INSERT_TOKEN)
                else:
                    w2 += painter.fontMetrics().width(CellEditor.INSERT_TOKEN)
                painter.fillRect(x+w1+self.parent.text_padding_left,y,w2,h,self.parent.palette_brush(QPalette.Highlight))
            self.cellTextColor = self.parent.painter_brush_font.color()

        self.paintItem_text(col,painter,row,item,x,y,w,h)
        self.cellTextColor = None
        
    def keyPressEvent(self,event):
        mod = event.modifiers()
        _c = mod&Qt.ControlModifier
        _s = mod&Qt.ShiftModifier
        if _c:
            # move stuff between the clipboard
            if event.key() == Qt.Key_V:
                text = QApplication.instance().clipboard().text()
                text = text.replace('\r','').replace('\n','')
                self.editor.insert( text)
            elif event.key() == Qt.Key_C:
                sel = self.editor.selection
                if sel:
                    QApplication.instance().clipboard().setText(sel) 
            elif event.key() == Qt.Key_A:
                self.editor.selection_all();
        # save and being editing the next sell with Tab
        elif event.key() in (Qt.Key_Tab,Qt.Key_Backtab):   
            # if we are editing one row at a time TAB can sequentially move through all rows
            if len(self.open_editors) == 1:
                row = list(self.open_editors)[0]
                if   event.key() == Qt.Key_Tab     : row += 1
                else                               : row -= 1
                # if r is still withing range
                self.editor_save()
                if 0 <= row < len(self.parent.data):
                    default_text = self.parent.getItem(row,self.index)
                    self.editor_start({row,},default_text)
        elif event.key() == Qt.Key_Left:
            self.editor.index_left()
            if _s: self.editor.selection_end  = self.editor.insert_index
            else: self.editor.selection_clear()
        elif event.key() == Qt.Key_Right:
            self.editor.index_right()
            if _s: self.editor.selection_end  = self.editor.insert_index
            else: self.editor.selection_clear()
        elif event.key() == Qt.Key_Delete:
            self.editor.delete()
        elif event.key() == Qt.Key_Backspace:
            self.editor.backspace()
        elif event.key() == Qt.Key_Home:
            self.editor.insert_index = 0
        elif event.key() == Qt.Key_End:
            self.editor.insert_index = len(self.editor.buffer)
        # use enter to save the changes
        elif event.key() in (Qt.Key_Enter,Qt.Key_Return):
            self.editor_save()
        elif event.key() == Qt.Key_Escape:
            self.editor_close()
        # some bonus keystrokes that are not normally found    
        elif event.key() == Qt.Key_PageUp:
            self.editor.buffer= unicode(self.editor.buffer).upper()
        elif event.key() == Qt.Key_PageDown:
            self.editor.buffer= unicode(self.editor.buffer).lower()
        elif event.key() == Qt.Key_Insert:
            self.editor.buffer= unicode(self.editor.buffer).title()
        elif event.key() == Qt.Key_Shift:
            self.editor.selection_start = self.editor.insert_index
            self.editor.selection_end   = self.editor.insert_index
        #default
        else:
            self.editor.insert(event.text())
        self.parent.update()
    
        
    def mouseDoubleClick(self,row):
        # todo open/close editor should be moved to it's own function
        
        temp = set()
        sel = self.parent.selection
        if len(sel) > 0:
            temp = set(sel)
        temp.add(row)
        default_text = self.parent.getItem(row,self.index)
        for row in temp:
            if row < 0 or row > len(self.parent.data):
                return
        self.editor_start(temp,default_text)
   
    def mouseClick(self,row_index,posx,posy):
        pass
        
    def editor_start(self,rows,text=""):
        """
            start editing the rows in the iterable 'rows'
            use the default text 'text'
        """
        self.open_editors = set(rows)
        self.captureKeyboard()
        #for row in self.open_editors:
        #    if self.parent.getItem(row,self.index) != default_text:
        #        default_text = ""
        self.editor = CellEditor(text)  
 
    def editor_save(self):
        """
            save the modified buffer to 'index; of each row in the data set
        """
        for row in self.open_editors:
            self.parent.data[row][self.index] = self.editor.buffer
        self.parent.update()
        self.cell_modified.emit(self.open_editors,unicode(self.editor.buffer))
        self.editor_close()
        
    def editor_close(self):
        """
            end the editing session
        """
        
        self.editor = None
        self.open_editors = set() # clear all rows that are being edited
        self.releaseKeyboard()
        self.parent.update()
          
if __name__ == '__main__':    
    
    app = QApplication(sys.argv)

    table = LargeTable()
    table.columns = []
    table.columns.append(EditColumn(table,0,"Test Column"))
    
    items = [ ["Text One","abm1","ttl1"], ["Text Two","abm1","ttl2"], ["Text Three","abm2","ttl3"], ["Text Four","abm3","ttl4"] ]     
    table.setData(items)
    table.container.resize(640,320)
    table.container.show()
    
    sys.exit(app.exec_())