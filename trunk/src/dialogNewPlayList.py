
# module laid out in define-import-execute format

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgetLineEdit import *
from StringParser import StringParse

class NewPlayListDialog(QDialog):
    def __init__(self,defaults="",parent=None):
        super(NewPlayListDialog,self).__init__(parent);
        self.setWindowTitle("Create New Playlist")
        
        # --------------------------
        # Widgets
        self.rad_all     = QRadioButton("All Music",self)
        self.rad_preset  = QRadioButton("Preset Search",self)
        self.rad_custom  = QRadioButton("Custom Search:",self)
        
        self.edit         = LineEdit(self)
        
        btn_accept  = QPushButton("Create",self)
        btn_cancel  = QPushButton("Cancel",self)

        self.chk_today   = QCheckBox("Ignore Songs Played Today",self)
        
        self.spin_preset = QSpinBox(self)
        self.spin_size   = QSpinBox(self)
        self.spin_hash   = QSpinBox(self)

        # --------------------------
        # Default Values
        self.rad_all.setChecked(True)

        self.edit.setPlaceholderText("All Music")
        
        self.spin_preset.setRange(0,9);
        self.spin_hash.setRange(0,100);
        self.spin_size.setRange(10,200);

        self.spin_preset.setDisabled(True);
        
        self.spin_preset.setValue(0);
        self.spin_hash.setValue(0);
        self.spin_size.setValue(50);

        # --------------------------
        # Layout
        self.grid = QGridLayout(self)
        #self.grid_app.setRowMinimumHeight(0,20)
        #self.grid_app.setRowMinimumHeight(1,20)
        #
        row = 0
        self.grid.addWidget(self.rad_all   ,row,0,Qt.AlignLeft)
        row+=1;
        self.grid.addWidget(self.rad_preset,row,0,Qt.AlignLeft)
        self.grid.addWidget(QLabel("Preset Number:"),row,1,Qt.AlignRight)
        self.grid.addWidget(self.spin_preset,row,2,Qt.AlignRight)
        row+=1;
        self.grid.addWidget(self.rad_custom,row,0,Qt.AlignLeft)

        row+=1; # self.edit ROW            
        vl_edit = QVBoxLayout(); # layout allows self.edit to expand
        self.grid.addLayout(vl_edit,row,0,1,3)#       widget,row,col,row_span,col_span
        vl_edit.addWidget(self.edit)
        self.grid.setRowMinimumHeight(row,20)

        row+=1;
        self.grid.addWidget(QLabel("Artist Song Limit:"),row,0,Qt.AlignLeft)
        self.grid.addWidget(QLabel("Play List Length"),row,2,Qt.AlignLeft)
        self.grid.setRowMinimumHeight(row,20)

        row+=1;
        self.grid.addWidget(self.spin_hash,row,0,Qt.AlignRight)
        self.grid.addWidget(self.spin_size,row,2,Qt.AlignRight)
        self.grid.setRowMinimumHeight(row,20)
        
        row+=1;
        self.grid.addWidget(self.chk_today,row,0,1,3,Qt.AlignLeft)
        
        row+=1;
        self.grid.addWidget(btn_cancel,row,0,Qt.AlignCenter)
        self.grid.addWidget(btn_accept,row,2,Qt.AlignCenter)
        self.grid.setRowMinimumHeight(row,20)
        
        # --------------------------
        # connect signals
        self.rad_all.clicked.connect(self.event_click_radio_button_1)   
        self.rad_preset.clicked.connect(self.event_click_radio_button_2)   
        self.rad_custom.clicked.connect(self.event_click_radio_button_3)   
        #self.edit.textEdited.connect(self.event_text_changed)
        self.edit.keyPressEvent = self.event_text_changed
        
        btn_accept.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        self.spin_preset.valueChanged.connect(self.event_spin_preset_changed)
        
        self.setDefaults(defaults);
        
    def setDefaults(self,string=""):
        obj = StringParse(string);
        
        text = ""
        if 'f' in obj.Switch:
            text = obj.Switch['f'];
        
        if 't' in obj.Switch:
            self.chk_today.setChecked(True)
        
        #print string
        #print  obj.Switch
        if 'n' in obj.Switch:
            self.spin_preset.setValue(int(obj.Switch['n']))
            self.event_spin_preset_changed(int(obj.Switch['n']))
            self.rad_reset.setDisabled(False)
            self.rad_preset.setChecked(True)
        elif 'a' in obj.Switch or text == "": 
            self.rad_all.setChecked(True)
        else:
            self.edit.setText(text)
            self.rad_custom.setChecked(True)
            
        if 's' in obj.Switch:
            self.spin_size.setValue(int(obj.Switch['s']))
            
        if 'h' in obj.Switch:
            self.spin_hash.setValue(int(obj.Switch['h'])) 
        
    def reject(self):
        super(NewPlayListDialog,self).reject()
    
    def event_click_radio_button_1(self,event=None):
        self.spin_preset.setDisabled(True);
        self.edit.setText("");
        
    def event_click_radio_button_2(self,event=None):
        self.spin_preset.setDisabled(False);
        self.event_spin_preset_changed(self.spin_preset.value())

    def event_click_radio_button_3(self,event=None):
        self.spin_preset.setDisabled(True);
            
    def event_text_changed(self,event=None):
        super(LineEdit,self.edit).keyPressEvent(event)
        self.rad_custom.setChecked(True)
        
    def event_spin_preset_changed(self,value=-1):
        self.edit.setText("Value: %d"%value);
        
    def getFormatedString(self):    
        string = "new "
    
        #--------------------------------------------------------------
        if self.spin_size.value() != 0:
            string += "-s %d "%self.spin_size.value()
        #--------------------------------------------------------------    
        if self.rad_preset.isChecked():
            string += '-n %d '%self.spin_preset.value()
        elif self.rad_all.isChecked() or self.edit.displayText() == "":
            string += "-a "
        else:
            text = self.edit.displayText()
            text = text.replace('"', '\\"'); #escape any quotes
            string += "-f \"%s\" "%text
        #--------------------------------------------------------------    
        if self.chk_today.isChecked():
            string += "-t "
        #--------------------------------------------------------------    
        if self.spin_hash.value() != 0:
            string += "-h %d "%self.spin_hash.value()
        #--------------------------------------------------------------    
        string += '-p '
        return string;

# ############################################################################
# ############################################################################
# Execute
# ############################################################################
# ############################################################################    
if __name__ != "__main__":
    from MpGlobalDefines import *
    # item is being loaded into another application
    # custom application code goes here
    def accept(self):
        print "Running as Import";
        super(NewPlayListDialog,self).accept()
        
    def event_spin_preset_changed(self,value=-1):

        preset = (Settings.SEARCH_PRESET0, \
                  Settings.SEARCH_PRESET1, \
                  Settings.SEARCH_PRESET2, \
                  Settings.SEARCH_PRESET3, \
                  Settings.SEARCH_PRESET4, \
                  Settings.SEARCH_PRESET5, \
                  Settings.SEARCH_PRESET6, \
                  Settings.SEARCH_PRESET7, \
                  Settings.SEARCH_PRESET8, \
                  Settings.SEARCH_PRESET9)[value]
        self.edit.setText(preset);
        self.edit.setCursorPosition(0)
    NewPlayListDialog.event_spin_preset_changed = event_spin_preset_changed
    
    NewPlayListDialog.accept = accept

    
else: # run as the main module
    
    def accept(self):    
        print "Running As Main, closing...";
        print self.getFormatedString()
        super(NewPlayListDialog,self).accept()
    NewPlayListDialog.accept = accept   # register a new function for accept
    
        
    import sys
    import os
    app = QApplication(sys.argv)
    app.setApplicationName("Console Player")
    app.setQuitOnLastWindowClosed(True)
    # create a window with no parent at 200 200 and data
    window = NewPlayListDialog("new -s 17 -f \"this\" -h 4 -t",None)
    #window.Renew(data)
    window.show()

    sys.exit(app.exec_())
    