from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from widgetLineEdit import *

from widgetTree import * 

# i am getting bizarre import errors,
# from MpApplication import MainWindow Fails. for no obvious reason


from MpSort import *
from Song_Search import *
import MpScripting
import MpCommands

class helpDialog(QDialog):
    def __init__(self,parent=None):
        super(QDialog,self).__init__(parent)
        self.setWindowTitle("Console Player Help")
        self.resize(750, 350)
        
        # ###################################
        # create widgets
        self.tree = HelpTree(self,["Help Options",]);
        self.disp = QTextEdit(self);
        self.hbox = QHBoxLayout(self);
        
        # ###################################
        # set defaults
        
        self.tree.setFixedWidth(200)

        self.disp.setAcceptRichText(True)
        self.disp.setReadOnly(True)
        # ###################################
        # add widgets to dialog
        self.hbox.addWidget(self.tree);
        self.hbox.addWidget(self.disp);
  
        self.setData()

        return;
    def setData(self,varient=None):

        
        prompt_start = self.docToHtml(ReadableDocs(MpApplication.MainWindow))
        prompt_quick = self.docToHtml(ReadableDocs(tab_quickselect.Table_Quick))
        prompt_list = self.docToHtml(ReadableDocs(table_playlist.TablePlayList))
        
        prompt_search = self.docToHtml(ReadableDocs(SearchObject))
         
        prompt_command = self.docToHtml(ReadableDocs(MpCommands.processTextInput))
        
        ch_start = self.tree.addParent("Getting Started",prompt_start) #
        ch_list = self.tree.addParent("PlayLists",prompt_list) #
        ch_search = self.tree.addParent("Search",prompt_search) #
        ch_cmd    = self.tree.addParent("Commands",prompt_command) #
        ch_quick = self.tree.addParent("Quick Selection",prompt_quick) #
        
         #self.tree.insertParent(3,["insert Parent",],"no data")
        
         #print self.tree.topLevelItemCount()
        
        global CommandList
        k = lambda x: x[0]
        R = sorted(CommandList.items(), key = k)
        for name,fptr in R : 
            if fptr == None:
                continue;
            doc = ReadableDocs(fptr)
            if doc[:3] != 'DEV':
                i = doc.find('\n')
                r = doc[i+7:doc.find('\n',i+1)].strip()
                if r == name and doc[i+1]=='A': 
                    #print name
                    continue
                            
                self.tree.addChild(ch_cmd,name,self.docToHtml(doc))
         # add seaching information.
        doc = ReadableDocs(SearchObject.compile)
        self.tree.addChild(ch_search,"Dot Words",self.docToHtml(doc))
        
        doc = ReadableDocs(SearchObject._parseFrame)
        self.tree.addChild(ch_search,"Special Characters",self.docToHtml(doc))
        
        self.disp.setHtml(prompt_start)
        #print "c"
        if ch_start != None:
            self.tree.setCurrentItem(ch_start,0)

      
    def docToHtml(self,doc):

        html = stringToHTMLString(doc)
        html = HTMLString_StyleHeader(html)
        return html
        
    def sizeHint(self):
        return QSize(750,350);

class dialogAbout(QDialog):
    """ 
        Dilog About is in this file becuase there is really nothing to it.
    """
    def __init__(self,parent=None):
        super(dialogAbout,self).__init__(parent)
        self.setWindowTitle("About")
        string ="<font size=\"5\">Console Player</font><br>"
        string+="Author: Nick Setzer<br>"
        string+="A music player and library manager for Windows Xp, Vista and 7 as well as linux (Ubuntu) and Mac (maybe?)<br><br>"
        string+="Console Player is written in Python using PyQt, and VLC for media playback.<br><br>"
        string+="Audio tag detection is done with the Mutagen library."

        
        p_icon = QPixmap(MpGlobal.installPath+"icon.png")# pix buffer for icon
        lbl_image = QLabel(self)
        lbl_image.setPixmap(p_icon);
        
        lbl = QTextEdit(string,self)
        #lbl.setWordWrap(True)
        #lbl.setTextFormat(Qt.RichText)

        btn = QPushButton("OK")
        btn.setMaximumWidth(48);
        
        lbl.setAcceptRichText(True)
        lbl.setReadOnly(True)
        
        hbox = QHBoxLayout()
        hbox.addWidget(lbl_image)
        hbox.addWidget(lbl)

        vbox = QVBoxLayout(self)
        vbox.addLayout(hbox)
        vbox.addWidget(btn,Qt.AlignRight)
        
        btn.clicked.connect(self.accept)
        
        self.setMaximumWidth(450);
        self.setMaximumHeight(200);
    #def resizeEvent(self,event): 
    #    print self.height()       
    def sizeHint(self):
        return QSize(450,200)

class HelpTree(TreeWidget):

    def mouseReleaseEvent(self,event=None):
        super(HelpTree,self).mouseReleaseEvent(event)

        if event:
            index = self.indexAt(event.pos())
            item = self.getItem(index) # converts an index to a TreeItem
            if item != None:
                if event.button() == Qt.RightButton :
                    pass
                elif event.button() == Qt.LeftButton :
                    self.parent.disp.setHtml(unicode(item.data))
                    self.setCurrentItem(item,0) # highlight the item of the displayed text
        return; 
  
  
from StringParser import StringParse 

from MpCommands import *
from MpScripting import *

 
import  MpApplication
import  table_playlist   
import tab_quickselect   
  
if __name__ == "__main__":

    def main(argv=None):
    
        global Window  
        
        if argv is None:
            argv = sys.argv
          
        Window = helpDialog();
        print "window show enter"
        Window.show();
        
        print "window show exit"
        
    global Application
    Application = QApplication(sys.argv)
    Application.setApplicationName("New Project")
    Application.setQuitOnLastWindowClosed(True)

    main()

    sys.exit(Application.exec_())