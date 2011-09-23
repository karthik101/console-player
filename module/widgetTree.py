#!/usr/bin/python -O

# simpleTreeWidget.py
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui  import *

class TreeWidget(QTreeWidget):

    def __init__(self, parent=None, headers= ["Default",]):
        super(TreeWidget,self).__init__(parent)
        self.setColumnCount(len(headers)-1);
        #print len(headers)
        self.setHeaders(headers)
        self.parent = parent
        
    def addParent(self,itemChild,data=None):

        
        if type(itemChild) == list:
            itemChild = TreeItem(itemChild,data)
        elif type(itemChild) == str or type(itemChild) == unicode:
            itemChild = TreeItem( [itemChild,], data)
       
        self.addTopLevelItem(itemChild)
        #item = TreeItem(['one',],'',self)
        #self.addTopLevelItem(item)
        
        return itemChild
    def insertParent(self,index,itemChild,data=None):

        if type(itemChild) == list:
            itemChild = TreeItem(itemChild,data)
            
        self.insertTopLevelItem(index,itemChild)
        
        return itemChild
    def parentCount(self):
        return self.topLevelItemCount();
        
    def insertChild(self,parentRow,index,itemChild,data=None):
        #
        # OVERLOADED FUNCTION
        # self.insertChild(parent/row,index,item/child,data=None)
        # parentRow: int or TreeItem
        #       int:    function will find TOPLEVEL TreeItem corresponding to row in self
        #       TreeItem:   function will insert child
        # itemChild: StringList or TreeItem
        #       StringList: list of string data, a new TreeItem will be constructed then added at index
        #       TreeItem:   child item to insert at index
        if type(itemChild) == list:
            itemChild = TreeItem(itemChild,data)
        elif type(itemChild) == str or type(itemChild) == unicode:
            itemChild = TreeItem( [itemChild,], data)
            
        if type(parentRow) == int:    
            parentRow = self.topLevelItem(parentRow)
        
        parentRow.insertChild(index,itemChild)  
        
        return itemChild
    def addChild(self,parentRow,itemChild,data=None):
        # OVERLOADED FUNCTION
        # self.insertChild(parent/row,item/child,data=None)
        # parentRow: int or TreeItem
        #       int:    function will find TOPLEVEL TreeItem corresponding to row in self
        #       TreeItem:   function will insert child
        # itemChild: StringList or TreeItem
        #       StringList: list of string data, a new TreeItem will be constructed then added at index
        #       TreeItem:   child item to insert at index
        if type(itemChild) == list:
            itemChild = TreeItem(itemChild,data)
        elif type(itemChild) == str or type(itemChild) == unicode:
            itemChild = TreeItem( [itemChild,], data)
        
            
        if type(parentRow) == int:    
            parentRow = self.topLevelItem(parentRow)
        
        if parentRow != None:
        
            parentRow.addChild(itemChild)  
            return itemChild
       
        return None;
    def removeChild(self,parentRow,index):
        
        # OVERLOADED FUNCTION
        # index:    int or TreeItem
        #       TreeItem: remove child of type TreeItem from the parent
        #       int:      remove the child at index from the parent
        
        if type(parentRow) == QModelIndex:
            parentRow = self.itemFromIndex(parentRow)
            
        if type(index) == int:    
            index = parentRow.child(index)
            
        if index!= None:    
            parentRow.removeChild (index)
            return True;
        return False;
    def childCount(self,parentRow):
    
        if type(parentRow) == int:    
            parentRow = self.topLevelItem(parentRow)  
        elif type(parentRow) == QModelIndex:
            parentRow = self.itemFromIndex(parentRow)
         
        return parentRow.childCount();    
    
    def getItem(self,parentRow,childIndex=-1):
        
        # this is my favorite function ever.
        # USE:
        
        # getItem(int row)
        # getItem(TreeItem item)
        # getItem(QModelIndex index)
        # getItem(int row, int child)
        # getItem(TreeItem item, int child)
        # getItem(QModelIndex index, int child)
        
        # when no child index is specified,
        #   this function returns the item at index row, or specified my modelindex
        # specifing and child index, returns the child at that index for parent
        
        if type(parentRow) == int:    
            parentRow = self.topLevelItem(parentRow)  
        elif type(parentRow) == QModelIndex:
            parentRow = self.itemFromIndex(parentRow)
         
        if (parentRow== None):
            return None;
         
        if childIndex < 0:  
            return parentRow;
        if childIndex < parentRow.childCount():
            return parentRow.child(childIndex);
        else:
            return None;
    
    def setHeaders(self,headers):
        item = self.headerItem()

        for col in range(self.columnCount()+1):
            item.setText(col,headers[col%len(headers)])
    def setHeader(self,index,header):
    
        self.headerItem().setText(index,header)
            
    def mouseReleaseEvent(self,event=None):
        super(TreeWidget,self).mouseReleaseEvent(event)
        #Qt.NoButton 	
        #Qt.LeftButton 	
        #Qt.RightButton 	
        #Qt.MidButton 	
        #Qt.MiddleButton 
        #Qt.XButton1 	
        #Qt.XButton2 	
        
        #if event:
        #    index = self.indexAt(event.pos())
        #    item = self.getItem(index) # converts an index to a TreeItem
        #    if event.button() == Qt.RightButton :
        #        print ">"+str(item)
        #    elif event.button() == Qt.LeftButton :
        #        print "<"+str(item)
        return; 
        
class TreeItem(QTreeWidgetItem):

    # int childCount (self)
    # addChild (self, QTreeWidgetItem child)
    # QTreeWidgetItem child (self, int index)
    # int indexOfChild (self, QTreeWidgetItem achild)
    # removeChild (self, QTreeWidgetItem child)
    def __init__ (self, text=["No Data",], data='No Text Data', parent=None, _type = QTreeWidgetItem.Type):
        # text as list of strings
        super(TreeItem,self).__init__(parent,_type)
        
        self.data = data
        self.display = text;
        
        if type(text) == str or type(text) == unicode:
            text = [text,];
            
        for col in range(self.columnCount()+1):
            self.setText(col,text[col%len(text)])
            
        flags = (Qt.ItemIsEditable | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable | Qt.ItemIsEnabled )
        self.setFlags( flags )
        
    def __str__(self):
        return "%s => <%s>"%(self.display[0], str(self.data)[:20]);

if __name__ == "__main__":
    
    class MainWindow(QMainWindow):
        def __init__(self,parent=None):
            super(MainWindow,self).__init__(parent)
            self.setWindowTitle("simpleTreeWidget")
            self.resize(640, 360)
            self.tree = TreeWidget(self,["One",]);
            self.setCentralWidget(self.tree);
            
            
            self.tree.addParent("title","no Data") #
            
            # for i in range(10):
            #     text = ["Item: %d"%(i+1),]
            #     self.tree.addParent(text,"no Data") #
            # self.tree.insertParent(3,["insert Parent",],"no data")
            # 
            # #print self.tree.topLevelItemCount ()
            # 
            # for i in range(10):
            #     text = ["Child: %d"%(i+1),]
            #     self.tree.addChild(i,text,"ChildData")
            # 
            # item = self.tree.getItem(3,0)
            # text = ["GrandChild",]
            # child = TreeItem(text)
            # item.addChild(child)
      
            print "init done"
            #print self.tree.getItem(2)
            #print self.tree.getItem(2,0)
    
    def main(argv=None):
        global Window  
        if argv is None:
            argv = sys.argv
          
        Window = MainWindow();
        Window.show();
        
    global Application
    Application = QApplication(sys.argv)
    Application.setApplicationName("New Project")
    Application.setQuitOnLastWindowClosed(True)

    main()

    sys.exit(Application.exec_())

