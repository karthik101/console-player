from PyQt4.QtCore import *
from PyQt4.QtGui import *
from MpGlobalDefines import *
from Song_Object import Song
from datatype_hex64 import *
from MpFileAccess import *
from SystemPathMethods import *
from widgetLineEdit import *
import time
from calendar import timegm


class SongEditWindow(QDialog):
        
    editList = []   # list of tuples of widgets
    multiList = []    
        
    art = 0 # string
    ttl = 1 # string
    abm = 2 # string
    gen = 3 # string
    com = 4
    rte = 5 # int
    pct = 6 # int
    sct = 7 # int
    frq = 8 # int
    ind = 9 # int
    yer =10
    dte =11 # string
    pth =12 # string
    add =13

    def __init__(self,parent):

        super(SongEditWindow, self).__init__(parent)
        
        self.editList = []
        self.multiList = []   
        
        #self.setWindowIcon(QIcon('icon.png'))
        
        #self.resize(300,200)

        self.container = QVBoxLayout(self)
        #self.setLayout(self.container)
        
        self.cbox = QComboBox(self)
        self.normalMessage = "Normal Operation"
        self.cbox.addItem(self.normalMessage)
        self.cbox.addItem("From FileName: Track - Art - Ttl - Alb")
        self.cbox.addItem("From FileName: Art - Ttl - Alb")
        self.cbox.addItem("From FileName: Art - Alb")
        self.cbox.addItem("Undo One Playcount")
        
        
        
        self.editList.append(self.newMultiTextEdit("Artist"))
        self.editList.append(self.newMultiTextEdit("Title"))
        self.editList.append(self.newMultiTextEdit("Album"))
        self.editList.append(self.newMultiTextEdit("Genre"))
        self.editList.append(self.newMultiTextEdit("Comment"))
        self.editList.append(self.newIntEdit("Rating",-5,5))
        self.editList.append(self.newIntEdit("Play Count",-100,9999))
        self.editList.append(self.newIntEdit("Skip Count",-100,9999))
        self.editList.append(self.newIntEdit("Frequency",-100,9999))
        self.editList.append(self.newIntEdit("Album Index",0,999))
        self.editList.append(self.newIntEdit("Year",0,9999)) # Y10K bug
        
        
        self.editList.append(self.newTextEdit("Last Played"))
        self.editList.append(self.newTextEdit("Path"))
        
        self.editList.append(self.newTextEdit("Date Added"))

        self.hbox_btn   = QHBoxLayout()
        self.btn_accept = QPushButton("Accept",self)
        self.btn_cancel = QPushButton("Cancel",self)
        self.btn_reset  = QPushButton("Restore Defaults",self)
        
        self.hbox_btn.addWidget(self.btn_reset)
        self.hbox_btn.addWidget(self.btn_cancel)
        self.hbox_btn.addWidget(self.btn_accept)
        #self.editList.append(self.newTextEdit("File Name"))

        self.container.addWidget(self.cbox)

        for x in self.editList:
            self.container.addLayout(x[0]) 
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
        
        
        
        #self.move(200,200) # dialogs autocenter on parentand auto size
        #self.resize(-1,-1)

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
        self.editList[self.ttl][1].addItem(data[0][MpMusic.TITLE])
        self.editList[self.abm][1].addItem(data[0][MpMusic.ALBUM])
        self.editList[self.gen][1].addItem(data[0][MpMusic.GENRE])
        self.editList[self.com][1].addItem(data[0][MpMusic.COMMENT])
        self.editList[self.rte][1].setValue(data[0][MpMusic.RATING])
        self.editList[self.pct][1].setValue(data[0][MpMusic.PLAYCOUNT])
        self.editList[self.sct][1].setValue(data[0][MpMusic.SKIPCOUNT])
        self.editList[self.frq][1].setValue(data[0][MpMusic.FREQUENCY])
        self.editList[self.ind][1].setValue(data[0][MpMusic.SONGINDEX])
        self.editList[self.yer][1].setValue(data[0][MpMusic.YEAR])
        
        self.editList[self.pth][1].setText(data[0][MpMusic.PATH])
        self.editList[self.pth][1].setCursorPosition(0)
        
        self.editList[self.dte][1].setText(data[0][MpMusic.DATESTAMP])
        self.editList[self.add][1].setText(str(data[0][MpMusic.DATEADDEDS]))
        
    def setMultiData(self,data):
        #print self.editList[0]
        
        art = [ data[0][MpMusic.ARTIST ], ]
        ttl = [ data[0][MpMusic.TITLE  ], ]
        abm = [ data[0][MpMusic.ALBUM  ], ]
        gen = [ data[0][MpMusic.GENRE  ], ]
        com = [ data[0][MpMusic.COMMENT], ]
        
        
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
            if data[x][MpMusic.TITLE] not in ttl:
                ttl.append(data[x][MpMusic.TITLE])
            if data[x][MpMusic.ALBUM] not in abm:
                abm.append(data[x][MpMusic.ALBUM])
            if data[x][MpMusic.GENRE] not in gen:
                gen.append(data[x][MpMusic.GENRE]) 
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
        if len(ttl) > 1:
            ttl = ["<Multiple Values>",] + ttl
        if len(abm) > 1:
            abm = ["<Multiple Values>",] + abm
        if len(gen) > 1:
            gen = ["<Multiple Values>",] + gen
        if len(com) > 1:
            com = ["<Multiple Values>",] + com
            
        if pth != "<Multiple Values>" :
            pth += "*.*"
            self.editList[self.pth][2].setDisabled(False)
        else:
            self.editList[self.pth][2].setDisabled(True)
            
        self.editList[self.art][1].addItems(art)
        self.editList[self.ttl][1].addItems(ttl)
        self.editList[self.abm][1].addItems(abm)
        self.editList[self.gen][1].addItems(gen)
        self.editList[self.com][1].addItems(com)
        
        self.editList[self.pth][1].setText(pth)
        self.editList[self.dte][1].setText(dte)
        self.editList[self.add][1].setText(add)
        
        
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
                
            if self.editList[self.ttl][2].isChecked():
                song[MpMusic.TITLE] = unicode(self.editList[self.ttl][1].currentText())
                
            if self.editList[self.abm][2].isChecked():
                song[MpMusic.ALBUM] = unicode(self.editList[self.abm][1].currentText())
                
            if self.editList[self.gen][2].isChecked():
                song[MpMusic.GENRE] = unicode(self.editList[self.gen][1].currentText())
            
            if self.editList[self.com][2].isChecked():
                song[MpMusic.COMMENT] = unicode(self.editList[self.com][1].currentText())
            
            if self.editList[self.rte][2].isChecked():
                if MULTIDATA :
                    song[MpMusic.RATING] += self.editList[self.rte][1].value()
                else:
                    song[MpMusic.RATING] = self.editList[self.rte][1].value()
                
                if song[MpMusic.RATING] > 5:
                    song[MpMusic.RATING] = 5
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
                song[MpMusic.PATH] = unicode(self.editList[self.pth][1].text())

            if self.editList[self.dte][2].isChecked():
                date = str(self.editList[self.dte][1].text())
                t = getEpochTime(date)
                if t != 0:
                    song[MpMusic.DATESTAMP] = date
                    song[MpMusic.DATESTAMP] = t
                    
            if self.editList[self.add][2].isChecked():
                date = str(self.editList[self.add][1].text())
                t = getEpochTime(date)
                if t != 0:
                    song[MpMusic.DATEADDEDS] = date
                    song[MpMusic.DATEADDED]  = t
            
            
            if OPERATION == 4:
                t = getEpochTime(song[MpMusic.DATESTAMP])
                SECONDS_IN_DAY = 86400#60*60*24
                t -= song[MpMusic.FREQUENCY]*SECONDS_IN_DAY
                song[MpMusic.DATESTAMP] = secondsToFString(t)
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
        hbox  = QHBoxLayout()
        label = QLabel(field,self)
        check = QCheckBox("",self)
        spring = None
        edit  = QLineEdit(self)
        label.setFixedWidth(100)
        edit.setFixedWidth(220)
        edit.setDisabled(True)
        hbox.addWidget(label,0,Qt.AlignLeft)
        hbox.addWidget(check,0,Qt.AlignLeft)
        hbox.addWidget(edit ,0,Qt.AlignRight)
        
        check.stateChanged.connect(self.checkClicked)
        
        return (hbox,edit,check,label,spring)
        
    def newMultiTextEdit(self,field):
        # create a new set of widgets for editing text fields
        # each field needs a label, a check box and a line edit
        # use the check box to enable the user to change that field
        hbox  = QHBoxLayout()
        label = QLabel(field,self)
        check = QCheckBox("",self)
        spring = None
        edit  = ComboBox(self)#QLineEdit(self)
        label.setFixedWidth(100)
        edit.setFixedWidth(200)
        edit.setDisabled(True)
        hbox.addWidget(label,0,Qt.AlignLeft)
        hbox.addWidget(check,0,Qt.AlignLeft)
        hbox.addWidget(edit,0,Qt.AlignRight)

        edit.setEditable(True)
        edit.addItem("<Multiple Values>")
        
        # relevent edit functions:
        # __len__
        # removeItem(int)
        # addItem(String)
        # currentText()
        
        self.multiList.append(edit)
        
        check.stateChanged.connect(self.checkClicked)
        
        return (hbox,edit,check,label,spring)
        
    def newIntEdit(self,field,min,max):
        # create a new set of widgets for editing text fields
        # each field needs a label, a check box and a line edit
        # use the check box to enable the user to change that field
        hbox  = QHBoxLayout()
        label = QLabel(field,self)
        check = QCheckBox("",self)
        spring = None
        spinbox  = QSpinBox(self)
        label.setFixedWidth(100)
        spinbox.setFixedWidth(220)
        spinbox.setDisabled(True)
        spinbox.setRange(min,max)
        hbox.addWidget(label,0,Qt.AlignLeft)
        hbox.addWidget(check,0,Qt.AlignLeft)
        hbox.addWidget(spinbox,0,Qt.AlignRight)
        
        check.stateChanged.connect(self.checkClicked)
        
        return (hbox,spinbox,check,label,spring)
        
    def checkClicked(self,event):
        for x in self.editList:
            if x[2].isChecked() :
                x[1].setDisabled(False)
            else:
                x[1].setDisabled(True)
                
def getEpochTime( date ):
    """return epoch time for a date"""
    datetime = None
    try:
        datetime = time.strptime(date,"%Y/%m/%d %H:%M")
        return timegm(datetime)   
    except:
        pass
        
    return 0     

def secondsToFString(sec):
    structtime = time.gmtime(sec)
    return time.strftime("%Y/%m/%d %H:%M",structtime)
    
if __name__ == '__main__':
    import sys
    from MpFileAccess import createSongV2
    
    path="M:\\discography\\discography - blind melon\\blind melon\\02 - tones of home.mp3"
    exif="Blind Melon|Tones of Home|Blind Melon|Rock|2010/12/05 15:48|266|5|23|0|0|0|0"
    exi2="Blind Melon|No Rain|Blind Melon|Rock|2010/12/05 15:48|266|5|23|0|0|0|0"
    song = [[]]*16;
    song[EXIF] = exif
    song[PATH] = path
    createSongV2(song)
    song2 = [[]]*16;
    song2[EXIF] = exi2
    song2[PATH] = path
    createSongV2(song2)
    data = [song,song2]
    
    app = QApplication(sys.argv)
    app.setApplicationName("Console Player")
    app.setQuitOnLastWindowClosed(True)
    # create a window with no parent at 200 200 and data
    window = SongEditWindow(None)
    #window.Renew(data)
    window.show()

    
    sys.exit(app.exec_())