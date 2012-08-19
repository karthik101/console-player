
# TODO: currentyly each edit row is stored as a tuple, and should be it's own object.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from MpGlobalDefines import *
from Song_Object import Song
from datatype_hex64 import *


from SystemPathMethods import *
from widgetLineEdit import *
from SystemDateTime import DateTime

_COL_LBL = 0
_COL_CHK = 1
_COL_EDT = 2

class SongEditWindow(QDialog):
        
    editList = []   # list of tuples of widgets
    multiList = []    
        
    art = 0 # string
    cmp = 1 # string
    ttl = 2 # string
    abm = 3 # string
    gen = 4 # string
    lng = 5 # string
    com = 6 # string
    pth = 7 # string
    rte = 8 # int
    pct = 9 # int
    sct =10 # int
    frq =11 # int
    ind =12 # int
    yer =13 # int
    dte =14 # date
    add =15 # date
    
    

    def __init__(self,parent):

        super(SongEditWindow, self).__init__(parent)
        
        self.gridlayout = QGridLayout();
        self.editList = []
        self.multiList = []   
        
        #self.setWindowIcon(QIcon('icon.png'))
        
        #self.resize(300,200)

        self.container = QVBoxLayout(self)
        
        self.container.addLayout(self.gridlayout)
        #self.setLayout(self.container)
        
        self.cbox = QComboBox(self)
        self.normalMessage = "Normal Operation"
        self.cbox.addItem(self.normalMessage)
        self.cbox.addItem("From FileName: Track - Art - Ttl - Alb")
        self.cbox.addItem("From FileName: Art - Ttl - Alb")
        self.cbox.addItem("From FileName: Art - Alb")
        self.cbox.addItem("Undo One Playcount")
        
        self.newMultiTextEdit("Artist")
        self.newMultiTextEdit("Composer")
        self.newMultiTextEdit("Title")
        self.newMultiTextEdit("Album")
        self.newMultiTextEdit("Genre")
        self.newMultiTextEdit("Language")
        self.newMultiTextEdit("Comment")
        self.newTextEdit("Path")
        self.newIntEdit("Rating",-MpMusic.MAX_RATING,MpMusic.MAX_RATING)
        self.newIntEdit("Play Count",-100,9999)
        self.newIntEdit("Skip Count",-100,9999)
        self.newIntEdit("Frequency",-100,9999)
        self.newIntEdit("Album Index",0,999)
        self.newIntEdit("Year",0,9999) # Y10K bug
        self.newDateEdit("Last Played")
        self.newDateEdit("Date Added")
        
        self.hbox_btn   = QHBoxLayout()
        self.btn_accept = QPushButton("Accept",self)
        self.btn_cancel = QPushButton("Cancel",self)
        self.btn_reset  = QPushButton("Restore Defaults",self)
        
        self.hbox_btn.addWidget(self.btn_reset)
        self.hbox_btn.addWidget(self.btn_cancel)
        self.hbox_btn.addWidget(self.btn_accept)

        self.container.addWidget(self.cbox)

        self.container.addLayout(self.hbox_btn)

        self.btn_reset.clicked.connect(self.reset)
        # conect buttons to duplicate the accept/rejext nature of a dialog
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_accept.clicked.connect(self.accept)
        self.cbox.currentIndexChanged.connect(self.comboBox_Changed)     
    
    def initData(self,data):
        # reset the widget state
                    
        
            #widget.addItems(["a","b","c"])
        # update the data display
        self.data = data
        self.setData()
        
        self.cbox.setHidden(not Settings.DEVMODE)
        
        self.setHidden(self.pct,not Settings.DEVMODE)
        self.setHidden(self.sct,not Settings.DEVMODE)
        self.setHidden(self.frq,not Settings.DEVMODE)
        self.setHidden(self.pth,not Settings.DEVMODE)
        self.setHidden(self.dte,not Settings.DEVMODE)

    def setData(self):
    
        
        
        for widget in self.multiList:
            # clear all multiLine Text Edit Boxes of all entries
            while len(widget) > 0:
                widget.removeItem(0)
                
        for widget in self.editList:
            widget[2].setCheckState(Qt.Unchecked)
            widget[1].setDisabled(True)

        if len(self.data) == 1 :
            self.setSingleData(self.data)
            self.setWindowTitle("Edit Song")
        else:
            self.setMultiData(self.data)
            self.setWindowTitle("Edit Multiple Songs")
            
    def setSingleData(self,data):
        #print self.editList[0]
        self.editList[self.art][1].addItem(data[0][MpMusic.ARTIST])
        self.editList[self.cmp][1].addItem(data[0][MpMusic.COMPOSER])
        self.editList[self.ttl][1].addItem(data[0][MpMusic.TITLE])
        self.editList[self.abm][1].addItem(data[0][MpMusic.ALBUM])
        self.editList[self.gen][1].addItem(data[0][MpMusic.GENRE])
        self.editList[self.lng][1].addItem(data[0][MpMusic.LANG])
        self.editList[self.com][1].addItem(data[0][MpMusic.COMMENT])
        self.editList[self.rte][1].setValue(data[0][MpMusic.RATING])
        self.editList[self.pct][1].setValue(data[0][MpMusic.PLAYCOUNT])
        self.editList[self.sct][1].setValue(data[0][MpMusic.SKIPCOUNT])
        self.editList[self.frq][1].setValue(data[0][MpMusic.FREQUENCY])
        self.editList[self.ind][1].setValue(data[0][MpMusic.SONGINDEX])
        self.editList[self.yer][1].setValue(data[0][MpMusic.YEAR])
        
        self.editList[self.pth][1].setText(data[0][MpMusic.PATH])
        self.editList[self.pth][1].setCursorPosition(0)
        
        self.editList[self.dte][1].setDateTime( DateTime.fmtToQDateTime(data[0][MpMusic.DATESTAMP] ) )
        self.editList[self.add][1].setDateTime( DateTime.fmtToQDateTime(data[0][MpMusic.DATEADDEDS]) )
        
    def setMultiData(self,data):
        #print self.editList[0]
        
        art = [ data[0][MpMusic.ARTIST  ], ]
        cmp = [ data[0][MpMusic.COMPOSER], ]
        ttl = [ data[0][MpMusic.TITLE   ], ]
        abm = [ data[0][MpMusic.ALBUM   ], ]
        gen = [ data[0][MpMusic.GENRE   ], ]
        lng = [ data[0][MpMusic.LANG    ], ]
        com = [ data[0][MpMusic.COMMENT ], ]
        
        
        dte = data[0][MpMusic.DATESTAMP]
        rte = 0 #data[0][MpMusic.RATING]
        pct = 0 #data[0][MpMusic.PLAYCOUNT]
        sct = 0 #data[0][MpMusic.SKIPCOUNT]
        frq = 0 #data[0][MpMusic.FREQUENCY]
        ind = 0;
        yer=0;
        add=data[0][MpMusic.DATEADDEDS];
        pth = fileGetPath(data[0][MpMusic.PATH]).lower()
        
        for x in range(1,len(data)):
            if data[x][MpMusic.ARTIST] not in art:
                art.append(data[x][MpMusic.ARTIST])
            if data[x][MpMusic.COMPOSER] not in cmp:
                cmp.append(data[x][MpMusic.COMPOSER])
            if data[x][MpMusic.TITLE] not in ttl:
                ttl.append(data[x][MpMusic.TITLE])
            if data[x][MpMusic.ALBUM] not in abm:
                abm.append(data[x][MpMusic.ALBUM])
            if data[x][MpMusic.GENRE] not in gen:
                gen.append(data[x][MpMusic.GENRE]) 
            if data[x][MpMusic.LANG] not in lng:
                lng.append(data[x][MpMusic.LANG])
            if data[x][MpMusic.COMMENT] not in com:
                com.append(data[x][MpMusic.COMMENT])
            if pth != fileGetPath(data[x][MpMusic.PATH]).lower() :
                pth = "<Multiple Values>"
            if dte != data[x][MpMusic.DATESTAMP]:
                dte = "<Multiple Values>"   
            if add != data[x][MpMusic.DATEADDED]:
                add = "<Multiple Values>"   
            
        if len(art) > 1:
            art = ["<Multiple Values>",] + art
        if len(cmp) > 1:
            cmp = ["<Multiple Values>",] + cmp
        if len(ttl) > 1:
            ttl = ["<Multiple Values>",] + ttl
        if len(abm) > 1:
            abm = ["<Multiple Values>",] + abm
        if len(gen) > 1:
            gen = ["<Multiple Values>",] + gen
        if len(lng) > 1:
            lng = ["<Multiple Values>",] + lng
        if len(com) > 1:
            com = ["<Multiple Values>",] + com
            
        if pth != "<Multiple Values>" :
            pth += "*.*"
            self.editList[self.pth][2].setDisabled(False)
        else:
            self.editList[self.pth][2].setDisabled(True)
            
        self.editList[self.art][1].addItems(art)
        self.editList[self.cmp][1].addItems(cmp)
        self.editList[self.ttl][1].addItems(ttl)
        self.editList[self.abm][1].addItems(abm)
        self.editList[self.gen][1].addItems(gen)
        self.editList[self.lng][1].addItems(lng)
        self.editList[self.com][1].addItems(com)
        
        self.editList[self.pth][1].setText(pth)
        self.editList[self.dte][1].setDateTime(QDateTime())
        self.editList[self.add][1].setDateTime(QDateTime())
        
        
        self.editList[self.rte][1].setValue(rte)
        self.editList[self.pct][1].setValue(pct)
        self.editList[self.sct][1].setValue(sct)
        self.editList[self.frq][1].setValue(frq)
        self.editList[self.ind][1].setValue(ind)
        self.editList[self.yer][1].setValue(yer)
          
    def getData(self):
        MULTIDATA = len(self.data) > 1
        OPERATION = self.cbox.currentIndex()

        for item in self.editList:
            if not item[2].isEnabled():
                item[2].setCheckState(Qt.Unchecked)
        for song in self.data:
            if self.editList[self.art][2].isChecked():
                song[MpMusic.ARTIST] = unicode(self.editList[self.art][1].currentText())
                
            if self.editList[self.cmp][2].isChecked():
                print unicode(self.editList[self.cmp][1].currentText())
                print self.cmp,self.lng
                song[MpMusic.COMPOSER] = unicode(self.editList[self.cmp][1].currentText())
                
            if self.editList[self.ttl][2].isChecked():
                song[MpMusic.TITLE] = unicode(self.editList[self.ttl][1].currentText())
                
            if self.editList[self.abm][2].isChecked():
                song[MpMusic.ALBUM] = unicode(self.editList[self.abm][1].currentText())
                
            if self.editList[self.gen][2].isChecked():
                song[MpMusic.GENRE] = unicode(self.editList[self.gen][1].currentText())
                
            if self.editList[self.lng][2].isChecked():
                song[MpMusic.LANG] = unicode(self.editList[self.lng][1].currentText())
                
            if self.editList[self.com][2].isChecked():
                song[MpMusic.COMMENT] = unicode(self.editList[self.com][1].currentText())
            
            if self.editList[self.rte][2].isChecked():
                if MULTIDATA :
                    song[MpMusic.RATING] += self.editList[self.rte][1].value()
                else:
                    song[MpMusic.RATING] = self.editList[self.rte][1].value()
                
                if song[MpMusic.RATING] > MpMusic.MAX_RATING:
                    song[MpMusic.RATING] = MpMusic.MAX_RATING
                if song[MpMusic.RATING] < 0:
                    song[MpMusic.RATING] = 0
                    
            if self.editList[self.pct][2].isChecked():
                if MULTIDATA :
                    song[MpMusic.PLAYCOUNT] += self.editList[self.pct][1].value()
                else:
                    song[MpMusic.PLAYCOUNT] = self.editList[self.pct][1].value()
                    
                if song[MpMusic.PLAYCOUNT] < 0:
                    song[MpMusic.PLAYCOUNT] = 0    
            
            if self.editList[self.sct][2].isChecked():
                if MULTIDATA :
                    song[MpMusic.SKIPCOUNT] += self.editList[self.sct][1].value()
                else:
                    song[MpMusic.SKIPCOUNT] = self.editList[self.sct][1].value()
                    
                if song[MpMusic.SKIPCOUNT] < 0:
                    song[MpMusic.SKIPCOUNT] = 0    
                    
            if self.editList[self.frq][2].isChecked():
                if MULTIDATA :
                    song[MpMusic.FREQUENCY] += self.editList[self.frq][1].value()
                else:
                    song[MpMusic.FREQUENCY] = self.editList[self.frq][1].value()   
                    
                if song[MpMusic.FREQUENCY] < 0:
                    song[MpMusic.FREQUENCY] = 0  
                    
            if self.editList[self.ind][2].isChecked():
                song[MpMusic.SONGINDEX] = self.editList[self.ind][1].value()  
                
            if self.editList[self.yer][2].isChecked():
                song[MpMusic.YEAR] = self.editList[self.yer][1].value()   
                
            if self.editList[self.pth][2].isChecked():
                # auto strip any quotes around the path name
                s = unicode(self.editList[self.pth][1].text())
                if s[0] in "'\"" and s[0]==s[-1]:
                    s = s[1:-1]
                song[MpMusic.PATH] = s

            if self.editList[self.dte][2].isChecked():
                dt = DateTime.QDateTimeToFmt( self.editList[self.dte][1].dateTime() );

                song[MpMusic.DATESTAMP] = dt
                song[MpMusic.DATEVALUE] = DateTime().getEpochTime(dt)
                    
            if self.editList[self.add][2].isChecked():
                dt = DateTime.QDateTimeToFmt( self.editList[self.add][1].dateTime() );
                song[MpMusic.DATEADDED] = DateTime().getEpochTime(dt)
                song[MpMusic.DATEADDEDS] = dt
            
            
            if OPERATION == 4:
                t = DateTime().getEpochTime(song[MpMusic.DATESTAMP])
                SECONDS_IN_DAY = 86400#60*60*24
                t -= song[MpMusic.FREQUENCY]*SECONDS_IN_DAY
                song[MpMusic.DATESTAMP] = DateTime().formatDateTime(t)
                song[MpMusic.DATEVALUE] = t
                song[MpMusic.PLAYCOUNT] -= 1
                #song[MpMusic.FREQUENCY] = 0
            
            song.update()
    
    def setHidden(self,row,value):
        self.editList[row][1].setHidden(value)
        self.editList[row][2].setHidden(value)
        self.editList[row][3].setHidden(value)
    
    def reset(self):
        for widget in self.editList:
            widget[2].setCheckState(Qt.Unchecked)
            widget[1].setDisabled(True)
        self.setData()
    
    def reject(self):
        self.data = None
        
        super(SongEditWindow, self).reject()
        
    def accept(self):
        
        if len(self.data) > 0 :
            self.getData()  # for the checked options set the data in the array
        self.data = None
        super(SongEditWindow, self).accept()

    def set_setEnabled_all(self,enabled=True):
        for item in self.editList:
            item[1].setEnabled(enabled)
            item[2].setEnabled(enabled)
            #item[3].setEnabled(enabled)
    def set_setEnabled_chbox(self,enabled=True):
        for item in self.editList:
            item[2].setEnabled(enabled)
            #item[2].setEnabled(enabled)
            #item[3].setEnabled(enabled) 
    def comboBox_Changed(self,index):
        if self.cbox.itemText(index) == self.normalMessage:
            self.set_setEnabled_chbox()
        else:
            self.set_setEnabled_all(False)

    def newTextEdit(self,field):
        # create a new set of widgets for editing text fields
        # each field needs a label, a check box and a line edit
        # use the check box to enable the user to change that field
        hbox  = None#QHBoxLayout()
        label = QLabel(field,self)
        check = QCheckBox("",self)
        spring = None
        edit  = QLineEdit(self)
        label.setFixedWidth(100)
        #edit.setFixedWidth(220)
        #edit.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Minimum)
        edit.setDisabled(True)
        #hbox.addWidget(label,0,Qt.AlignLeft)
        #hbox.addWidget(check,0,Qt.AlignLeft)
        #hbox.addWidget(edit ,0,Qt.AlignRight)
        self.gridlayout.addWidget(label,len(self.editList),_COL_LBL)
        self.gridlayout.addWidget(check,len(self.editList),_COL_CHK)
        self.gridlayout.addWidget(edit ,len(self.editList),_COL_EDT)
        
        check.stateChanged.connect(self.checkClicked)
        
        self.editList.append( (hbox,edit,check,label,spring) )
        
    def newDateEdit(self,field):
        # create a new set of widgets for editing Date fields
        # each field needs a label, a check box and a QDateEdit
        # use the check box to enable the user to change that field
        hbox  = None#QHBoxLayout()
        label = QLabel(field,self)
        check = QCheckBox("",self)
        spring = None
        edit  = QDateTimeEdit(self)
        label.setFixedWidth(100)
        #edit.setFixedWidth(220)
        #edit.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Minimum)
        edit.setDisabled(True)
        edit.setDisplayFormat("yyyy/MM/dd HH:mm")
        #hbox.addWidget(label,0,Qt.AlignLeft)
        #hbox.addWidget(check,0,Qt.AlignLeft)
        #hbox.addWidget(edit ,0,Qt.AlignRight)
        self.gridlayout.addWidget(label,len(self.editList),_COL_LBL)
        self.gridlayout.addWidget(check,len(self.editList),_COL_CHK)
        self.gridlayout.addWidget(edit ,len(self.editList),_COL_EDT)
        
        
        check.stateChanged.connect(self.checkClicked)
        
        edit.mouseReleaseEvent  = lambda x : debug(x);
        
        self.editList.append( (hbox,edit,check,label,spring) )
        
    def newMultiTextEdit(self,field):
        # create a new set of widgets for editing text fields
        # each field needs a label, a check box and a line edit
        # use the check box to enable the user to change that field
        hbox  = None#QHBoxLayout()
        label = QLabel(field,self)
        check = QCheckBox("",self)
        spring = None
        edit  = ComboBox(self)#QLineEdit(self)
        label.setFixedWidth(100)
        #edit.setFixedWidth(200)
        #edit.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Minimum)
        edit.setDisabled(True)
        
        #hbox.addWidget(label,0,Qt.AlignLeft)
        #hbox.addWidget(check,0,Qt.AlignLeft)
        #hbox.addWidget(edit,0,Qt.AlignRight)
        self.gridlayout.addWidget(label,len(self.editList),_COL_LBL)
        self.gridlayout.addWidget(check,len(self.editList),_COL_CHK)
        self.gridlayout.addWidget(edit ,len(self.editList),_COL_EDT)
        
        edit.setEditable(True)
        edit.addItem("<Multiple Values>")
        
        self.multiList.append(edit)
        
        check.stateChanged.connect(self.checkClicked)
        
        self.editList.append( (hbox,edit,check,label,spring) )
        
    def newIntEdit(self,field,min,max):
        # create a new set of widgets for editing text fields
        # each field needs a label, a check box and a line edit
        # use the check box to enable the user to change that field
        hbox  = None#QHBoxLayout()
        label = QLabel(field,self)
        check = QCheckBox("",self)
        spring = None
        spinbox  = QSpinBox(self)
        label.setFixedWidth(100)
        #spinbox.setFixedWidth(220)
        #spinbox.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Minimum)
        spinbox.setDisabled(True)
        spinbox.setRange(min,max)
        
        #hbox.addWidget(label,0,Qt.AlignLeft)
        #hbox.addWidget(check,0,Qt.AlignLeft)
        #hbox.addWidget(spinbox,0,Qt.AlignRight)
        self.gridlayout.addWidget(label   ,len(self.editList),_COL_LBL)
        self.gridlayout.addWidget(check   ,len(self.editList),_COL_CHK)
        self.gridlayout.addWidget(spinbox ,len(self.editList),_COL_EDT)
        
        
        check.stateChanged.connect(self.checkClicked)
        
        self.editList.append( (hbox,spinbox,check,label,spring) )
        
    def checkClicked(self,event):
        for x in self.editList:
            if x[2].isChecked() :
                x[1].setDisabled(False)
            else:
                x[1].setDisabled(True)
                 
    
if __name__ == '__main__':
    #  import sys
    #  
    #  path="M:\\discography\\discography - blind melon\\blind melon\\02 - tones of home.mp3"
    #  exif="Blind Melon|Tones of Home|Blind Melon|Rock|2010/12/05 15:48|266|5|23|0|0|0|0"
    #  exi2="Blind Melon|No Rain|Blind Melon|Rock|2010/12/05 15:48|266|5|23|0|0|0|0"
    #  song = [[]]*16;
    #  song[EXIF] = exif
    #  song[PATH] = path
    #  createSongV2(song)
    #  song2 = [[]]*16;
    #  song2[EXIF] = exi2
    #  song2[PATH] = path
    #  createSongV2(song2)
    #  data = [song,song2]
    #  
    #  app = QApplication(sys.argv)
    #  app.setApplicationName("Console Player")
    #  app.setQuitOnLastWindowClosed(True)
    #  # create a window with no parent at 200 200 and data
    #  window = SongEditWindow(None)
    #  #window.Renew(data)
    #  window.show()
    #  
    #  
    #  sys.exit(app.exec_())
    pass
    
    
