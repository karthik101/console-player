# #########################################################
# #########################################################
# File: MpApplication
# Description:
#       The creation of the main window, as well as definitions
#   of all widgets can be found here, helper functions to these
#   widgets can be found at the bottom of the file
#       see the respective widgetX files for other widget definitions
#       See MpScripting for more specific functions
#   In general, functions in this file should be related to
#       Qt Slots, or callbacks from widgets
# #########################################################

import sys
import os

isPosix = os.name == 'posix'

import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import dialogSongEdit
import dialogColumnSelect
import dialogSync


from widgetPage import *

from widgetLineEdit import LineEdit

from MpGlobalDefines import *
from Song_Object import Song
from Song_LibraryFormat import *

from datatype_hex64 import *

from widgetLargeTable import LargeTable

from table_playlist import *

from frame_main import *

from tab_explorer import * 
from tab_playlist_editor import * 
from tab_library import *
from tab_quickselect import *

from widget_playbutton import *
from widget_currentSongDisplay import *
from widget_currentTimeDisplay import *

from App_EventManager import EventManager

from MpSongHistory import *

from Qt_CustomStyle import *

_STATUS_BAR_VISIBLE = True; #ach! hans, run! a global.
# ######################################
# Main Window Class
# ######################################

class MainWindow(QMainWindow):
    """
        Getting Started
       
        Load music into the application by dragging and dropping music files or folders.
        
        Type 'new' in the command line and press enter.
        
        read the help.
    """
    tbl_playlist=None;
    tab_library=None;

    syncDialogObj = None
    
    btn_playstate = None;
    
    tab_Explorer = 2 
    
    window = None;
    ui = None;      # the bare bones user interface
    geometry = None
    playListWidth = 300
    dialogSongEdit = None
    
    editorTabs = [] # list of open playlists as array of tuples 
    #(index,page,vbox,edit,tbl_left,tbl_rite,splitter)
    edit_ed = 3 # location to access elements in the editorTab Array of tuples
    edit_tl = 4
    edit_tr = 5
    
    style_dict = {} # dictionary of style colors (in QColor Form)
    
    def debugMsg(self,string,retail=False):
        """ print a string to the debug text buffer"""
        txt = MpGlobal.Window.txt_debug
        # move the cursor to the end of the text buffer
        txt.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
        # insert the text
        txt.insertPlainText(string)
        # move the cursor again to ensure new text is visible
        txt.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
        
        if Settings.DEVMODE == True or retail:
            MpGlobal.Window.txt_debug.show()
               
    def debugMsgReturn(self,string=None):
        """
            Erase the last line of the debug text box
            if a string is provided, the last line is replaced
            with string
        """
        txt = MpGlobal.Window.txt_debug
        s = txt.toPlainText();
        s = s[:s.rfind("\n")];
        if string != None:
            s += string;
        txt.setPlainText(s);
        txt.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
    
    def debugClear(self):
        txt = MpGlobal.Window.txt_debug
        txt.setPlainText("");
        
    def __init__(self,title):
        super(QMainWindow, self).__init__()
        
        self.setWindowTitle(title)
        self.setMinimumSize(230,110) 
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptDrops(True);
        self.setWindowIcon(QIcon(MpGlobal.FILEPATH_ICON))
        
        self.move  ( Settings.SCREEN_POSITION_X ,Settings.SCREEN_POSITION_Y )
        
        if Settings.WINDOW_MAXIMIZED :
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.resize( Settings.SCREEN_POSITION_W ,Settings.SCREEN_POSITION_H )
        
        # --------------------------------
        
        self.init_Ui()
         
        self.init_DisplaySong()   

        init_MenuBar(self)
        self.init_StatusBar()
        
        # --------------------------------------
        
        self.tab_library = Tab_Library(self)
        
        self.tab_quickselect = Tab_QuickSelect()
        self.tab_quickselect.setIcon(MpGlobal.icon_favpage)
        
        self.tab_explorer = Tab_Explorer()
        self.tab_explorer.setIcon(MpGlobal.icon_Folder)
        
        self.init_ConnectSignals() # do this last, after creating all objects
        
        self.txt_main.setFocus()
        
        self.pixmap_dndMusic = MpGlobal.pixmap_Song #TODO what is this
        
        if Settings.DEVMODE == False:
            self.txt_debug.hide()
        
        D = self.get_defaultColorDict()

        if Settings.THEME != "none":
            D = style_set_custom_theme(MpGlobal.installPath,Settings.THEME,MpGlobal.Application,D,Settings.USE_CUSTOM_THEME_COLORS)
        
        self.set_colorFromCssDict(D)
            
    def init_Ui(self):

        self.splitter = QSplitter(Qt.Horizontal,self)

        self.frame_main = Frame_Main(self)
        
        
        self.spt_left = QSplitter(Qt.Vertical, self)
        
        self.splitter.addWidget(self.spt_left)
        self.splitter.insertWidget(Settings.PLAYLIST_SIDE,self.frame_main) # for insertion to left or right use 0=left, 1=right

        self.tabMain = QTabWidget(self)
        
        #self.txt_searchBox = self.tab_library.txt_searchBox
        #self.search_label = self.tab_library.search_label
        #self.tabMain.addTab(self.tab_library,, "Library")        

        self.txt_debug = QPlainTextEdit("...",self)
        
        self.txt_debug.setEnabled(True)
        #self.txt_debug.setMaximumHeight(320)
        self.txt_debug.setReadOnly(True)
        
        self.spt_left.addWidget(self.tabMain)
        self.spt_left.addWidget(self.txt_debug)

        self.setCentralWidget(self.splitter)
        
        self.statusbar = QStatusBar(self)
        self.menubar = QMenuBar(self)
        
        self.setStatusBar(self.statusbar)
        self.setMenuBar(self.menubar)

        self.tabMain.setCurrentIndex(0)
        # this sets a minimum size for the left side of the splitter
        # this also enables contained widgets to be resized freely
        self.tabMain.setMinimumSize(100,100) 

        
    def init_DisplaySong(self):
        pass

    def init_StatusBar(self):
        lbl1 = QLabel("0 Selected")
        lbl2 = QLabel("PlayList Length")
        lbl3 = QLabel("Search Terms: 0")
        lbl4 = QLabel("...")

        lbl3.setToolTip("No Search Terms")
        
        self.statusbar.addWidget(lbl1,.1)
        self.statusbar.addPermanentWidget(lbl2)
        self.statusbar.addWidget(lbl3)
        self.statusbar.addWidget(lbl4)
        
        self.statusWidgets = [lbl1,lbl2,lbl3,lbl4]
        #statusWidgets[2].setToolTip(string)
    def init_ConnectSignals(self):
        """
            connect custom signals that can be emmitted from the
            seconday thread
        """
        self.btn_prev.clicked.connect(button_music_prev)
        self.btn_next.clicked.connect(button_music_next)
        
        self.tabMain.currentChanged.connect(tabbar_tab_changed)

        self.splitter.splitterMoved.connect(splitter_resize_control)
        # connect signals for the QThread to Use
        QObject.connect(self, SIGNAL("DEBUG_MESSAGE"),debug, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("DIAG_MESSAGE"),self.debugMsg, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("UPDATE_TIMEBAR"),self.bar_time.periodicUpdate, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("UPDATE_TIMEBARMAXVAL"),self.bar_time.setMaximum, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("UPDATE_TIMEINFO"),self.dsp_info.updateTime, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("UPDATE_INDEXINFO"),self.dsp_info.updateIndex, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("UPDATE_STATUSBAR"),UpdateStatusWidget, Qt.QueuedConnection)
        
        #TODO is this signal depreciated?
        QObject.connect(self, SIGNAL("UPDATE_PLAYBUTTON"),self.btn_playstate.updateDisplay, Qt.QueuedConnection)
        
        QObject.connect(self, SIGNAL("UPDATE_INFODISPLAY"),info_UpdateDisplay, Qt.QueuedConnection)
        
        QObject.connect(self, SIGNAL("QUEUE_FUNCTION"),Queue_FunctionCall, Qt.QueuedConnection)
        
        QObject.connect(self, SIGNAL("SET_PLAYBUTTON_ICON"),button_PlayPause_setPlayIcon, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("SET_CONTBUTTON_ICON"),button_PlayPause_setContIcon, Qt.QueuedConnection)
        
        QObject.connect(self, SIGNAL("FILL_PLAYLIST"),self.tbl_playlist.updateTable, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("FILL_LIBRARY"),self.tab_library.table.updateTable, Qt.QueuedConnection)

        self.xcut_fconsole = QShortcut(QKeySequence(r"Ctrl+K"),self)
        self.xcut_flibrary = QShortcut(QKeySequence(r"Ctrl+L"),self)
        self.xcut_togdebug = QShortcut(QKeySequence(Qt.Key_Escape),self)
        
        self.xcut_fconsole.activated.connect(self.__Action_shortcut_console__)
        self.xcut_flibrary.activated.connect(self.__Action_shortcut_library__)
        self.xcut_togdebug.activated.connect(self.__Action_shortcut_toggle_debug__)
  
    def sizeHint(self):
        return QSize(660, 305)
    
    #def minimumSizeHint(self):
    #    return QSize( MpGlobal.SplitterWidthMin,50)
        
    def resizeEvent(self,event):  
        #self.tbl_playlist.table.setColumnWidth(1,self.tbl_playlist.table.width())
        global _STATUS_BAR_VISIBLE;

        w = self.width()
        h = self.height()

        wthresh = 300;
        hthresh1 = 200;
        hthresh2 = 200;
        if w < wthresh:
            self.spt_left.hide()
            MpGlobal.Window.statusWidgets[2].hide();
            MpGlobal.Window.statusWidgets[3].hide();
        
        else:   
            MpGlobal.Window.statusWidgets[2].show();
            MpGlobal.Window.statusWidgets[3].show();
            self.spt_left.show()
            tsize = sum ( MpGlobal.Window.splitter.sizes() )
            
            lsize = tsize - self.playListWidth
            psize = self.playListWidth
            if self.splitter.widget(0) == self.frame_main:
                new_sizes = [psize,lsize]
            else:
                new_sizes = [lsize,psize]
                
            self.splitter.setSizes(new_sizes)
        
        
        #if h < hthresh1:
        #    self.tbl_playlist.container.hide()
        #    self.btn_clr.hide()
        #    self.btn_sfl.hide()
        #    self.btn_apl.hide()
        #    self.btn_spn.hide()
        #    self.spt_left.hide()
        #    self.statusbar.hide()
        #    self.menubar.hide()
        if h < hthresh2:
            self.tbl_playlist.container.hide()
            self.btn_clr.hide()
            self.btn_sfl.hide()
            self.btn_apl.hide()
            self.btn_spn.hide()
            self.spt_left.hide()
            self.statusbar.hide()
            self.menubar.hide()
        else:    
            self.tbl_playlist.container.show()
            self.btn_clr.show()
            self.btn_sfl.show()
            self.btn_apl.show()
            self.btn_spn.show()
            if (_STATUS_BAR_VISIBLE):
                self.statusbar.show()
            self.menubar.show()
            if w >= wthresh:
                self.spt_left.show()

    def closeEvent(self,event):
        On_Close_Save_Data()
         
        if Settings.SCREENSAVER_ENABLE_CONTROL and MpGlobal.SSService != None:
            MpGlobal.SSService.Reset()
        print "Closing Threads"    
        if MpGlobal.PlayerThread != None:
            MpGlobal.PlayerThread.exit(0)
        
        disableHook()
        
        print "Closing Application"    
        # frequently have crashes on close 
        # use the print to determine before or after
        
        event.accept()
    
    def changeEvent(self,event):
        """ grey out the icons in the menu bar """
        if event.type() == QEvent.ActivationChange:
            if MpGlobal.Application.activeWindow() != None:
                if self.menu_vol != None and not isPosix:
                    self.menu_vol.setIcon(MpGlobal.icon_volume)
            else:
                if self.menu_vol != None and not isPosix:
                    self.menu_vol.setIcon(MpGlobal.icon_volumeOOF)

    def dragEnterEvent(self,event):
        event.accept() # enable drops by accepting event
    
    def dropEvent(self,event):

        #print "received drop from <%s>"%event.source()
        if event.source() == None: # event comes from outside the application
            mdata = event.mimeData()
            #print list(mdata.formats())
            if mdata.hasUrls() :
                event.accept() # accept before processinf or explorer will hang
                url_list = mdata.urls()
                for x in range(len(url_list)):
                    if not url_list[x].isRelative() :
                        # usrl_list  is alist of urls, but they are not URI-escaped for some reason on both windows and ubuntu Natty Narwhal
                        # the file:// needs to be removed, and on windows there are 3 slashes not 2
                        # on linux the third slash is also the first slash of the file path
                        if isPosix:
                            fpath = url_list[x].toString().replace("file://","") 
                        else:
                            fpath = url_list[x].toString().replace("file:///","") 
                        #print fpath
                        fext = fileGetExt(fpath)
                        # now accept unicode filepaths
                        if pathMatchExt(fpath): #and pathIsUnicodeFree(fpath):
                            MpGlobal.EventHandler.postEvent(event_load_song,fpath)

                        elif os.path.isdir(fpath):
                            MpGlobal.EventHandler.postEvent(event_load_folder,fpath)
                        #elif XML file drop
                        #elif M3U file drop # ask whether to load songs into library or play
                        #elif playlist file drop (and etc) # play this list
                        elif fext == 'log':
                            history_load(fpath,MpGlobal.Player.library)

                Player_set_unsaved();
                
    def setTheme(self,name='default'):
        D = style_set_custom_theme(MpGlobal.installPath,name,MpGlobal.Application)
        self.set_colorFromCssDict(D)

        return (D != None)
        
    def get_defaultColorDict(self):
        return {
            
            "theme_p_mid"        : "#757575",
            "theme_s_mid"        : "rgb(200,85,0)",
            "theme_bg_color"     : "rgb(30,35,40)",
            "theme_very_light"   : "#FFFFFF",
            "theme_neutral"      : "#404040",
            "theme_very_dark"    : "#000000",
            #-----------------------------------------------------------
            "font_size"       : "12",            
            "font_family"     : "Verdana",            
            "text_color"      : "#000000",            
            "text_light"      : "#EEEEEE",          
            "text_dark"       : "#000000",             
            
            "text_important1" : "rgb(255,200,100)",           
            "text_important2" : "rgb(255,5,5)",           
            #-----------------------------------------------------------                                                  
            "color_highlight"   : "rgb(51,153,255)",  
            "color_highlightOOF": "rgba(51,200,255,.5)",    
            
            "color_special1"    : "rgb(150,50,128)", 
            "color_special2"    : "rgba(255,0,0,.1)",   
            "color_special3"    : "rgba(255,255,0,.1)", 

            "color_invalid"     : "rgba(255,5,5,.5)", 
            #-----------------------------------------------------------                                                  
            # secret
            "prompt_valid"      : "#08550E",
            "prompt_warn"       : "#FF6600",
            "prompt_error"      : "#CC0800",
            "prompt_unknown"    : "#FFFF00",
            "prompt_spec"       : "#0000EE",
            
            }
            
        #self.set_colorFromCssDict(dict)
        
    def set_colorFromCssDict(self,dict):
        """
            given a dictionary of key=>value
            pairs from a style dictionary file
            convert these values into a QColor Dictionary
        """
        if dict == None:
            return;
        cdict = self.get_defaultColorDict() # default values, then replace with values from dict
    
        # the companion values for the next 3 can be recreated
        cdict = css_dict_value("theme_p_mid",cdict,dict);
        cdict = css_dict_value("theme_s_mid",cdict,dict);
        cdict = css_dict_value("theme_bg_color",cdict,dict);
        
        cdict = css_dict_value("theme_very_light",cdict,dict);
        cdict = css_dict_value("theme_neutral",cdict,dict);
        cdict = css_dict_value("theme_very_dark",cdict,dict);

  
        cdict = css_dict_value("text_color",cdict,dict);
        cdict = css_dict_value("text_light",cdict,dict);
        cdict = css_dict_value("text_dark",cdict,dict);
                
        cdict = css_dict_value("text_important1",cdict,dict);
        cdict = css_dict_value("text_important2",cdict,dict);
                
        cdict = css_dict_value("color_highlight",cdict,dict);
        cdict = css_dict_value("color_highlightOOF",cdict,dict);
        cdict = css_dict_value("color_special1",cdict,dict);
        cdict = css_dict_value("color_special2",cdict,dict);
        cdict = css_dict_value("color_special3",cdict,dict);
        cdict = css_dict_value("color_invalid",cdict,dict);
        
        if "font_size" in dict:
            cdict["font_size"] = dict["font_size"]
        if "font_family" in dict:
            cdict["font_family"] = dict["font_family"]
        # using style_dict, now set object's color properties

        self.style_dict = cdict;
        
        self.update_widget_colors()
        
    def update_widget_colors(self):    

        self.tbl_playlist.setRowHighlightComplexRule(0,None,self.style_dict["color_special1"])
        self.tbl_playlist.setRowTextColorComplexRule(0,None,self.style_dict["text_important2"])

        self.tab_library.table.setRuleColors( \
            self.style_dict["text_important1"], \
            self.style_dict["text_important2"], \
            self.style_dict["theme_p_mid"]    , \
            self.style_dict["color_special1"] )

        # for all open tabs upadte any tables that need updating
        for i in range( self.tabMain.count() ):
            tab = self.tabMain.widget(i)
            if isinstance(tab,Tab_PlaylistEditor):
                tab.table_library.setRuleColors( \
                    self.style_dict["text_important1"], \
                    self.style_dict["text_important2"], \
                    self.style_dict["theme_p_mid"]    , \
                    self.style_dict["color_special1"] )
                tab.table_playlist.setRuleColors( \
                    self.style_dict["text_important1"], \
                    self.style_dict["text_important2"], \
                    self.style_dict["theme_p_mid"]    , \
                    self.style_dict["color_special1"] )
                    
        self.tab_library.table.setRowTextColorComplexRule(0,None,self.style_dict["text_important1"])
        # for the selected songs
        self.tab_explorer.table.setRowHighlightComplexRule(0,None,self.style_dict["color_special1"])
        
        self.dsp_info.brush_barfill = QBrush(self.style_dict["text_important1"])
        

    def setPlayListWidth(self,w) :

        tsize = sum ( self.splitter.sizes() )
        r = tsize - w
        
        if self.splitter.widget(0) == self.frame_main:
            n = [w,r]
        else:
            n = [r,w]
            
        self.splitter.setSizes( n )
         
    def __Action_New_PlayList__(self):
        """ Create a new playlist editor
        """
        tab = Tab_PlaylistEditor()
        tab.addTab( "New Playlist" )
        tab.setCloseButton()
        tab.switchTo()
            
    def __Action_Load_PlayList__(self):
        """ Create a new playlist editor and
            immediatley prompt the user to open A LIST
        """
        tab = Tab_PlaylistEditor()
        tab.addTab( "New Playlist" )
        tab.setCloseButton()
        tab.switchTo()
        if not tab.btn_click_playlist_load():
            tab.btn_click_close()

    def __Action_shortcut_library__(self):
        obj = MpGlobal.Window.tab_library.txt_searchBox
        obj.setFocus()
        obj.setSelection(0,len(obj.displayText()))
        
    def __Action_shortcut_console__(self):
        obj = MpGlobal.Window.txt_main
        obj.setFocus()
        obj.setSelection(0,len(obj.displayText()))
    def __Action_shortcut_toggle_debug__(self):
        obj = MpGlobal.Window.txt_main
        obj.setFocus()
        obj.setSelection(0,len(obj.displayText()))
        if not Settings.DEVMODE:
            toggle_DebugText_Show()
    def Action_sel_all(self):
        self.tab_library.table.selection = set(range(len(self.tab_library.table.data)));
        self.tab_library.table.updateTable();            
    def Action_sort_REVERSE(self):
        MpGlobal.Player.library.reverse()
        MpGlobal.Player.lastSortType *= -1;
        MpGlobal.Window.tab_library.table.updateTable()
        
        r = MpGlobal.Player.lastSortType>0
        ico = MpGlobal.icon_Clear
        index = r if r>=0 else -r
        if index in (MpMusic.ARTIST, MpMusic.TITLE,MpMusic.ALBUM):
            ico = MpGlobal.icon_Check if r else MpGlobal.icon_Clear
        else:
            ico = MpGlobal.icon_Clear if r else MpGlobal.icon_Check
        MpGlobal.Window.act_sfl_reverse.setIcon( ico )
    
    def Action_sort_DATESTAMP(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.DATESTAMP)
    def Action_sort_PLAYCOUNT(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.PLAYCOUNT)
    def Action_sort_FREQUENCY(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.FREQUENCY)
    def Action_sort_PATH(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.PATH)
    def Action_sort_RATING(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.RATING)
    def Action_sort_ARTIST(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.ARTIST)
    def Action_sort_TITLE(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.TITLE)
    def Action_sort_ALBUM(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.ALBUM)
    
    def Action_sort_LENGTH(self):
        self.tab_library.table.sortColumnByExifTag(MpMusic.LENGTH)
    def Action_sort_GENRE(self):                  
        self.tab_library.table.sortColumnByExifTag(MpMusic.GENRE)
    def Action_sort_FSIZE(self):                  
        self.tab_library.table.sortColumnByExifTag(MpMusic.FILESIZE)
    def Action_sort_SKIPCOUNT(self):              
        self.tab_library.table.sortColumnByExifTag(MpMusic.SKIPCOUNT)

                 
# ######################################
# Sub-Classed Qt Widgets
# ######################################

class TextEdit(QLineEdit):
    # text edit which maintains a history of previous input
    history = []
    hindex = 0;
    def __init__(self,parent=None):
        super(TextEdit,self).__init__(parent)
        self.setMinimumWidth(MpGlobal.SplitterWidthMin)
    def keyReleaseEvent(self,event):
        txt = self.displayText()
        key = event.key()
        if key == Qt.Key_Up :
            if len(self.history) > 0 :
                self.setText(self.history[self.hindex])
                if self.hindex < len(self.history) - 1:
                    self.hindex += 1
        elif key == Qt.Key_Down :
            if self.hindex > 0 :
                self.hindex -= 1
                self.setText(self.history[self.hindex])  
            else:
                self.setText("")
        elif key == Qt.Key_Enter or key == Qt.Key_Return :

            self.history.insert(0,txt) # make a copy of the item to store in the history
            self.hindex = 0;
            self.setText("")
            processTextInput(txt)   # this function passes an object, which is wiped out

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
        
class MpSTDWrite():
    def __init__(self, name):
        self.name = name
        #self.stdout = sys.stdout
        self.file = open(self.name, "w")
        self.file.write("Session log")
        self.file.close()
    def __del__(self):
        #sys.stdout = self.stdout
        pass
    def write(self, data):
        s = str(data)
        self.file = open(self.name, "a")
        self.file.write(s)
        self.file.close()
        debug(s)
        #self.stdout.write(data)  
        return

class MpSTDDebug():

    def __del__(self):
        #sys.stdout = self.stdout
        pass
        
    def write(self, data):
        uni = unicode(data).strip()
        if len(uni) > 0:
            MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),uni)
        #self.stdout.write(data)  
        return
    

# ######################################
# Event Functions
# ######################################

def init_preMainWindow():
    """
        Events to initalize after creation of the 
        QApplication but before the main windo show.
    """ 
    #MpGlobal.AudioPlayer = VLCObject()
    MpGlobal.AudioPlayer = getNewAudioPlayer()
    MpGlobal.Player = MediaManager(MpGlobal.AudioPlayer)
    MpGlobal.EventHandler = EventManager();
    
    # ######################################
    # Create the Player
    # ######################################
    MpGlobal.PlayerThread = MediaPlayerThread(MpGlobal.Window)
    MpGlobal.PlayerThread.start()
    
    registerSSService()
     
    getApplicationIcons()
    
    # init the search classes for searching through the library.
    SearchObject_Controller.getSearchDictionary   = SOC_getSearchDictionary   
    SearchObject_Controller.getFavoriteArtistList = SOC_getFavoriteArtistList                            
    SearchObject_Controller.getPresetString       = SOC_getPresetString
    
    # ######################################
    # Set Keyboard Hook
    # ######################################

    if "-devmode" not in sys.argv and Settings.MEDIAKEYS_ENABLE:
        initHook()
        debugPreboot("KeyBoard Hook Enabled")
    
    MpGlobal.Player.library = musicLoad_LIBZ(MpGlobal.FILEPATH_LIBRARY)
    #TODO: FIX THIS FUNCTION CALL
    R = playListLoad(MpGlobal.FILEPATH_PLAYLIST_CURRENT,MpGlobal.Player.library)
    if len(R) == 2:
        Settings.PLAYER_LAST_INDEX = R[0]
        MpGlobal.Player.playList = R[1]

def init_postMainWindow():
    """
        Called immediatley after window.show()
    """
    
    
    
    sortLibraryInplace(MpMusic.ARTIST)
    buildArtistList()
    
    MpGlobal.Player.libDisplay = MpGlobal.Player.library[:]
    
    MpGlobal.Window.tab_library.table.updateTable(0,MpGlobal.Player.libDisplay) 
    MpGlobal.Window.tbl_playlist.updateTable(0,MpGlobal.Player.playList) 
    
    MpGlobal.Window.setPlayListWidth(MpGlobal.Window.playListWidth)
    if not MpGlobal.Window.txt_debug.isHidden():
        splitter_resize_debug()
    
    MpGlobal.Window.tab_library.search_label.setText("%d/%d"%(len(MpGlobal.Player.libDisplay),len(MpGlobal.Player.library)))
    
    if Settings.PLAYER_LAST_INDEX < len(MpGlobal.Player.playList):
        MpGlobal.Player.CurrentIndex = Settings.PLAYER_LAST_INDEX
        
    MpGlobal.Player.loadSong()
    
    UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
    
    MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Ready, DevMode : %s"%Settings.DEVMODE)   

    MpGlobal.Window.txt_debug.setPlainText(MpGlobal.debug_preboot_string)
    MpGlobal.debug_preboot_string = "" 
    
    MpGlobal.Window.tab_library.addTab("Library")
    
    MpGlobal.Window.tab_quickselect.switchTo()
    MpGlobal.Window.tab_quickselect.addTab( "Quick Select" )
    
    MpGlobal.Window.tab_explorer.load_directory()  
    MpGlobal.Window.tab_explorer.addTab( "Explorer" )
    
    if len(sys.argv) > 1:   
        session_receive_argument(" ".join(sys.argv[1:]))    # this is yet another Yay Lazy moment, where other code does what i want.
    
    if Settings.RELEASE:
        sys.stdout = MpSTDDebug()
        sys.stderr = MpSTDDebug()

def init_MenuBar(window):
        # Main Menues
        window.menu_File  = QMenu("&File",window)
        window.menu_Lib   = QMenu("&Music",window)
        window.menu_View  = QMenu("&View",window)
        window.menu_Pref  = QMenu("&Settings",window)
        window.menu_Help  = QMenu(" &? ",window)
        window.menu_Sort  = QMenu("&Sort Library",window)
        # MEta Menues
        window.menu_pMode = QMenu("&Playback Mode",window.menu_Lib)
        
        if not isPosix:
            window.menu_vol = QMenu(window)
        else:
            window.menu_vol = None

        #----------------------------------------------------------------------
        # add Actions
        window.menu_File.addAction("E&xit",safeClose)
        
        window.menu_Lib.addAction("New Play List",show_NewPlayList_Dialog);
        window.menu_Lib.addSeparator()
        window.menu_Lib.addAction("New Editable Play List",window.__Action_New_PlayList__)
        window.menu_Lib.addAction("Open Play List",window.__Action_Load_PlayList__)
        window.menu_Lib.addSeparator()
        window.menu_Lib.addMenu(window.menu_pMode)
        
        window.act_pMode_pb1 = window.menu_pMode.addAction("New Playlist after last song finishes",setPlayBack_Mode1)
        window.act_pMode_pb2 = window.menu_pMode.addAction("Loop Same Playlist"  ,setPlayBack_Mode2)
        window.act_pMode_pb3 = window.menu_pMode.addAction("Loop Same Song"      ,setPlayBack_Mode3)
        window.act_pMode_pb4 = window.menu_pMode.addAction("Stop on Playlist End",setPlayBack_Mode4)
        
        #if Settings.DEVMODE:
        window.act_view_console   = window.menu_View.addAction("Console",toggle_Console_Show)
        window.act_view_statusbar = window.menu_View.addAction("Statusbar",toggle_Statusbar_Show)
        window.act_view_debug     = window.menu_View.addAction("Debug",toggle_DebugText_Show)
        

        window.menu_Pref.addAction("Preferences",menu_open_Settings)
        
        #----------------------------------------------------------------------
        # Sort Menu
        #window.act_sel_all       = window.menu_Sort.addAction("Select All",window.Action_sel_all) 
        window.act_sfl_reverse   = window.menu_Sort.addAction("Reverse",window.Action_sort_REVERSE) 
        window.menu_Sort.addSeparator() 
        window.act_sfl_artist    = window.menu_Sort.addAction("Artist",window.Action_sort_ARTIST   ) 
        window.act_sfl_title     = window.menu_Sort.addAction("Title",window.Action_sort_TITLE    ) 
        window.act_sfl_album     = window.menu_Sort.addAction("Album",window.Action_sort_ALBUM    ) 
        window.act_sfl_genre     = window.menu_Sort.addAction("Genre",window.Action_sort_GENRE) 
        window.act_sfl_playcount = window.menu_Sort.addAction("Play Count",window.Action_sort_PLAYCOUNT) 
        window.act_sfl_skipcount = window.menu_Sort.addAction("Skip Count",window.Action_sort_SKIPCOUNT   ) 
        window.act_sfl_length    = window.menu_Sort.addAction("Length",window.Action_sort_LENGTH   ) 
        window.act_sfl_rating    = window.menu_Sort.addAction("Rating",window.Action_sort_RATING   ) 
        window.act_sfl_freq      = window.menu_Sort.addAction("Frequency",window.Action_sort_FREQUENCY     ) 
        window.act_sfl_datestamp = window.menu_Sort.addAction("Last Played",window.Action_sort_DATESTAMP) 
        window.act_sfl_fsize      = window.menu_Sort.addAction("File Size",window.Action_sort_FSIZE    ) 
        window.act_sfl_path      = window.menu_Sort.addAction("Path",window.Action_sort_PATH     ) 
        
        #window.act_sel_all       .setShortcut(QKeySequence(r"Ctrl+A"))
        window.act_sfl_artist    .setShortcut(QKeySequence(r"Ctrl+S"))
        window.act_sfl_title     .setShortcut(QKeySequence(r"Ctrl+T"))
        window.act_sfl_album     .setShortcut(QKeySequence(r"Ctrl+B"))
        window.act_sfl_playcount .setShortcut(QKeySequence(r"Ctrl+I"))
        window.act_sfl_rating    .setShortcut(QKeySequence(r"Ctrl+R"))
        window.act_sfl_freq      .setShortcut(QKeySequence(r"Ctrl+F"))
        window.act_sfl_datestamp .setShortcut(QKeySequence(r"Ctrl+D"))
        window.act_sfl_path      .setShortcut(QKeySequence(r"Ctrl+P"))
        
        #----------------------------------------------------------------------
        # Help Menu
        window.menu_Help.addAction("Help",open_dialog_Help   ) 
        window.menu_Help.addAction("About",open_dialog_About  ) 
        
        #----------------------------------------------------------------------
        # Volume Menu
        
            
        window.volumeBar = QSlider(Qt.Horizontal,window)
        window.volumeBar.setRange(0,100)
        window.volumeBar.setValue(Settings.PLAYER_VOLUME)
        window.volumeBar.valueChanged.connect(MpGlobal.Player.setVolume)
        #window.volumeBar.setFixedWidth(100)
        
        if not isPosix:
            window.menu_vol.setIcon(MpGlobal.icon_volume)
            window.wac_vol = QWidgetAction(window.menu_vol)
            window.wac_vol.setDefaultWidget(window.volumeBar)   
            window.menu_vol.addAction(window.wac_vol)
            
        else:
            window.hbox_btn.insertWidget(1,window.volumeBar);
        #----------------------------------------------------------------------
        # add Menues to menubar
        window.menubar.addMenu(window.menu_File)
        window.menubar.addMenu(window.menu_Lib)
        window.menubar.addMenu(window.menu_View)
        window.menubar.addMenu(window.menu_Pref)
        window.menubar.addMenu(window.menu_Help)
        if not isPosix:
            window.menubar.addMenu(window.menu_vol)
        
        window.menu_Lib.addMenu(window.menu_Sort)
        
        #----------------------------------------------------------------------
        # Set Default Icons
        if Settings.DEVMODE == True:
            window.act_view_debug.setIcon(MpGlobal.icon_Check)
        window.act_view_console.setIcon(MpGlobal.icon_Check)
        window.act_view_statusbar.setIcon(MpGlobal.icon_Check)
        
        window.act_pMode_pb1.setIcon(MpGlobal.icon_Check)
        


def splitter_resize_control(pos,index):
    sizes = MpGlobal.Window.splitter.sizes()
    totalsize = sum(sizes)
    
    p = 1
    l = 0
    
    if MpGlobal.Window.splitter.widget(0) == MpGlobal.Window.frame_main:
        p=0; l=1;
    # check the size of the layouts in the main splitter
    # if they are above or below the set maximum then set them equal to that value
    
    if (sizes[p] < MpGlobal.SplitterWidthMin):
        sizes[p] = MpGlobal.SplitterWidthMin
        sizes[l] = totalsize - MpGlobal.SplitterWidthMin
        #MpGlobal.Window.splitter.setSizes(sizes)
    if (sizes[p] > MpGlobal.SplitterWidthMax):
        sizes[p] = MpGlobal.SplitterWidthMax
        sizes[l] = totalsize - MpGlobal.SplitterWidthMax
        #MpGlobal.Window.splitter.setSizes(sizes)
    
    MpGlobal.Window.playListWidth = MpGlobal.Window.splitter.sizes()[p]
    
def splitter_resize_debug(pos=None,index=None):
    sizes = MpGlobal.Window.splitter.sizes()
    totalsize = sum(sizes)
    size = 170
    totalsize -= size
    MpGlobal.Window.spt_left.setSizes([totalsize,size])



def open_dialog_Help():
    helpDialog().show();
        
def open_dialog_About():
    a = dialogAbout();
    a.exec_();
 
def button_PlayPause_setPlayIcon(value):
    """
        Updateing the display of the button is usually done from the second
        thread, therefore a signal needs to be emmitted to update the display
        signal to call this function:
        SET_PLAYBUTTON_ICON,MpMusic.PLAYING
    """
    
    obj = MpGlobal.Window.btn_playstate
    obj.state_btn1 = not (value == MpMusic.PLAYING)
    obj.update()
    
def button_PlayPause_setContIcon(value):
    """
        Updateing the display of the button is usually done from the second
        thread, therefore a signal needs to be emmitted to update the display
        signal to call this function:
        SET_CONTBUTTON_ICON,true/false
    """
    obj = MpGlobal.Window.btn_playstate
    obj.state_btn2 = value
    obj.update()
  
def button_music_prev(bool=0):
    MpGlobal.Player.prev()

def button_music_next(bool=0):
    MpGlobal.Player.fadeNext()
  
def button_library_SelectAll(bool=0):
    for song in MpGlobal.Player.libDisplay:
        if not song[MpMusic.SELECTED]:
            MpGlobal.Player.selCount += 1
            song[MpMusic.SELECTED] = True;
    MpGlobal.Window.tab_library.table.updateTable()
    UpdateStatusWidget(0,MpGlobal.Player.selCount)

def tabbar_tab_changed(index=0):
    pass
    #if index == 1:
 
    #    UpdateStatusWidget(3,"Playlist Length: %d. Maximum Songs per Artist: %d."%(MpGlobal.PLAYLIST_SIZE,s))
       
    
def toggle_DebugText_Show():
    if MpGlobal.Window.txt_debug.isHidden():
        MpGlobal.Window.txt_debug.show()
        MpGlobal.Window.act_view_debug.setIcon(MpGlobal.icon_Check)
    else:
        MpGlobal.Window.txt_debug.hide()
        MpGlobal.Window.act_view_debug.setIcon(MpGlobal.icon_Clear)
 
def toggle_Statusbar_Show():
    global _STATUS_BAR_VISIBLE
    if MpGlobal.Window.statusbar.isHidden():
        MpGlobal.Window.statusbar.show()
        _STATUS_BAR_VISIBLE = True
        MpGlobal.Window.act_view_statusbar.setIcon(MpGlobal.icon_Check)
        
    else:
        _STATUS_BAR_VISIBLE = False
        MpGlobal.Window.statusbar.hide()
        MpGlobal.Window.act_view_statusbar.setIcon(MpGlobal.icon_Clear)
 
def toggle_Console_Show():
    if MpGlobal.Window.txt_main.isHidden():
        MpGlobal.Window.txt_main.show()
        MpGlobal.Window.act_view_console.setIcon(MpGlobal.icon_Check)
    else:
        MpGlobal.Window.txt_main.hide()
        MpGlobal.Window.act_view_console.setIcon(MpGlobal.icon_Clear)


def show_NewPlayList_Dialog():
    
    diag = NewPlayListDialog(MpGlobal.last_gui_newplaylist_string);
    #QDialog.Rejected = 0 
    #QDialog.Accepted  = 1
    if QDialog.Accepted == diag.exec_():
        string = diag.getFormatedString();
        debug(string)
        processTextInput(string)# run a new playlist command
        MpGlobal.Application.processEvents();
        for song in MpGlobal.Player.library:
            song[MpMusic.SELECTED] = False
        MpGlobal.Player.selCount = 0;
        UpdateStatusWidget(0,MpGlobal.Player.selCount) 
        
        MpGlobal.last_gui_newplaylist_string = string
        # kick off new user text input 
    else:
        MpGlobal.last_gui_newplaylist_string = ""
 
def window_hide_show_library():
    pass


def Queue_FunctionCall(function):
    """
        takes as an argument a function reference
        and calls it. this is intended for use
        threads other than the main function
        when a function is needed to update the window
        but the thread does not have access to those objects
        that need to be updated
    """
    if function != None:
        function()
   
   
# ##############################################
# 
# ##############################################
def menu_open_Settings():
    dialog = SettingsWindow(None)


    if dialog.exec_():
        # save everything
        On_Close_Save_Data()
        
from MpScripting import *
from MpSort import *
from Song_Search import *
from MpCommands import *


from SystemPathMethods import *
from MpPlayer import *
from MpEventHook import initHook,disableHook
from UnicodeTranslate import Translate
from dialogNewPlayList import *  
from dialogHelp import helpDialog     
from MpEventMethods import *        
from MpPlayerThread import MediaPlayerThread

