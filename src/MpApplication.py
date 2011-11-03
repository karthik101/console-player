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
import dialogSync
import dialogColumnSelect

from widgetPage import *
import widgetTable

from widgetLineEdit import LineEdit

import widgetLineEdit

from MpGlobalDefines import *
from MpSong import Song
from datatype_hex64 import *

from table_playlist import *
from table_library import *
from table_quickselect import *
from table_playlisteditor import *
from table_fileexplorer import *
from table_external import *        #TODO i don't think this is used at all anymore

from widget_playbutton import *
from widget_currentSongDisplay import *
from widget_currentTimeDisplay import *

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
    tbl_library=None;
    tbl_explorer=None;
    tbl_quicklist = None;
    btn_playstate = None;
    
    tab_Explorer = 2 
    
    window = None;
    ui = None;      # the bare bones user interface
    geometry = None
    playListWidth = 250
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

        #self.ui = form_main.Ui_MainWindow()   # create a new user interface
        #self.setupUi(self)       # build the ui
        self.setFocusPolicy(Qt.StrongFocus)
        self.init_Ui()
        
        self.setWindowIcon(QIcon(MpGlobal.FILEPATH_ICON))

        self.move  ( Settings.SCREEN_POSITION_X ,Settings.SCREEN_POSITION_Y )
        
        if Settings.WINDOW_MAXIMIZED :
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.resize( Settings.SCREEN_POSITION_W ,Settings.SCREEN_POSITION_H )
        
        
        self.setMinimumSize(230,110)  
        self.init_DisplaySong()   
        self.init_DisplayTables()
        
        self.init_StatusBar()
        self.init_Gui()
        newFileExplorerTab(self)
        
        #self.dialogSongEdit = dialogSongEdit.SongEditWindow(self)
        self.syncDialogObj = None #dialogSync.SyncSongs(self)
        
        self.init_ConnectSignals() # do this last, after creating all objects
        
        init_MenuBar(self)
        #<WORK> REMOVE MIN WIDTH
        #self.setMinimumWidth(MpGlobal.SplitterWidthMin+20)
        
        #tsize = sum ( self.splitter.sizes() )
        #print tsize
        #self.splitter.setSizes([300,300])
        # set up keyboard shortcuts
        #
        
        self.txt_main.setFocus()
        self.setWindowTitle(title)
        
        if Settings.DEVMODE == False:
            self.txt_debug.hide()
        
        D = self.get_defaultColorDict()

        if Settings.THEME != "none":
            D = load_css(Settings.THEME,MpGlobal.Application,D,Settings.USE_CUSTOM_THEME_COLORS)
        
        self.set_colorFromCssDict(D)
            
    def init_Ui(self):

        self.splitter = QSplitter(Qt.Horizontal,self)

        self.vbox_library = VPage(self)
        self.vbox_playlist = VPage(self)
        self.vbox_playlist.layout.setSpacing(0)
        
        self.spt_left = QSplitter(Qt.Vertical,self.vbox_library )
        
        self.splitter.addWidget(self.spt_left)
        self.splitter.insertWidget(1,self.vbox_playlist) # for insertion to left or right use 0=left, 1=right

        self.tabMain = QTabWidget(self)
        self.tab_library = VPage(self.tabMain)

        # use my custom line edit widget
        self.search_hbox = QHBoxLayout()
   
        self.txt_searchBox = LineEdit(self.tabMain)
        self.txt_debug = QPlainTextEdit("...",self)
        
        #self.search_selbtn = QPushButton("Select All",self)
        self.search_label = QLabel("Found",self)
        #self.search_label.setFixedWidth(80)
        
        self.tab_library.addLayout(self.search_hbox)
        self.search_hbox.addWidget(self.txt_searchBox)
        #self.search_hbox.addWidget(self.search_selbtn)
        self.search_hbox.addWidget(self.search_label)

        self.tabMain.addTab(self.tab_library,MpGlobal.icon_note, "Library")        

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
        
    def init_DisplayTables(self):
        
        self.tbl_playlist = TablePlayList(self)
        self.tbl_library = TableLibrary(Settings.LIB_COL_ID, Settings.LIB_COL_ACTIVE, parent=self)
 
        self.vbox_playlist.insertLayout(5,self.tbl_playlist.container)
        self.tab_library.addLayout(self.tbl_library.container)
        
        self.pixmap_dndMusic = MpGlobal.pixmap_Song
        self.tbl_playlist.pixmap_drag = self.pixmap_dndMusic
        self.tbl_library.pixmap_drag  = self.pixmap_dndMusic
        
        self.txt_searchBox.keyReleaseEvent = txtSearch_KeyBoardRelease

        self.txt_searchBox.setPlaceholderText(MpGlobal.SEARCH_PROMPT)

    def init_DisplaySong(self):
        self.hbox_timeBar = QHBoxLayout()
        
        self.txt_main = widgetLineEdit.LineEditHistory(self)
        self.txt_main.keyReleaseEnter = processTextInput
        self.txt_main.setPlaceholderText("Command Input <Ctrl+K>")
        self.txt_main.setObjectName("Console")
        # this forces a minimum size for the right side of the splitter
        self.txt_main.setMinimumHeight(20)
        # #########################################
        # time display bar
        #self.bar_time = ScrollBar_Time()
        
        self.bar_time = MpTimeBar(self)
        #self.bar_time = QSlider(self)
        self.bar_time.setObjectName("MpMediaTime")
        self.bar_time.setPageStep(0)# slider is of length 'page step'
        
        # prev/next buttons
        self.btn_prev = QPushButton(self)#ButtonArrow(True) # mirror vertically
        self.btn_next = QPushButton(self)#ButtonArrow()

        self.btn_prev.setObjectName("MpMediaPrev")
        self.btn_next.setObjectName("MpMediaNext")
        
        self.btn_prev.setToolTip("Previous Song")
        self.btn_next.setToolTip("Next Song")
        
        self.hbox_timeBar.addWidget(self.btn_prev)
        self.hbox_timeBar.addWidget(self.bar_time)
        self.hbox_timeBar.addWidget(self.btn_next)
        self.hbox_timeBar.setSpacing(0)
        
        # #########################################
        # Play Button, Display Labels
        self.hbox_playbutton = QHBoxLayout()

        self.btn_playstate = ButtonPlay()
        self.dsp_info = CurrentSongDisplay()
        self.dsp_info.text_title = "Select a Song to Play"
        self.dsp_info.text_album = "Drag and Drop music to Load"
        self.dsp_info.stopScrolling()
        self.dsp_info.update()
        
        self.btn_playstate.setToolTip("Play/Pause Current Song\nStop playback when current song finishes")
        # add button and vbox to the hbox
        self.hbox_playbutton.addWidget(self.btn_playstate)
        self.hbox_playbutton.addWidget(self.dsp_info)
        self.hbox_playbutton.setSpacing(0)
        #self.hbox_playbutton.addWidget(self.dsp_rate)
        # add the time bar and display to the vbox
        self.vbox_playlist.addWidget(self.txt_main)
        self.vbox_playlist.addLayout(self.hbox_timeBar)
        self.vbox_playlist.layout.addSpacing(4)
        self.vbox_playlist.addLayout(self.hbox_playbutton)
        self.vbox_playlist.layout.addSpacing(4)
        self.vbox_playlist.layout.addSpacing(4)
        # set sizing for newly created widgets
        self.btn_prev.setFixedWidth(32)
        self.btn_next.setFixedWidth(32)
        self.btn_prev.setFixedHeight(16)
        self.btn_next.setFixedHeight(16)
    
        self.btn_playstate.setFixedHeight(48)
        self.btn_playstate.setFixedWidth(48)
        #self.dsp_rate.setFixedHeight(48)
        #self.dsp_rate.setFixedWidth(8)
        
        self.hbox_btn = QHBoxLayout()
        self.btn_clr = QPushButton(MpGlobal.icon_Trash,"",self)
        self.btn_sfl = QPushButton("Shuffle",self)
        self.btn_spn = QSpinBox(self)
        self.btn_apl = QPushButton(MpGlobal.icon_AutoPL,"",parent=self)
        
        self.btn_spn.setRange(0,9)
        self.btn_spn.setFixedWidth(32)
        self.hbox_btn.setSpacing(0)
        self.btn_clr.setToolTip("Clear current Playlist")
        s="Shuffle the remaining songs to be played\nIf songs in the playlist are selected, they will be shuffled in place"
        self.btn_sfl.setToolTip(s)
        s="Auto make a new playlist when\nthe current one finishes.\nNew Playlist will be made from a pool\nof songs from the indicated preset"
        self.btn_spn.setToolTip(s)
        self.btn_apl.setToolTip(s)
        # we need equal spacing on either side of the shuffle button
        # add spacers to make up for the width of widgets on the other side
        # don't argue with the AlignRight on the shuffle button, it just works to center
        self.hbox_btn.addWidget(self.btn_clr)
        if not isPosix: # adding a volume bar here instead
            self.hbox_btn.addSpacing(32) # equal to width of spinbox
        self.hbox_btn.addWidget(self.btn_sfl,0,Qt.AlignRight)
        self.hbox_btn.addWidget(self.btn_spn,0,Qt.AlignRight)
        self.hbox_btn.addWidget(self.btn_apl)

        self.vbox_playlist.addLayout(self.hbox_btn)
        
        self.btn_clr.setFixedWidth(24)
        #self.btn_sfl.setFixedWidth(50)
        self.btn_apl.setFixedWidth(24)
        
        self.btn_clr.clicked.connect(button_PlayList_Clear)
        self.btn_sfl.clicked.connect(button_PlayList_Shuffle)
        self.btn_apl.clicked.connect(button_PlayList_AutoPlayList)

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
        
        #self.txt_main.returnPressed.connect(txtMain_OnTextEnter)
        #self.txt_main.textEdited.connect(txtMain_OnTextChange)
        self.txt_searchBox.textEdited.connect(txtSearch_OnTextChange)
        #self.search_selbtn.clicked.connect(button_library_SelectAll)
        
        self.btn_prev.clicked.connect(button_music_prev)
        self.btn_next.clicked.connect(button_music_next)
        
        self.tabMain.currentChanged.connect(tabbar_tab_changed)
        #self.txt_searchBox.returnPressed.connect(txtSearch_OnTextEnter)

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
        
        # depreciated:
        QObject.connect(self, SIGNAL("ON_SONG_LOAD_FILLTABlE"),self.tbl_playlist.FillTable, Qt.QueuedConnection)
        # use this :
        QObject.connect(self, SIGNAL("FILL_PLAYLIST"),self.tbl_playlist.FillTable, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("FILL_LIBRARY"),self.tbl_library.FillTable, Qt.QueuedConnection)
        
        QObject.connect(self, SIGNAL("LOAD_FINISHED"),external_Load_Finish, Qt.QueuedConnection)
        
        
    
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
        hthresh2 = 150;
        if w < wthresh:
            self.spt_left.hide()
            MpGlobal.Window.statusWidgets[2].hide();
            MpGlobal.Window.statusWidgets[3].hide();
        
        else:   
            MpGlobal.Window.statusWidgets[2].show();
            MpGlobal.Window.statusWidgets[3].show();
            self.spt_left.show()
            tsize = sum ( MpGlobal.Window.splitter.sizes() )
            MpGlobal.Window.splitter.setSizes([tsize - self.playListWidth,self.playListWidth])
        
        
        if h < hthresh2:
            self.tbl_playlist.table.hide()
            self.tbl_playlist.scrollbar.hide()
            self.btn_clr.hide()
            self.btn_sfl.hide()
            self.btn_apl.hide()
            self.btn_spn.hide()
            self.spt_left.hide()
            self.statusbar.hide()
            self.menubar.hide()
        elif h < hthresh1:
            self.tbl_playlist.table.hide()
            self.tbl_playlist.scrollbar.hide()
            #self.btn_clr.hide()
            #self.btn_sfl.hide()
            #elf.btn_apl.hide()
            #elf.btn_spn.hide()
            #elf.spt_left.hide()
            self.statusbar.hide()
            self.menubar.hide()
        else:    
            self.tbl_playlist.table.show()
            self.tbl_playlist.scrollbar.show()
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
            
        if MpGlobal.LoadThread != None:
            MpGlobal.LoadThread.exit(0)
        
        disableHook()
        
        print "Closing Application"    
        # frequently have crashes on close 
        # use the print to determine before or after
        
        event.accept()
    def changeEvent(self,event):
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
        if event.source() == None: # event comes from outside the application
            mdata = event.mimeData()
            #print list(mdata.formats())
            if mdata.hasUrls() :
                event.accept() # accept before processinf or explorer will hang
                url_list = mdata.urls()
                D = []
                for x in range(len(url_list)):
                    if not url_list[x].isRelative() :
                        fpath = url_list[x].toString().replace("file:///","") 
                        fext = fileGetExt(fpath)
                        if pathMatchExt(fpath) and pathIsUnicodeFree(fpath):
                            MpGlobal.Player.external.append(fpath)
                        if os.path.isdir(fpath):
                            D.append(fpath);
                        if fext == 'log':
                            history_load(fpath,MpGlobal.Player.library)
            
                if len(D) > 0:
                    for dir in D:
                        load_music_from_dir(unicode(dir))
            
                external_Load_Start()
                Player_set_unsaved();
                
    def init_Gui(self): 
        pagem  = VPage(self)
        hbox = QHBoxLayout()
        table  = TableQuickSelect(pagem)
        self.tbl_gui = table
        cbox1 = QComboBox(pagem)
        cbox2 = QComboBox(pagem)
        cbox3 = QCheckBox("reverse",pagem)
        sbox1 = QSpinBox(pagem)
        pbtn1 = QPushButton("Clear Selection",pagem)
        pbtn2 = QPushButton("Create",pagem)
        
        hbox.addWidget(cbox1)
        hbox.addWidget(cbox2)
        hbox.addWidget(cbox3)
        hbox.addWidget(sbox1)
        hbox.addWidget(pbtn1)
        hbox.addWidget(pbtn2)
        
        pagem.addLayout(hbox)
        pagem.addWidget(QLabel("Create a new playlist by selecting artists then clicking 'Create'.",self))
        pagem.addLayout(table.container)
    
        self.tabMain.insertTab(1,pagem,MpGlobal.icon_favpage,"Quick Selection")
        self.tbl_quicklist = table
        
        cbox1.addItem("Display: Song Count")
        cbox1.addItem("Display: Play Count")
        cbox1.addItem("Display: Play Time")
        cbox1.addItem("Display: Listen Time")
        cbox1.addItem("Display: Frequency")
        cbox1.addItem("Display: Rating Count")
        cbox1.addItem("Display: Count of Rated songs")
        
        cbox2.addItem("Sort by: Artist")
        cbox2.addItem("Sort by: Song Count")
        cbox2.addItem("Sort by: Play Count")
        cbox2.addItem("Sort by: Play Time")
        cbox2.addItem("Sort by: Listen Time")
        cbox2.addItem("Sort By: Frequency")
        cbox2.addItem("Sort By: Rating Count")
        cbox2.addItem("Sort By: Count of Rated songs")
        
        sbox1.setRange(0,5)
        sbox1.setFixedWidth(32)
        sbox1.setToolTip("Set Minimum Rating")
        
        table.cbox1 = cbox1
        table.cbox2 = cbox2
        table.cbox3 = cbox3
        table.sbox1 = sbox1
        
        cbox1.currentIndexChanged[int].connect(table.__CBOX_CHANGE_DISPLAY__)
        cbox2.currentIndexChanged[int].connect(table.__CBOX_SORT_DISPLAY__)
        cbox3.stateChanged[int].connect(table.__CHECK_STATE_CHANGE__)
        sbox1.valueChanged[int].connect(table.__SBOX_Value_Changed__)
        pbtn1.clicked.connect(table.clearSelection)
        pbtn2.clicked.connect(table.newPushed)
        #c_rte=0 # combined rating
        #c_rct=0 # count of songs rated
    def setTheme(self,name='default'):
        D = load_css(name,MpGlobal.Application)
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
        self.tbl_playlist.brush_default = QBrush(self.style_dict["text_color"],0)
        self.tbl_playlist.brush_selected = QBrush(self.style_dict["color_highlight"])
        self.tbl_playlist.brush_selectedOOF = QBrush(self.style_dict["color_highlightOOF"])
        self.tbl_playlist.brush_selectedText = QBrush(self.style_dict["text_light"])
        self.tbl_playlist.brush_highlight1 = QBrush(self.style_dict["color_special1"])
        self.tbl_playlist.brush_highlight2 = QBrush(self.style_dict["color_invalid"])
        
        self.tbl_library.brush_default = QBrush(self.style_dict["text_color"],0)
        self.tbl_library.brush_selected = QBrush(self.style_dict["color_highlight"])
        self.tbl_library.brush_selectedOOF = QBrush(self.style_dict["color_highlightOOF"])
        self.tbl_library.brush_selectedText = QBrush(self.style_dict["text_light"])
        self.tbl_library.brush_highlight1 = QBrush(self.style_dict["color_special1"])
        self.tbl_library.brush_text_default = QBrush(self.style_dict["text_color"])
        self.tbl_library.brush_text_ready = QBrush(self.style_dict["text_important2"])
        self.tbl_library.brush_text_recent = QBrush(self.style_dict["text_important1"])
        self.tbl_library.brush_special = QBrush(self.style_dict["color_special2"])
        
        self.tbl_gui.brush_selected = QBrush(self.style_dict["color_special2"])
        self.tbl_gui.brush_selectedOOF = QBrush(self.style_dict["color_special2"])
        self.tbl_gui.brush_text_default = QBrush(self.style_dict["text_color"])
        self.tbl_gui.brush_text_favorite = QBrush(self.style_dict["text_important2"])
        
        self.dsp_info.brush_barfill = QBrush(self.style_dict["text_important1"])
    
        self.tbl_explorer.brush_default = QBrush(self.style_dict["text_color"],0)
        self.tbl_explorer.brush_selected = QBrush(self.style_dict["color_highlight"])
        self.tbl_explorer.brush_selectedOOF = QBrush(self.style_dict["color_highlightOOF"])
        self.tbl_explorer.brush_highlight1 = QBrush(self.style_dict["color_special1"]) #already exist
        self.tbl_explorer.brush_highlight2 = QBrush(self.style_dict["color_invalid"])  #invalid
        self.tbl_explorer.brush_highlight3 = QBrush(self.style_dict["color_special2"]) #loading

    def setPlayListWidth(self,w) :

        tsize = sum ( MpGlobal.Window.splitter.sizes() )
        r = tsize - w
        MpGlobal.Window.splitter.setSizes([r,w])
         
    def __Action_New_PlayList__(self):
        """ Create a new playlist editor and
            immediatley prompt the user to open one
        """
        obj = newPlayListEditor(self)
            
    def __Action_Load_PlayList__(self):
        """ Create a new playlist editor and
            immediatley prompt the user to open one
        """
        obj = newPlayListEditor(self)
        if obj.__btn_load__() == False:
            obj.__btn_close__()

    def __Action_shortcut_library__(self):
        obj = MpGlobal.Window.txt_searchBox
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
        self.tbl_library.selection = set(range(len(self.tbl_library.data)));
        self.tbl_library.UpdateTable(-1);            
    def Action_sort_REVERSE(self):
        MpGlobal.Player.library.reverse()
        MpGlobal.Player.lastSortType *= -1;
        MpGlobal.Window.tbl_library.updateDisplay()
        
        r = MpGlobal.Player.lastSortType>0
        ico = MpGlobal.icon_Clear
        index = r if r>=0 else -r
        if index in (MpMusic.ARTIST, MpMusic.TITLE,MpMusic.ALBUM):
            ico = MpGlobal.icon_Check if r else MpGlobal.icon_Clear
        else:
            ico = MpGlobal.icon_Clear if r else MpGlobal.icon_Check
        MpGlobal.Window.act_sfl_reverse.setIcon( ico )
    
    def Action_sort_DATESTAMP(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.DATESTAMP))
    def Action_sort_PLAYCOUNT(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.PLAYCOUNT))
    def Action_sort_FREQUENCY(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.FREQUENCY))
    def Action_sort_PATH(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.PATH))
    def Action_sort_RATING(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.RATING))
    def Action_sort_ARTIST(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.ARTIST))
    def Action_sort_TITLE(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.TITLE))
    def Action_sort_ALBUM(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.ALBUM))

    def Action_sort_LENGTH(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.LENGTH))
    def Action_sort_GENRE(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.GENRE))
    def Action_sort_FSIZE(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.FILESIZE))
    def Action_sort_SKIPCOUNT(self):
        self.tbl_library.columnClicked(self.tbl_library.col_id.index(MpMusic.SKIPCOUNT))

                 
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
    
    #QMetaType.Q_DECLARE_METATYPE(widgetTable.Table)
    #print QMetaType.type("Table")
    registerSSService()
     
    getApplicationIcons()
    
    MpGlobal.Player.library = musicLoad_LIBZ(MpGlobal.FILEPATH_LIBRARY)
    MpGlobal.Player.playList = playListLoad(MpGlobal.FILEPATH_PLAYLIST_CURRENT,MpGlobal.Player.library)

def init_postMainWindow():
    """
        Called immediatley after window.show()
    """
    
    sortLibraryInplace(MpMusic.ARTIST)
    buildArtistList()
    
    MpGlobal.Player.libDisplay = MpGlobal.Player.library[:]
    
    MpGlobal.Window.tbl_library.UpdateTable(0,MpGlobal.Player.libDisplay) 
    MpGlobal.Window.tbl_playlist.UpdateTable(0,MpGlobal.Player.playList) 
    
    MpGlobal.Window.setPlayListWidth(300)
    if not MpGlobal.Window.txt_debug.isHidden():
        splitter_resize_debug()
    
    MpGlobal.Window.search_label.setText("Found: %d"%len(MpGlobal.Player.libDisplay))
    
    if Settings.PLAYER_LAST_INDEX < len(MpGlobal.Player.playList):
        MpGlobal.Player.CurrentIndex = Settings.PLAYER_LAST_INDEX
        
    MpGlobal.Player.loadSong()
    
    UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
    
    MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Ready, DevMode : %s"%Settings.DEVMODE)   

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
    
def newPlayListEditor(MainWindow,name = "PlayList Editor"):
        # #######################################################
        # create the objects
        pagem  = VPage()
        #pagel = VPage(pagem)
        #pager = VPage(pagem)
        
        id = 0;
        for item in MpGlobal.Window.editorTabs:
            id = max(id,item[5])
        id += 1
        
        if name == "PlayList Editor":
            name += " (%d)"%id
            
        #index = MainWindow.tabMain.addTab(pagem,MpGlobal.icon_file,name)
        index = MainWindow.tabMain.addTab(pagem,name)
        
        
        #vbox = QVBoxLayout(page)
        #vboxl = QVBoxLayout(pagel)
        #vboxr = QVBoxLayout(pager)
        
        hbox = QHBoxLayout()
        edit = LineEdit(pagem)
        btn1 = QPushButton(MpGlobal.icon_open,"",pagem)
        btn2 = QPushButton(MpGlobal.icon_save,"",pagem)
        #btn3 = QPushButton(MpGlobal.icon_AutoPLO,"",pagem) 
        btn4 = QPushButton("Play",pagem) 
        btnX = CloseTabButton(MainWindow);
        
        
        #hbox.addWidget(btn3) # close
        hbox.addWidget(btn1) # open
        hbox.addWidget(btn2) # save
        hbox.addWidget(edit)
        hbox.addWidget(btn4) # play   
        MainWindow.tabMain.tabBar().setTabButton (index,QTabBar.LeftSide,btnX)
        
        
        splitter = QSplitter(pagem)
        
        #lname = "Left_%d"%len(MainWindow.editorTabs)
        #rname = "Right_%d"%len(MainWindow.editorTabs)
        lname = "Left"
        rname = "Right"
        
        tbl_left = TablePLEditor(pagem,lname,rname)
        tbl_rite = TablePLEditor(pagem,rname,lname)
        
        # #######################################################
        # add widgets to the containers
        pagem.addLayout(hbox)
        pagem.addWidget(splitter)

        #pagel.addWi()
        #pager.addLayout()
        
        splitter.addWidget(tbl_left.container)
        splitter.addWidget(tbl_rite.container)
        # #######################################################
        # Connect Signals and init the new Tab
        # each tab has a copy of the library to work with
        # data can be moved from the left or right table
        tbl_left.UpdateTable(0,)
        
        tbl_left.setTables(tbl_rite)
        tbl_rite.setTables(tbl_left)
        
        # create the two data pools, 
        # these will be searched then sorted and displayed
        
        leftData = sortLibrary(MpMusic.ARTIST)
        riteData = []
        
        tbl_left.setDataSrc(leftData)
        tbl_rite.setDataSrc(riteData)
        
        tbl_left.setOtherDataSrc(riteData)
        tbl_rite.setOtherDataSrc(leftData)
        
        tbl_left.setTextEdit(edit)
        tbl_rite.setTextEdit(edit)
        
        edit.textEdited.connect(tbl_left.__text_edit__)
        btn1.clicked.connect(tbl_left.__btn_load__)
        btn2.clicked.connect(tbl_left.__btn_save__)
        #btn3.clicked.connect(tbl_left.__btn_close__)
        btn4.clicked.connect(tbl_left.__btn_play__)
        
        tbl_left.runSearchUpdate("")    # update and show all
        tbl_rite.runSearchUpdate("")
        #tbl_left.UpdateTable(0,tbl_left.DataSrc)
        #tbl_rite.oTable.UpdateTable(0,tbl_rite.oDataSrc)

        tbl_rite.isRight = True # the right table is the playlist
        
        btn1.setFixedWidth(32)
        btn2.setFixedWidth(32)
        #btn4.setFixedWidth(48)

        # #######################################################
        # save a record of the new Tab
        
        object = [name,edit,tbl_left,tbl_rite,index,id,pagem,splitter]
        tbl_left.setObjectList(object)
        tbl_rite.setObjectList(object)
        
        MpGlobal.Window.tabMain.setCurrentIndex(index)
        MpGlobal.Window.tabMain.tabBar().setTabData(index,tbl_left)
        
        #TODO set btnX callBack
        btnX.setCallback(tbl_left.__btn_close__)
        
        MainWindow.editorTabs.append( object )
        
        return tbl_left

def newFileExplorerTab(self,path="C:\\"):
        # #######################################################
        # create the objects
        pagem = VPage(self)
        
        
        hbox = QHBoxLayout()
        cbox = QComboBox(pagem)
        cbox.setEditable(True)
        pbtn = QPushButton(pagem)
        pbtn_go = QPushButton("Open",pagem)
        
        self.tbl_explorer = TableFileExplorer(pagem,cbox)

        index = self.tabMain.addTab(pagem,MpGlobal.icon_Folder,"Explorer")    
        self.tabMain.setIconSize(QSize(16,16))
        hbox.addWidget(pbtn)
        hbox.addWidget(cbox)
        hbox.addWidget(pbtn_go)
        
        pagem.addLayout(hbox)
        pagem.addLayout(self.tbl_explorer.container)
        
        pbtn.setFixedWidth(20)
        pbtn_go.setFixedWidth(48)
        
        pbtn.setObjectName("MpExplorer_Back")
        
        pbtn.clicked.connect(self.tbl_explorer.__Goto_ParentDir__)
        pbtn_go.clicked.connect(self.tbl_explorer.__Goto_NewDir__)
  
def txtSearch_OnTextChange(text):
    
    
    text = MpGlobal.Window.txt_searchBox.textUpdate(text)
    text += MpGlobal.SEARCH_AUTOAPPEND
    MpGlobal.Window.tbl_library.selection = set() 
    
    if text == "" :
        MpGlobal.Player.libDisplay = MpGlobal.Player.library[:]
        MpGlobal.Window.tbl_library.UpdateTable(0,MpGlobal.Player.libDisplay)
        MpGlobal.Window.statusWidgets[2].setToolTip(u"No Search Terms")
        UpdateStatusWidget(2,0)
    else:
        #time = datetime.datetime.now()
        #try:
        so = SearchObject(text)
        MpGlobal.Window.statusWidgets[2].setToolTip(unicode(so))
        MpGlobal.Player.libDisplay = so.search(MpGlobal.Player.library)
        MpGlobal.Window.tbl_library.UpdateTable(0,MpGlobal.Player.libDisplay)
        UpdateStatusWidget(2,so.termCount)
        #except Exception as e:
        #    debug("EVAL ERROR: %s"%e.args)
            
        #end = datetime.datetime.now()
        #debug( "Search Time: %s"%(end-time) )
        
    #MpGlobal.Window.tabMain.setTabText(0,"Library (%d)"%len(MpGlobal.Player.libDisplay))
    MpGlobal.Window.search_label.setText("Found: %d"%len(MpGlobal.Player.libDisplay))
    
def txtSearch_KeyBoardRelease(event=None):
    super(QLineEdit,MpGlobal.Window.txt_searchBox).keyPressEvent(event)
    #print ">"
    if event.key() == Qt.Key_Down:
        MpGlobal.Window.tbl_library.selection = set()
        MpGlobal.Window.tbl_library.selection.add(0)
        MpGlobal.Window.tbl_library.FillTable(0)
        MpGlobal.Window.tbl_library.table.setFocus()

def splitter_resize_control(pos,index):
    sizes = MpGlobal.Window.splitter.sizes()
    totalsize = sum(sizes)
    # check the size of the layouts in the main splitter
    # if they are above or below the set maximum then set them equal to that value
    if (sizes[1] < MpGlobal.SplitterWidthMin):
        sizes[1] = MpGlobal.SplitterWidthMin
        sizes[0] = totalsize - MpGlobal.SplitterWidthMin
        #MpGlobal.Window.splitter.setSizes(sizes)
    if (sizes[1] > MpGlobal.SplitterWidthMax):
        sizes[1] = MpGlobal.SplitterWidthMax
        sizes[0] = totalsize - MpGlobal.SplitterWidthMax
        #MpGlobal.Window.splitter.setSizes(sizes)
    
    MpGlobal.Window.playListWidth = MpGlobal.Window.splitter.sizes()[1]
    
def splitter_resize_debug(pos=None,index=None):
    sizes = MpGlobal.Window.splitter.sizes()
    totalsize = sum(sizes)
    size = 170
    totalsize -= size
    MpGlobal.Window.spt_left.setSizes([totalsize,size])

def button_PlayList_Clear():
    MpGlobal.Player.playList = []
    MpGlobal.Window.tbl_playlist.UpdateTable(0,MpGlobal.Player.playList)
def button_PlayList_Shuffle():
    sindex = list(MpGlobal.Window.tbl_playlist.selection) # list of song indexes
    if len(sindex) > 1:
        # if multiple songs are selected in the playlist
        # select these songs into a new array, shuffle
        # and place back at the original indexes
        S = MpGlobal.Window.tbl_playlist.getSelection() # list of songs
        ShuffleList(S) # shuffle selection array in place
        for x in range(len(sindex)):
            MpGlobal.Player.playList[sindex[x]] = S[x]
    else:
        # shuffle the entire playlist starting with the first
        # song after the current song playing
        s = MpGlobal.Player.CurrentIndex + 1
        e = len(MpGlobal.Player.playList)
        ShufflePartition(MpGlobal.Player.playList,s,e)
    MpGlobal.Window.tbl_playlist.FillTable()
    
def button_PlayList_AutoPlayList():
    """ change the playlist ending policy
        order of the array determines how the values are updated
    """
    S = (MpGlobal.PLAYLIST_END_CREATE_NEW,\
         MpGlobal.PLAYLIST_END_STOP,\
         MpGlobal.PLAYLIST_END_LOOP_SAME,\
         MpGlobal.PLAYLIST_END_LOOP_ONE)
    R = ( setPlayBack_Mode1, \
          setPlayBack_Mode4, \
          setPlayBack_Mode2, \
          setPlayBack_Mode3 )    
    index = (S.index(MpGlobal.PLAYLIST_END_POLICY)+1)%len(S)      
    R[index]();
    #MpGlobal.PLAYLIST_END_POLICY = R[]
    #button_PlayList_AutoPlayList_SetIcon()
    return
def button_PlayList_AutoPlayList_SetIcon():
    if MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_CREATE_NEW:
        MpGlobal.Window.btn_apl.setIcon(MpGlobal.icon_AutoPL)
        MpGlobal.Window.btn_spn.setDisabled(False)
    elif MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_STOP:
        MpGlobal.Window.btn_apl.setIcon(MpGlobal.icon_AutoPLO)
        MpGlobal.Window.btn_spn.setDisabled(True)
    elif MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_LOOP_SAME:
        MpGlobal.Window.btn_apl.setIcon(MpGlobal.icon_AutoPLS)
        MpGlobal.Window.btn_spn.setDisabled(True)
    else:
        MpGlobal.Window.btn_apl.setIcon(MpGlobal.icon_AutoPL1)
        MpGlobal.Window.btn_spn.setDisabled(True)    
def setPlayBack_Mode1():  
    MpGlobal.PLAYLIST_END_POLICY = MpGlobal.PLAYLIST_END_CREATE_NEW
    button_PlayList_AutoPlayList_SetIcon()
    MpGlobal.Window.act_pMode_pb1.setIcon(MpGlobal.icon_Check)
    MpGlobal.Window.act_pMode_pb2.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb3.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb4.setIcon(MpGlobal.icon_Clear)
def setPlayBack_Mode2():  
    MpGlobal.PLAYLIST_END_POLICY = MpGlobal.PLAYLIST_END_LOOP_SAME
    button_PlayList_AutoPlayList_SetIcon()
    MpGlobal.Window.act_pMode_pb1.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb2.setIcon(MpGlobal.icon_Check)
    MpGlobal.Window.act_pMode_pb3.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb4.setIcon(MpGlobal.icon_Clear)
def setPlayBack_Mode3():  
    MpGlobal.PLAYLIST_END_POLICY = MpGlobal.PLAYLIST_END_LOOP_ONE
    button_PlayList_AutoPlayList_SetIcon()
    MpGlobal.Window.act_pMode_pb1.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb2.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb3.setIcon(MpGlobal.icon_Check)
    MpGlobal.Window.act_pMode_pb4.setIcon(MpGlobal.icon_Clear)
def setPlayBack_Mode4():  
    MpGlobal.PLAYLIST_END_POLICY = MpGlobal.PLAYLIST_END_STOP
    button_PlayList_AutoPlayList_SetIcon()
    MpGlobal.Window.act_pMode_pb1.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb2.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb3.setIcon(MpGlobal.icon_Clear)
    MpGlobal.Window.act_pMode_pb4.setIcon(MpGlobal.icon_Check)
 
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
    MpGlobal.Window.tbl_library.UpdateTable()
    UpdateStatusWidget(0,MpGlobal.Player.selCount)

def tabbar_tab_changed(index=0):
    if index == 1:
        MpGlobal.Window.tbl_quicklist.UpdateTable(-1);
        s = MpGlobal.Window.tbl_quicklist.calc_hvalue();  
        UpdateStatusWidget(3,"Playlist Length: %d. Maximum Songs per Artist: %d."%(MpGlobal.PLAYLIST_SIZE,s))
       
    
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
        
def external_Load_Start():

    if MpGlobal.ENABLE_MUSIC_LOAD == False and len(MpGlobal.Player.external) > 0:
        MpGlobal.ENABLE_MUSIC_LOAD = True
        MpGlobal.LoadThread = Thread_LoadMedia(MpGlobal.Window)
        MpGlobal.LoadThread.start()

def external_Load_Finish():  
    if MpGlobal.LoadThread.isRunning():
        # once got a thread destryoed while running error
        MpGlobal.Window.emit(SIGNAL("LOAD_FINISHED"))
        debug(" *** Thread Ended while still Running.")
    else:
        MpGlobal.LoadThread = None
        MpGlobal.Window.txt_searchBox.setText(".pcnt =0")
        MpGlobal.Window.tbl_library.updateDisplay(".pcnt =0")

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
from MpSearch import *
from MpCommands import *
from MpFileAccess import *
from MpPlayer import *
from MpEventHook import disableHook
from UnicodeTranslate import Translate
from MpThreading import Thread_LoadMedia
from dialogNewPlayList import *  
from dialogHelp import helpDialog     
        
