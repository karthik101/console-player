#!/usr/bin/python -O

# column_choose.py
import os
import sys

import sip

if __name__ == "__main__":
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)

from PyQt4.QtCore import *
from PyQt4.QtGui  import *

class DialogColumnSelect(QDialog):
    def __init__(self,L, active, parent=None):
        super(DialogColumnSelect,self).__init__(parent)
        self.setWindowTitle("column_choose")
        self.resize(400, 150)

        self.centralLayout = QGridLayout(self)
        
        self.centralLayout.setMargin(0)
        self.centralLayout.setSpacing(0)

        self.lista = QListWidget();
        self.listb = QListWidget();
        
        lbl_act = QLabel('Active Columns')
        lbl_ina = QLabel('Inactive Columns')
        
        self.btn_up = QPushButton('up');
        self.btn_dn = QPushButton('down');
        self.btn_mv = QPushButton('<-->');

        self.btn_accept = QPushButton('apply')
        
        self.btn_up.setFixedWidth(48)
        self.btn_dn.setFixedWidth(48)
        self.btn_mv.setFixedWidth(48)
        #self.btn_accept
        
        self.centralLayout.addWidget(lbl_act, 0, 1, 1, 1,Qt.AlignHCenter)
        self.centralLayout.addWidget(lbl_ina, 0, 3, 1, 1,Qt.AlignHCenter)
        
        self.centralLayout.addWidget(self.lista, 1, 1, 4, 1)
        self.centralLayout.addWidget(self.listb, 1, 3, 4, 1)
        
        self.centralLayout.addWidget(self.btn_up, 2, 0, 1, 1,Qt.AlignHCenter)
        self.centralLayout.addWidget(self.btn_dn, 3, 0, 1, 1,Qt.AlignHCenter)
        self.centralLayout.addWidget(self.btn_mv, 2, 2, 1, 1,Qt.AlignHCenter)
        
        self.centralLayout.addWidget(self.btn_accept, 6, 3, 1, 1,Qt.AlignHCenter)
        
        self.centralLayout.setColumnMinimumWidth(0,52)
        self.centralLayout.setColumnMinimumWidth(2,52)
        
        

        for i in range(active):
            self.lista.addItem(L[i])
        for i in range(active,len(L)):
            self.listb.addItem(L[i])
        
        self.lista.itemClicked.connect(self.event_click_left)
        self.listb.itemClicked.connect(self.event_click_right)
        
        self.btn_up.clicked.connect(self.event_move_up)
        self.btn_dn.clicked.connect(self.event_move_down)
        self.btn_mv.clicked.connect(self.event_move)
        self.btn_accept.clicked.connect(self.accept)
        # current selected item.
        
        self.c_row = 0;
        self.c_item = None;
        self.c_side = 0;
        
        self.ResultList = L
        self.ActiveCount = active
        
    def event_click_left(self,item=None):
        if item != None:
            
            row = self.lista.indexFromItem(item).row()
            
            self.btn_mv.setText('-->')
            
            self.c_row = row;
            self.c_item = item;
            self.c_side = 0;
            
            self.listb.setCurrentItem(self.c_item)
            
            #print item.data(Qt.DisplayRole),row
            return
        
    def event_click_right(self,item=None):
        if item != None:
            row = self.listb.indexFromItem(item).row()
            
            self.btn_mv.setText('<--')
            
            self.c_row = row;
            self.c_item = item;
            self.c_side = 1;
            
            self.lista.setCurrentItem(self.c_item)
            
            #print item.data(Qt.DisplayRole),row
            return;
    
    def event_move_up(self,event=None):
    
        if self.c_side == 0:
            L = self.lista
        else:
            L = self.listb
            
        if self.c_item != None and self.c_row > 0:
            
            item = L.takeItem(self.c_row)
            self.c_row -= 1;
            #print self.c_row
            L.insertItem(self.c_row,self.c_item)
            L.setCurrentItem(self.c_item)
            
    def event_move_down(self,event=None):
    
        if self.c_side == 0:
            L = self.lista
        else:
            L = self.listb
            
        if self.c_item != None and self.c_row < L.count():
            
            item = L.takeItem(self.c_row)
            self.c_row += 1;
            #print self.c_row
            L.insertItem(self.c_row,self.c_item)
            L.setCurrentItem(self.c_item)
            
    def event_move(self,event=None):
        if self.c_side == 0:
            L = self.lista
            T = self.listb
        else:
            L = self.listb
            T = self.lista
            
        if self.c_item != None and self.c_row < L.count():
            
            item = L.takeItem(self.c_row)
            self.c_row += 1;
            #print self.c_row
            T.addItem(self.c_item)
            T.setCurrentItem(self.c_item)
            self.c_row = T.indexFromItem(self.c_item).row()
            self.c_side = 0 if self.c_side else 1
            
            #print self.c_row
            
            L.setCurrentItem(None)
            T.setCurrentItem(self.c_item)
            
            if self.c_side:
                self.btn_mv.setText('<--')
            else:
                self.btn_mv.setText('-->')
          
    def accept(self,event=None):
        active = self.lista.count();
        
        #print "active %d"%active
        
        self.ResultList = []
        
        for i in range(self.lista.count()):
            name = self.lista.item(i).data(Qt.DisplayRole)
            self.ResultList.append(name)
        
        self.ActiveCount = self.lista.count()
        
        for i in range(self.listb.count()):
            name = self.listb.item(i).data(Qt.DisplayRole)
            self.ResultList.append(name)
        
        #print R
        
        super(DialogColumnSelect,self).accept();
        
def main(argv=None):
	global Window  
	if argv is None:
		argv = sys.argv

    #[11, 2, 3, 4, 9, 8, 15, 6, 7, 5, 99, 13, 12, 1]
	Window = DialogColumnSelect(['A','B','C'],3);
	Window.show();

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setApplicationName("column_choose")
    app.setQuitOnLastWindowClosed(True)

    main()

    sys.exit(app.exec_())
