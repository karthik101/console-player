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
import widgetPlayButton
from widgetLineEdit import LineEdit
import widgetInfoDisplay
import widgetLineEdit

from MpGlobalDefines import *




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
        self.splitter.addWidget(self.vbox_playlist)

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
        self.tbl_library = TableLibrary(self)
 
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
        table  = TableGui(pagem)
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

class TablePlayList(widgetTable.Table):
    """
        Play Lists.
        
        Playlists are genereated from the selection pool. The pool can be manipulated by using the commands 'find' and 'remove' however, it is a better idea to use presets.
        
        
        Getting Started
        
        
        \\<b\\> Presets\\</b\\>
            Customize your presets in the settings menu.
            
            In the bottom right of the playlist table, there is a little green 'A' icon. The number next to indicates the preset to use. When the current playlist finishes a new playlist will automatically be made from that preset.
    
    """
    brush_highlight1 = QBrush(QColor(150,50,100,128))
    brush_highlight2 = QBrush(QColor(255,5,5,128))
    brush_selected = QBrush(QColor(25,50,150,255))
    def __init__(self,parent=None):
        header = ["#","Data"]
        super(TablePlayList,self).__init__(parent,header)
        self.table.horizontalHeader().hide()
        self.table.setColumnWidth(0,20)
        self.table.setColumnWidth(1,MpGlobal.SplitterWidthMax)
        self.table.setDragDropMode(QAbstractItemView.DragDrop)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setDragType("dragFromPlayList")
        self.setDragReceiveType("dragFromPlayList")
        self.addDragReceiveType("dragFromLibrary")
        self.addDragReceiveType("dragTableEditor_Left")
        self.addDragReceiveType("dragTableEditor_Right")
        #self.table.resizeColumnToContents(1)
        self.table.setObjectName("table_Playlist")
    def FillTable(self,offset=-1):  
        super(TablePlayList,self).FillTable(offset)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
    def FillRow(self,index):
        i = "%s - %s"%(self.data[index][MpMusic.ARTIST],self.data[index][MpMusic.TITLE])
        R = [index+1,i]
        return R
    def FillRowColor(self,index):
    
        # b1 provides a bg-color for the numbered
        # when the given index has a special state and is selected.
        b1 = self.brush_selected;
        if index == MpGlobal.Player.CurrentIndex:
            b1 = self.brush_highlight1;
        elif index == MpGlobal.Player.stopIndex:
            b1 = self.brush_highlight2;
        
        elif not self.table.hasFocus():
            b1 = self.brush_selectedOOF;
            
        if index in self.selection:
            if self.table.hasFocus() :
                return (b1,self.brush_selected)
            else:
                return (b1,self.brush_selectedOOF)
        elif index == MpGlobal.Player.stopIndex:
            return (b1,self.brush_highlight2)
            
        elif index == MpGlobal.Player.CurrentIndex:
            if MpGlobal.Player.stopNext :
                return (b1,self.brush_highlight2)
            elif MpGlobal.Player.CurrentIndex < len(self.data) and not MpGlobal.INPUT_PLAY_GOTO_ZERO:
                return self.brush_highlight1 
                    
        return self.brush_default
            
    def DoubleClick(self,item):
        offset = MpGlobal.Window.tbl_playlist.getDisplayOffset()
        index = offset+item.row()
        if item.column() == 1:
            MpGlobal.Player.playSong(index)
        else:
            if MpGlobal.Player.stopIndex == index:
                MpGlobal.Player.stopIndex = -1
            else:
                MpGlobal.Player.stopIndex = index
                MpGlobal.Player.stopNext = False;
            MpGlobal.Window.tbl_playlist.FillTable()
    def dropEvent(self,event,row):
        dragType = event.mimeData().text()
        if event.mimeData().hasText == False :
            return;
        if dragType not in self.dragReceive :
            return; # make sure that the drag is of valid type
            
        srcSelf = (event.source() == self.table)
        
        R = [] #list of indexes of songs in an array

        data = None;
        
        # determine which data the drag is coming from
        if srcSelf :
            R = list(self.selection)
            data = MpGlobal.Player.playList
        else:
            if dragType == "dragFromLibrary":
                R = list(MpGlobal.Window.tbl_library.selection)
                data = MpGlobal.Player.libDisplay
            elif dragType == "dragTableEditor_Left":
                tab   = MpGlobal.Window.tabMain
                index = tab.currentIndex()
                text  = tab.tabText(index)
                table = None
                for item in MpGlobal.Window.editorTabs:
                    if item[0] == text:
                        table = item[2]
                if table == None:
                    debug("Table Error")
                    return;
                R = list(table.selection)
                data = table.data
            elif dragType == "dragTableEditor_Right":
                tab   = MpGlobal.Window.tabMain
                index = tab.currentIndex()
                text  = tab.tabText(index)
                table = None
                for item in MpGlobal.Window.editorTabs:
                    if item[0] == text:
                        table = item[3]
                if table == None:
                    debug("Table Error")
                    return;
                R = list(table.selection)
                data = table.data
        
        if len(R) > 0:
            R.sort() # sort the index values from low to high    
             
            cindex_flag = False # if true, magic must be done to find the current index again
            
            tempsong = MpGlobal.Player.CurrentSong
            # with a list of row indexes, convert them to a list of songs
            S = []
            index = row + self.getDisplayOffset()
            
            if index > len(MpGlobal.Player.playList):
                # if drop position is outside list range,
                # this will drop the item after the last element
                index = len(MpGlobal.Player.playList)
            
            # save the relative location of the stop index, when compared to the current song
            save_stop_index = MpGlobal.Player.stopIndex - MpGlobal.Player.CurrentIndex;
            
            for x in range(len(R)):
                if x < len(data):
                    S.append(data[R[x]])
            if len(S) == 0:
                return
            # S is now an array of songs ready to be spliced into the play list
            if srcSelf :
                # we are moving elements within the array
                # sort and remove them one at a time
                # update the insert index if needed
                R.reverse()
                for x in R:
                    MpGlobal.Player.playList.pop(x)
                    if x == MpGlobal.Player.CurrentIndex :
                        cindex_flag = True
                    if x < MpGlobal.Player.CurrentIndex :
                        MpGlobal.Player.CurrentIndex -= 1
                    if x < index:
                        index -= 1
            # splice in the drop list of songs into the playlist
            MpGlobal.Player.playList = MpGlobal.Player.playList[:index] + S + MpGlobal.Player.playList[index:]
            if index <= MpGlobal.Player.CurrentIndex :
                MpGlobal.Player.CurrentIndex += len(S)
            if cindex_flag :
                # this takes care if the same song is in the list twice
                # however if the same song is in the selection twice then user is dumb
                for x in range(index,index+1+len(S)):
                    if MpGlobal.Player.playList[x] == tempsong :
                        MpGlobal.Player.CurrentIndex = x;
                        break;
                        
            if MpGlobal.Player.stopIndex >= 0 :
                MpGlobal.Player.stopIndex = MpGlobal.Player.CurrentIndex + save_stop_index;
                # stop_index cannot be beyond the length of the playlist
                if MpGlobal.Player.stopIndex >= len(MpGlobal.Player.playList):
                    MpGlobal.Player.stopIndex = len(MpGlobal.Player.playList)-1;
                    
            self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.playList)
            # create a list of all the moved elements
            R = range(index,index+len(R))
            # use this list to form a new selection
            self.selection = set(R)
            # highlight the selected items
            UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
            self.FillTable()
            MpGlobal.Player.updateDisplayIndex()
        #else:
        #    debug("Drop Received Empty Selection")
        # if srcSelf is true, the drop operation came from self.
        # otherwise some magic needs to be done to get the selection from elseware
    def keyReleaseEvent(self,event):
    
        _ctrl = event.modifiers()&Qt.ControlModifier ==  Qt.ControlModifier
        
        if event.key() == Qt.Key_Up:
            self.__keyboard_scroll_UP__(); 
        elif event.key() == Qt.Key_Down:
            self.__keyboard_scroll_DOWN__();
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            #index = 0;
            if len(self.selection) > 0:
                R = list(self.selection)
                R.sort()
                index = R[0]
                MpGlobal.Player.playSong(index);
            
        elif event.key() == Qt.Key_Delete :
            R = list(self.selection)
            R.sort(reverse = True)
            cindex_flag = False
            for x in R:
                MpGlobal.Player.playList.pop(x)
                if x == MpGlobal.Player.CurrentIndex :
                    cindex_flag = True
                if x < MpGlobal.Player.CurrentIndex :
                    MpGlobal.Player.CurrentIndex -= 1
            self.selection = set()
            if cindex_flag :
                MpGlobal.Player.playSong(MpGlobal.Player.CurrentIndex)
            MpGlobal.Player.updateDisplayIndex()
            
            # there is a odd jump relative to the mouse if this is not done
            offset = self.getDisplayOffset()
            if offset == self.scroll_MaxRange:
                offset -= 1
                
            self.UpdateTable(offset,MpGlobal.Player.playList)
            UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
        elif _ctrl and event.key() == Qt.Key_A:
            self.selection = set(range(len(self.data)));
            self.UpdateTable(-1);       
    def minimumSize(self):
        return QtCore.QSize(200, 200)

class TableLibrary(widgetTable.Table):
    widthA = 100; #On Resize check these for percents, auto scaling of these regions
    widthT = 100; #sum these and divide out each for a scale  
    widthB = 100;
    brush_highlight1 = QBrush(QColor(255,255,0,32))
    brush_special = QBrush(QColor(255,0,0,32))
    
    brush_text_default  = QBrush(QColor(  0,  0,  0)) 
    brush_text_ready  = QBrush(QColor(180, 10,  5)) 
    brush_text_recent = QBrush(QColor(5, 10,  180)) 

    # the MpMusic Constant associated with each column
    
    col_id = [MpMusic.PLAYCOUNT, \
              MpMusic.ARTIST, \
              MpMusic.TITLE, \
              MpMusic.ALBUM, \
              MpMusic.LENGTH, \
              MpMusic.RATING, \
              MpMusic.GENRE, \
              MpMusic.FREQUENCY, \
              MpMusic.DATESTAMP, \
              MpMusic.FILESIZE, \
              MpMusic.SKIPCOUNT, \
              MpMusic.COMMENT,\
              MpMusic.SONGINDEX,\
              MpMusic.SONGID,
              MpMusic.PATH];
                                    
    col_title = {MpMusic.PLAYCOUNT: "#", \
                 MpMusic.ARTIST   : "Artist", \
                 MpMusic.TITLE    : "Title", \
                 MpMusic.ALBUM    : "Album", \
                 MpMusic.LENGTH   : "Length", \
                 MpMusic.RATING   : "Rating", \
                 MpMusic.GENRE    : "Genre", \
                 MpMusic.FREQUENCY: "Frequency", \
                 MpMusic.DATESTAMP: "Last Played", \
                 MpMusic.FILESIZE : "File Size", \
                 MpMusic.SKIPCOUNT: "Skip Count", \
                 MpMusic.COMMENT  : "Comment", \
                 MpMusic.SONGINDEX: "Album Index", \
                 MpMusic.PATH     : "File Path", \
                 MpMusic.SONGID   : "ID"};          
       
    def __init__(self,parent):
      
        header = [];
        for const in self.col_id:
            header.append(self.col_title[const])

        super(TableLibrary,self).__init__(parent,header)
        self.table.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDragType("dragFromLibrary")
        self.setDragReceiveType("None")
        
        h = self.table.horizontalHeader();
        h.setSortIndicatorShown(True)
        self.table.horizontalHeader().setSortIndicator(1,False) 
        
        self.resizeColumn()
        self.table.setObjectName("table_Library")

    def FillTable(self,offset=-1):    
        """fill the table with data, starting at index offset, from the Display Array"""
        R = []
        k=0;
        if offset < 0 :
            offset = self.scrollbar.value()
            
            
        #offset = max(0,offset)
        #TODO ERROR WITH READING VALUE, set signal to whatch for when offset is set
        #assert offset >= 0, "OFFSET READ ERROR m:%d M:%d v:%d"%(self.scrollbar.minimum(),self.scrollbar.maximum(),self.scrollbar.value())
        #if (selfta == None):
        #    return
        size = len(self.data) # in case size is zero, prevent any drawing to it
        #self.table.setModel(None);
        
        #print self.event_proc
        
        self.event_proc = True
        
        for i in range(self.rowCount):
            k = i+offset; # the k'th element of the data array
            
            if k < len(self.data) and size > 0:
                R = self.FillRow(k)
                brush = self.FillRowColor(k)
                
                # set a color for the current song
                
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),R[j])
                    self.model.setData(self.model.index(i,j),brush,Qt.BackgroundRole)
 
                date = self.data[k][MpMusic.DATEVALUE]
                
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.PLAYCOUNT)),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.LENGTH   )),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.RATING   )),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,self.col_id.index(MpMusic.FREQUENCY)),Qt.AlignRight,Qt.TextAlignmentRole)

                datecol = self.col_id.index(MpMusic.DATESTAMP)
                
                if date < MpGlobal.LaunchEpochTime:
                    self.model.setData(self.model.index(i,datecol),self.brush_text_ready,Qt.ForegroundRole)
                elif date > MpGlobal.RecentEpochTime:
                     self.model.setData(self.model.index(i,datecol),self.brush_text_recent,Qt.ForegroundRole)
                else:
                    self.model.setData(self.model.index(i,datecol),self.brush_text_default,Qt.ForegroundRole)

            else:
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),"")
                    self.model.setData(self.model.index(i,j),self.brush_default,Qt.BackgroundRole) 
                    
        self.event_proc = False
        #highlight the current song
        #qFG_text_color = self.brush_text_default;
        #if self.data[k] == MpGlobal.Player.CurrentSong:
        #    qFG_text_color = self.brush_text_recent;
        #self.model.setData(self.model.index(i,j),qFG_text_color,Qt.ForegroundRole)                        
                    
        #self.table.setModel(self.model);
        # TODO REMOVE THIS
        # self.table.resizeColumnToContents(self.col_id.index(MpMusic.PATH))
        
        return;
        
    def FillRow(self,index):
        R = [""]*len(self.col_id);
        R[self.col_id.index(MpMusic.PLAYCOUNT)] = self.data[index][MpMusic.PLAYCOUNT]
        R[self.col_id.index(MpMusic.ARTIST)]    = self.data[index][MpMusic.ARTIST]
        R[self.col_id.index(MpMusic.TITLE)]     = self.data[index][MpMusic.TITLE]
        R[self.col_id.index(MpMusic.ALBUM)]     = self.data[index][MpMusic.ALBUM]
        R[self.col_id.index(MpMusic.LENGTH)]    = convertTimeToString(self.data[index][MpMusic.LENGTH])
        R[self.col_id.index(MpMusic.RATING)]    = self.data[index][MpMusic.RATING]
        R[self.col_id.index(MpMusic.GENRE)]     = self.data[index][MpMusic.GENRE]
        R[self.col_id.index(MpMusic.FREQUENCY)] = self.data[index][MpMusic.FREQUENCY]
        R[self.col_id.index(MpMusic.DATESTAMP)] = self.data[index][MpMusic.DATESTAMP]
        R[self.col_id.index(MpMusic.FILESIZE)]  = self.data[index][MpMusic.FILESIZE]
        R[self.col_id.index(MpMusic.SKIPCOUNT)] = self.data[index][MpMusic.SKIPCOUNT]
        R[self.col_id.index(MpMusic.COMMENT)]   = self.data[index][MpMusic.COMMENT]
        R[self.col_id.index(MpMusic.PATH)]      = self.data[index][MpMusic.PATH]
        R[self.col_id.index(MpMusic.SONGID)]    = str(self.data[index].id)
        R[self.col_id.index(MpMusic.SONGINDEX)] = self.data[index][MpMusic.SONGINDEX]
        return R
        
    def FillRowColor(self,index):
        if index in self.selection:
            if self.table.hasFocus() :
                return self.brush_selected
            else:
                return self.brush_selectedOOF
        elif self.data[index][MpMusic.SPECIAL] :
            return self.brush_special
        elif self.data[index][MpMusic.SELECTED] :
            return self.brush_highlight1
        else:   
            return self.brush_default
   
    def columnClicked(self,col):
        # create a list of columns, selecting the clicked one.
        id = self.col_id[col]
        # sort the library by the clicked column 
   
        self.sortColumnByEXIF(id)
        # perform a search and update the table
        MpGlobal.Window.tbl_library.updateDisplay()
        
        
        #MpGlobal.Window.tbl_library.UpdateTable(0,MpGlobal.Player.libDisplay) 
        # allow alternating clicks to flip the sort direction
        # lastSortType is set in the sort functions
        return;
        
    def sortColumnByEXIF(self,exifTag):
    
        i = 1;
        
        if exifTag in (MpMusic.ARTIST, MpMusic.TITLE,MpMusic.ALBUM, MpMusic.GENRE, MpMusic.COMMENT, MpMusic.PATH, MpMusic.SONGID):
            dir = MpGlobal.Player.lastSortType==exifTag
            i = 0;
        else:
            dir = MpGlobal.Player.lastSortType!=exifTag
            i = 1;
        
        if exifTag in (MpMusic.DATESTAMP,MpMusic.DATEVALUE):
            i = 2;
        # string: #-A-Z-a, a-Z-A-#
        # number: increasing, decreasing
        # date  : Recent First | Recent Last
        
        t_txt  =    (u"#-A-Z-\u3042" , u"\u3042-Z-A-#"), \
                    (u"Increasing"   , u"Decreasing"  ), \
                    (u"Not Recent First" , u"Recent First" ), \
        
        dir_text = t_txt[i][1] if dir else t_txt[i][0]

        if exifTag in self.col_id:
            self.table.horizontalHeader().setSortIndicator(self.col_id.index(exifTag),dir)  
        
        sortLibraryInplace(exifTag,dir)   

        
        UpdateStatusWidget(3,"sorted by %s - %s"%(MpMusic.exifToString(exifTag),dir_text))
            
    def resizeColumn(self):
        self._resizeColumn(self.col_id.index(MpMusic.PLAYCOUNT), 35)
        self._resizeColumn(self.col_id.index(MpMusic.ARTIST)   ,150)
        self._resizeColumn(self.col_id.index(MpMusic.TITLE)    ,200)
        self._resizeColumn(self.col_id.index(MpMusic.ALBUM)    ,150)
        self._resizeColumn(self.col_id.index(MpMusic.LENGTH)   , 50)
        self._resizeColumn(self.col_id.index(MpMusic.RATING)   , 50)
        self._resizeColumn(self.col_id.index(MpMusic.GENRE)    ,100)
        self._resizeColumn(self.col_id.index(MpMusic.FREQUENCY), 75)
        self._resizeColumn(self.col_id.index(MpMusic.DATESTAMP),130)
        self._resizeColumn(self.col_id.index(MpMusic.FILESIZE) ,130)
        self._resizeColumn(self.col_id.index(MpMusic.SKIPCOUNT),100)
        self._resizeColumn(self.col_id.index(MpMusic.COMMENT)  ,130)
        self._resizeColumn(self.col_id.index(MpMusic.PATH)     ,500)
        
    def _resizeColumn(self,index,size):
        if index < self.colCount:
            self.table.setColumnWidth(index,size)
            
    def DoubleClick(self,item):
        R = self.getSelection()
        if len(R) > 0 :
            index = MpGlobal.Player.CurrentIndex + 1
            MpGlobal.Player.playList = MpGlobal.Player.playList[:index] + R + MpGlobal.Player.playList[index:]
            UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
            MpGlobal.Window.tbl_playlist.data = MpGlobal.Player.playList
            MpGlobal.Window.tbl_playlist.UpdateTable(MpGlobal.Window.tbl_playlist.getDisplayOffset(),MpGlobal.Player.playList)
        return
        
    def leftReleaseEvent(self,item,event):
        super(TableLibrary,self).leftReleaseEvent(item,event)

        _row = self.itemToIndex(item)
        if 0 <= _row < len(self.data):
            UpdateStatusWidget(3,self.data[_row][MpMusic.PATH])
            
    def rightClickEvent(self,event):
        
        item = self.table.indexAt(event.pos())
        row = item.row() + self.getDisplayOffset()
            
        if len(self.selection) > 0 and row < len(self.data):

            # modify the context menu based on click context
            contextMenu = QMenu(self.table)
            
            
            contextMenu.addSeparator()
            if len(self.selection) == 1:
                contextMenu.addAction("Add Song to Pool",self.__Action_addSelectionToPool)
                
                contextMenu.addAction("Edit Song",self.__Action_editSong__)
                contextMenu.addAction("DELETE Song",self.__Action_deleteSingle)
            
            else:
                contextMenu.addAction("Add Selection to Pool",self.__Action_addSelectionToPool)
                contextMenu.addAction("Edit Songs",self.__Action_editSong__)
                
            contextMenu.addAction("Explore Containing Folder",self.__Action_Explore__)
            
            contextMenu.addSeparator()
            
            contextMenu.addAction("Select Columns",self.__Action_ColumnSelect)
            
            contextMenu.addSeparator()
            contextMenu.addMenu(MpGlobal.Window.menu_Sort)
            
            
            action = contextMenu.exec_( event.globalPos() )

            info_UpdateCurrent()
    
    def keyPressEvent(self,event):
        
        _shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier
        _ctrl = event.modifiers()&Qt.ControlModifier ==  Qt.ControlModifier
        if event.key() == Qt.Key_Up:
            self.__keyboard_scroll_UP__();
            R = list(self.selection)
            if len(R) > 0:
                UpdateStatusWidget(3,self.data[R[0]][MpMusic.PATH])

        elif event.key() == Qt.Key_Down:
            self.__keyboard_scroll_DOWN__();
            R = list(self.selection)
            if len(R) > 0:
                UpdateStatusWidget(3,self.data[R[0]][MpMusic.PATH])
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            # on key press of return add to the playlist the songs found in the selection
            #TODO CALL doubleclick event 
            R = self.getSelection()
            if len(R) > 0 :
                index = MpGlobal.Player.CurrentIndex + 1
                MpGlobal.Player.playList = MpGlobal.Player.playList[:index] + R + MpGlobal.Player.playList[index:]
                UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
                MpGlobal.Window.tbl_playlist.data = MpGlobal.Player.playList
                MpGlobal.Window.tbl_playlist.UpdateTable(MpGlobal.Window.tbl_playlist.getDisplayOffset(),MpGlobal.Player.playList)
        elif _ctrl and event.key() == Qt.Key_A:
            self.selection = set(range(len(self.data)));
            self.UpdateTable(-1);         
        
        elif not _shift and not _ctrl:
            MpGlobal.Window.txt_searchBox.setFocus()
            MpGlobal.Window.txt_searchBox.keyPressEvent(event)
    
    def updateDisplay(self,string = None):
        """
            convenience method for calling a new search.
        """
        searchText = MpGlobal.Window.txt_searchBox.displayText()
        
        if string != None:
            MpGlobal.Window.txt_searchBox.setText(string)
            searchText = string
            
        txtSearch_OnTextChange(searchText);

    def setColumnIDList(self,id_list,count):
        self.col_id = id_list;
        self.setColumnCount(count); # count = number of active columns
        self.FillTable()
              
    def setColumnCount(self,count):   
    
        header = [];
        for i in range(count):
            header.append( self.col_title[ self.col_id[i] ] )
            
        self.colCount = len(header)
        
        self.model.setColumnCount(count)
        self.model.setHorizontalHeaderLabels( header );
        
        self.resizeColumn();    # for each column set default sizes

    def __Action_editSong__(self):

        dialog = dialogSongEdit.SongEditWindow(MpGlobal.Window)

        dialog.initData(self.getSelection())
        
        dialog.exec_()
        
        del dialog
        
        self.FillTable()
    def __Action_Explore__(self):
        sel = self.getSelection()
        path = fileGetPath(sel[0][MpMusic.PATH])
        MpGlobal.Window.tbl_explorer.__load_Directory__(path)
        MpGlobal.Window.tabMain.setCurrentIndex(MpGlobal.Window.tab_Explorer)
    def __Action_addSelectionToPool(self):
        R = list(self.selection)
        for i in R:
            if self.data[i][MpMusic.SELECTED] == False:
                self.data[i][MpMusic.SELECTED] = True;
                MpGlobal.Player.selCount += 1;
                
        #MpGlobal.Player.selCount = len(Global.Player.library)   
        self.UpdateTable(-1);         

                
        UpdateStatusWidget(0,MpGlobal.Player.selCount) 
    def __Action_deleteSingle(self):
        R = self.getSelection()
        if len(R) == 1:
            message = "Are you sure you want to delete this song?\n"
            message += R[0][MpMusic.ARTIST] + " - " + R[0][MpMusic.TITLE]
            
            msgBox = QMessageBox(MpGlobal.Window)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(message)
            #    "Delete Song Confirmation", message,
             #   QMessageBox.NoButton, self)
            msgBox.addButton("Delete", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            
            if msgBox.exec_() == QMessageBox.AcceptRole:            
                MpGlobal.Player.libDelete.append( R[0] )
                MpGlobal.Player.library.remove(R[0])
                MpGlobal.Window.tbl_library.updateDisplay()
                Player_set_unsaved();
    def __Action_ColumnSelect(self):

        obj = MpGlobal.Window.tbl_library
        
        R = [0]*len(obj.col_id)
        
        #translate id numbers to strings
        for i in range(len(R)):
            R[i] = MpMusic.exifToString(obj.col_id[i])
        
        # create the dialog with the new string list
        dialog = dialogColumnSelect.DialogColumnSelect(R,obj.colCount)

        if dialog.exec_():
            print dialog.ResultList   
            print dialog.ActiveCount
            
            # retranslate to id numbers
            for i in range(len(R)):
                R[i] = MpMusic.stringToExif(dialog.ResultList[i])
            
            self.setColumnIDList(R,dialog.ActiveCount)
            
            self.resizeColumn()
                        
class TableGui(widgetTable.Table):
    """
        Quick Selection
        
        The quick selection tab allows you to select from the list of artists in your library. It also allows you to view statistics on each artist, and sort the list by these values.
        
        \\<table\\>
        Song Count | Displays the number of songs by that artist
        Playcount  | Displays the number of plays for that artist, equal to the sum of all plays of songs by that artist.
        Play Time  | Displays how long it would take to listen to each song by an artist once.
        Listen Time| This is the sum of Playcount * Length for each song by an artist
        Frequency  | This is the average frequency for all songs by the artist
        Rating Count | The sum of rated values for each song
        Count of Ratings | the number of songs rated by an artist
        \\</table\\>
        
        By clicking "Create" a new playlist will be made from the artists selected.
        
        By default an artist only appears in the list if there are at least 2 songs by that artist.
        
        use the build command to change the minimum value of songs per artist, "build 6" will set the minimum song count to 6.
    """
    dispElement = 3
    brush_selected = QBrush(QColor(0,205,25,255)) 
    brush_selectedOOF = QBrush(QColor(0,205,25,128)) 
    
    brush_text_default  = QBrush(QColor(  0,  0,  0)) 
    brush_text_favorite = QBrush(QColor(180, 10,  5)) 
    
    cbox1 = None;
    cbox2 = None;
    cbox3 = None;
    sbox1 = None;
    
    c_size = 90

    display_policy = 3
    
    artindex = 0
    selindex = 1
    favindex = 2
    
    mrange = 25

    def __init__(self,parent):
        header = ("Data","Artist","Data","Artist","Data","Artist")
        super(TableGui,self).__init__(parent,header)
        self.table.horizontalHeader().hide()
        
        self.table.setColumnWidth(0,self.c_size)  
        self.table.setColumnWidth(2,self.c_size)  
        self.table.setColumnWidth(4,self.c_size)  
        
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.table.setDragDropMode(QAbstractItemView.DragOnly)
        self.table.setObjectName("table_Quick")
    def calc_mrange(self):
        self.mrange = math.ceil(len(self.data) / float(self.display_policy))
    
    def UpdateTable(self,offset=0,array=None):
    
        self.calc_mrange()
        self.display_policy = self.getDisplayPolicy()
        super(TableGui,self).UpdateTable(offset,array)

    def adustScrollBar(self,offset=-1):
        
        if offset == -1:
            offset = self.scrollbar.value()
        self.scroll_MaxRange = max(0,self.mrange - self.rowCount + 4) 
        self.scrollbar.setMaximum(self.scroll_MaxRange)
        self.scrollbar.setPageStep(self.rowCount)
        self.scrollbar.setValue(offset)
        
        assert self.scrollbar.value() >= 0, "OFFSET WRITE ERROR m:%d M:%d v:%d"%(self.scrollbar.minimum(),self.scrollbar.maximum(),self.scrollbar.value())
    
    
    def FillTable(self,offset=-1):    
        """fill the table with data, starting at index offset, from the Display Array"""
        # mrange is the max range for the current width
        self.calc_mrange()

        if offset < 0 :
            offset = self.scrollbar.value()
        else:
            self.scrollbar.setValue(offset)
            
        size = len(self.data) # in case size is zero, prevent any drawing to it
        
        
        
        #S = [self.data,];
        # collect the data to be displayed into rows based off of the display policy
        _size = len(self.data)/self.display_policy
        #_size = self.display_policy + len(self.data)/self.display_policy - 1;
        
        S = [None]*(_size+1)
        # initialize the display array with empty lists
        for i in range(len(S)):
           S[i] = []
        # finally, add the data to the display list
        for i in range(len(self.data)):
            S[i%(_size+1)].append(self.data[i])
            #if self.data[i][0] == u"K-On!": # debug K-on was on a fringe border case thingy
            #    print size,_size,i;
                   
        for i in range(self.rowCount):
            k = i+offset; # the k'th element of the data array
            
            if k < self.mrange+1 and 0 <= k < _size+1:
                
                self.b1 = self.brush_default
                self.b2 = self.brush_default
                self.b3 = self.brush_default
                
                self.c1 = self.brush_text_default
                self.c2 = self.brush_text_default
                self.c3 = self.brush_text_default
                
                R = self.FillRow(S,k) # returns formatted data for the table

                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),R[j])
                    
                #if self.dispElement in (4,5):
                self.model.setData(self.model.index(i,0),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,2),Qt.AlignRight,Qt.TextAlignmentRole)
                self.model.setData(self.model.index(i,4),Qt.AlignRight,Qt.TextAlignmentRole)
                #else:
                #    self.model.setData(self.model.index(i,0),Qt.AlignLeft,Qt.TextAlignmentRole)
                #    self.model.setData(self.model.index(i,2),Qt.AlignLeft,Qt.TextAlignmentRole)
                #    self.model.setData(self.model.index(i,4),Qt.AlignLeft,Qt.TextAlignmentRole)
                
                
                self.model.setData(self.model.index(i,0),self.b1,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,1),self.b1,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,2),self.b2,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,3),self.b2,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,4),self.b3,Qt.BackgroundRole)
                self.model.setData(self.model.index(i,5),self.b3,Qt.BackgroundRole)
                
                self.model.setData(self.model.index(i,1),self.c1,Qt.ForegroundRole)
                self.model.setData(self.model.index(i,3),self.c2,Qt.ForegroundRole)
                self.model.setData(self.model.index(i,5),self.c3,Qt.ForegroundRole)
                
            else:
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),"")
                    self.model.setData(self.model.index(i,j),self.brush_default,Qt.BackgroundRole)

    def FillRow(self,data,index):

        p = self.display_policy
        r = len(self.data)
        s = r/self.display_policy

        if index >= len(data):
            return ["","","","","",""]
            
        data = data[index]   # to confuse you
        size = len(data)
        
        if size == 0:
            return ["","","","","",""]
            
        str1 = self.itemToString(data[0])
        str2  = ""
        str3  = ""
        
        str1a = data[0][0]
        str2a = ""
        str3a = ""
        
        if data[0][self.selindex]: self.b1 = self.brushSelectionColor();
        if data[0][self.favindex]: self.c1 = self.brush_text_favorite
           
        if size > 1:
            str2 = self.itemToString(data[1])
            str2a = data[1][0]
            if data[1][self.selindex]: self.b2 = self.brushSelectionColor();
            if data[1][self.favindex]: self.c2 = self.brush_text_favorite
        if size > 2:
            str3 = self.itemToString(data[2])
            str3a = data[2][0]
            if data[2][self.selindex]: self.b3 = self.brushSelectionColor();
            if data[2][self.favindex]: self.c3 = self.brush_text_favorite
  
        return [str1,str1a,str2,str2a,str3,str3a]

    def itemToString(self,item):
        """
            convert a index in the display data
            to a formatted string for display
        """
        
        if self.dispElement in (5,6):
            return "%s"%convertTimeToString(item[self.dispElement])
        else:
            return "%d"%item[self.dispElement]
    
    def indexElementToString(self,index):
        """
            convert a index in the display data
            to a formatted string for display
        """
        
        if self.dispElement in (5,6):
            return "%s "%convertTimeToString(self.data[index][self.dispElement])
        else:
            return "%d"%self.data[index][self.dispElement]
          
    def leftPressEvent(self,item,event): 
    
        offset = self.getDisplayOffset()
        
        row = item.row()
        col = item.column()
        
        i = self.positionToIndex(col,row)

        if i < len(self.data):
            self.data[i][1] = not self.data[i][1]
        
    def leftReleaseEvent(self,item,event):
        s = self.calc_hvalue();  
        UpdateStatusWidget(3,"Playlist Length: %d. Maximum Songs per Artist: %d."%(MpGlobal.PLAYLIST_SIZE,s))
        self.FillTable()
       
    def rightClickEvent(self,event):
    
        item = self.table.indexAt(event.pos())
        
        if item.row() >= 0:
            row = item.row()
            col = item.column()
            
            i = self.positionToIndex(col,row)
            if i < len(self.data):
                R = self.data[i][:]
                if not self.data[i][self.favindex] :
                    Settings.FAVORITE_ARTIST.append(R[0])
                    self.data[i][self.favindex] = True
                else:
                    for j in range(len(Settings.FAVORITE_ARTIST)):
                        if Settings.FAVORITE_ARTIST[j] == R[0]:
                            Settings.FAVORITE_ARTIST.pop(j)
                            break
                    self.data[i][self.favindex] = False
                #string = ""
                #for artist in Settings.FAVORITE_ARTIST:
                #    string += "%s, "%artist.encode('unicode-escape')
                #debug( string )
                self.FillTable()
            
    def calc_hvalue(self):
        s = 0
        for i in self.data:
            if i[self.selindex]:
                s+=1;
                
        if (s>1):
            s = 1 + MpGlobal.PLAYLIST_SIZE/s;  
        elif s==1:
            s =  MpGlobal.PLAYLIST_SIZE/s;
        else:
            s =  MpGlobal.PLAYLIST_SIZE;
            
        return s;
    
    def clearSelection(self):
        UpdateStatusWidget(3,"");
        for data in MpGlobal.Player.quickList:
            data[1] = False
        self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.quickList)
   
    def newPushed(self):
        s = self.calc_hvalue();
            
        processTextInput("new -h %d -p" % (s)) # this is called 'efficient'
    def __CBOX_CHANGE_DISPLAY__(self,index):
        self.dispElement = index + 3
        #print self.dispElement
        self.FillTable()
    def __CBOX_SORT_DISPLAY__(self,index=-1):
        
        value = self.cbox3.checkState() == Qt.Checked
        
        if index != 0:
            index += 2
        if index not in (0,7):
            value = not value
        #print self.data[0][index]
        if index == self.artindex:
            k = lambda song: sort_parameter_str(song,index)
        else:    
            k = lambda song: song[index]

        MpGlobal.Player.quickList.sort(key = k, reverse=value )
        
        self.FillTable()
        #self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.quickList)
        
    def __CHECK_STATE_CHANGE__(self,checkState):
        self.__CBOX_SORT_DISPLAY__(self.cbox2.currentIndex())
    
    def __SBOX_Value_Changed__(self,value):
        MpGlobal.PLAYLIST_GUI_MINIMUM_RATING = value
    
    def resizeEvent(self,event):
        self.resize_Column()
        #(self.display_policy - 1) + 
        self.calc_mrange()
        
        newmax = max(0,self.mrange - int(self.rowCount-2))
        
        self.scrollbar.setMaximum(newmax)
        
    def resize_Column(self):
        #w1 = self.table.columnWidth(0)
        w2 = self.table.width()
        
        self.display_policy = self.getDisplayPolicy()
        p = self.display_policy
        
        if p == 3:
            w2 = max( (w2-(self.c_size*3))/3,self.c_size*2)
        elif p == 2:
            w2 = max( (w2-(self.c_size*2))/2,self.c_size*2)
        else:
            w2 = max( w2-self.c_size,self.c_size*2)
            
        self.table.setColumnWidth(1,w2)  
        self.table.setColumnWidth(3,w2)  
        self.table.setColumnWidth(5,w2) 
        
    def getDisplayPolicy(self):
        """
            return the number of columns to make visible
            based off of the width of the display
        """
        
        w2 = self.table.width()
        
        # the magic number here, 9 and 6 come from the following
        #   3 (or 2) data display columns at c_size width
        #   3 (or 2) columns for artist name at 2*c_size width)
        
        if w2 > (self.c_size*9):
            return 3
        elif w2 > (self.c_size*6):
            return 2
        else:
            return 1

    def positionToIndex(self,col,row):
        d = self.getDisplayOffset()
        p = self.display_policy
        r = len(self.data)
        s = r/2
        t = r/3 
        
        #print row,col
        
        c = (col / 2)
        
        i = 0
        
        if p == 3 :
            i = t * c + c
        if p == 2 :
            i = s * c + c
        #if c > 0 :
        #    i += 1

        return row + d + i
        
    def indexToPosition(self,pos):
        d = self.getDisplayOffset()
        p = self.display_policy
        r = len(self.data)
        s = r/2
        t = r/3 
        
        col = 0
        row = 0
        
        if p == 3 :
            if pos > 2*t :
                col = 2
                row = pos - 2*t - 1
            elif pos > t:
                col = 1
                row = pos - t - 1
            else:
                col = 0
                row = pos
        elif p == 2 :
            if pos > s:
                col = 1
                row = pos - s - 1
            else:
                col = 0
                row = pos
        else:
            row = pos
        
        
        return (col,row)
            
class TableExternal(widgetTable.Table):
    def __init__(self,parent):
        header = ("Path",)
        super(TableExternal,self).__init__(parent,header)
        #self.table.setDragDropMode(QAbstractItemView.DragOnly)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    def FillRow(self,index):
        return [self.data[index],]
    def keyReleaseEvent(self,event):
        """
            Delete selected songs from the list of songs
            to load, when the delete key is pressed
        """
        if event.key() == Qt.Key_Delete :
            R = list(self.selection)
            R.sort(reverse = True)
            cindex_flag = False
            for x in R:
                MpGlobal.Player.external.pop(x)
            self.selection = set()
            self.UpdateTable(self.getDisplayOffset(),MpGlobal.Player.external)

    def resizeEvent(self,event):
        self.resize_Column()
        
    def resize_Column(self):
        #w1 = self.table.columnWidth(0)
        w2 = self.table.width()
        self.table.setColumnWidth(0,w2-1) 
        
class TablePLEditor(widgetTable.HPageTable):
    """ a table element that is linked with another similar table"""
    oTable = None
    oDataSrc = None # the other array of data
    DataSrc = None  # source for data
                    # data is therefore the display array
    DataSize = 0;
    objectList = None
    textEdit = None
    
    isRight = False
    
    lastSearch = 0;
    
    def __init__(self,parent,dragType="Unkown",DragReceive="None"):
        header = ("Artist","Title","Album")
        super(TablePLEditor,self).__init__(parent,header)
        self.setDragType("dragTableEditor_"+dragType)
        self.setDragReceiveType("dragTableEditor_"+DragReceive)
        
    def setTables(self,o):
        self.oTable = o # the other table in the set of 2
    def setTextEdit(self,o):
        self.textEdit = o # the text editor
    def setDataSrc(self,o):
        self.DataSrc = o # the array of data.
    def setOtherDataSrc(self,o):
        self.oDataSrc = o # the array of data.
    def setObjectList(self,o):
        self.objectList = o # the array of data.
        
    def dropEvent(self,event,row):
        if event.mimeData().hasText == False :
            return;
        if event.mimeData().text() not in self.dragReceive :
            return; # make sure that the drag is of valid type
          
        self.moveDataFromSibling()
        
        offset = self.oTable.getDisplayOffset()
        if offset == self.oTable.scroll_MaxRange:
            offset -= 1
                
        self.oTable.UpdateTable(offset)
            
        
    def keyReleaseEvent(self,event):
        if self.isRight :
            if event.key() == Qt.Key_Delete :
                self.oTable.moveDataFromSibling()
                
                offset = self.getDisplayOffset()
                if offset == self.scroll_MaxRange:
                    offset -= 1
                        
                self.UpdateTable(offset)
                
    
    def columnClicked(self,col):
        # create a list of columns, selecting the clicked one.
        id = (
             MpMusic.ARTIST, \
             MpMusic.TITLE, \
             MpMusic.ALBUM )[col]
             
        dir = self.lastSearch == col   

        self.table.horizontalHeader().setSortIndicator(col,dir)  
        
        sortList(self.DataSrc,id,dir)
        # perform a search and update the table

        if self.lastSearch == col:
            self.lastSearch = -1;
        else:
            self.lastSearch = col
        
        self.runSearchUpdate(self.objectList[1].text())

    
    def moveDataFromSibling(self):
        """
            Take the selected elements from the sibling table 
            remove them from that table and add them to the data in this table
            Sort this tables data, and redisplay both tables
        """
        sel = self.oTable.getSelection()
        listRemoveElements(self.oTable.DataSrc,sel)
        self.DataSrc += sel
        
        sortList(self.data,MpMusic.ARTIST)
        
        self.oTable.selection = set()
        self.selection = set()
        
        self.runSearchUpdate(self.textEdit.displayText())
        self.oTable.runSearchUpdate(self.textEdit.displayText())

        tl = self.objectList[2] 
        tr = self.objectList[3] 

        tr.DataSize = 0    
        for item in tr.DataSrc:
            tr.DataSize += item[MpMusic.FILESIZE]
        tr.DataSize /= 1024 # to mB 
        
        UpdateStatusWidget(3,"%s %s FileSize: %dMB"%(len(tl.data),len(tr.data),tr.DataSize))
        
    def FillRow(self,index):
        R = [""]*self.colCount;
        R[0] = self.data[index][MpMusic.ARTIST]
        R[1] = self.data[index][MpMusic.TITLE]
        R[2] = self.data[index][MpMusic.ALBUM]
        return R
    
    def runSearch(self,text):
        if text == "" :
            self.data = self.DataSrc
        else:
            so = SearchObject(text)
            self.data = so.search(self.DataSrc)
            
           
        
    def runSearchUpdate(self,text):
        self.runSearch(text)
        self.UpdateTable(self.getDisplayOffset(),self.data)
    
    """
        The Following are private methods and act as a place for a new tab
        to contain functions.
    """
    
    def __text_edit__(self,text):
        """ private method
            this acts as the only place that a text edit box can be hooked up to
            this table, and the other table. Because there are two tables
            the lineedit needs to be hooked up to one of the copies of this function
        """
        # clear the selection
        self.selection = set()
        self.oTable.selection = set()
        # reset the view to the top
        self.setDisplayOffset(0)
        self.oTable.setDisplayOffset(0)
        
        self.runSearchUpdate(text)
        self.oTable.runSearchUpdate(text)
        
        tl = self.objectList[2] 
        tr = self.objectList[3]  
        
        tr.DataSize = 0    
        for item in tr.DataSrc:
            tr.DataSize += item[MpMusic.FILESIZE]
        tr.DataSize /= 1024 # to mB 
        
        UpdateStatusWidget(3,"%s %s FileSize: %dMB"%(len(tl.data),len(tr.data),tr.DataSize))
        
    def __btn_load__(self,bool=False):
        
        tab   = MpGlobal.Window.tabMain
        index = tab.currentIndex()
        
        path = QFileDialog.getOpenFileName(MpGlobal.Window,
                "Open Playlist File",
                MpGlobal.installPath+"playlist/",
                "M3U Files (*.playlist)")
                
        tl = self.objectList[2] 
        tr = self.objectList[3] 
        
        R = MpGlobal.Player.library[:]
        # get the list of songs
        # remove those songs from the left display list
        if path != "":
            S = playListLoad(path,R)
            listRemoveElements(R,S)
            # update the data pools
            tl.DataSrc = R
            tr.DataSrc = S
            
            # set the name of the tab

            self.objectList[0] = fileGetName(path)
            MpGlobal.Window.tabMain.setTabText(index,self.objectList[0])
            tl.runSearchUpdate("")
            tr.runSearchUpdate("")
            return True
        else:
            return False
            
        UpdateStatusWidget(3,"%s %s FileSize: %dMB"%(len(tl.data),len(tr.data),tr.DataSize))

    def __btn_save__(self,bool=False):
        
        tab   = MpGlobal.Window.tabMain
        index = tab.currentIndex()
        
        path = QFileDialog.getSaveFileName(MpGlobal.Window,
                "Save Playlist File",
                MpGlobal.installPath+"playlist/",
                "M3U Files (*.playlist)")
                
        tl = self.objectList[2] 
        tr = self.objectList[3] 
        if path != "":
            playListSave(path,tr.DataSrc) 
            self.objectList[0] = fileGetName(path)
            MpGlobal.Window.tabMain.setTabText(index,self.objectList[0])
            return True
        else:
            return False
    
    def __btn_close__(self,bool=False):
        tab   = MpGlobal.Window.tabMain
        tabbar = tab.tabBar();
        #index = tab.currentIndex()
        index = -1;
        for i in range(tab.count()):
            if tabbar.tabData(i) == self:

                index = i;
        if index == -1:
            return;
        #index = self.objectList[4]
        #object = [name,edit,tbl_left,tbl_rite,index,pagem,splitter]
        # remove self from the list of open editors
        for x in range(len(MpGlobal.Window.editorTabs)):
            if MpGlobal.Window.editorTabs[x] == self.objectList:
                MpGlobal.Window.editorTabs.pop(x)
                break
        
        del self.objectList[0]
        del self.objectList[1]
        del self.objectList[2]
        del self.objectList[3]
        #del self.objectList[5]
        #del self.objectList[6]
                
        del self.DataSrc
        del self.data
        self.objectList  = None;
        
        del self.oTable.DataSrc
        del self.oTable.data
        self.oTable.objectList = None
        
        MpGlobal.Window.tabMain.removeTab(index)

    def __btn_play__(self,bool=False):
        
        for song in self.objectList[3].DataSrc:
            if song[MpMusic.SELECTED] == False :
                MpGlobal.Player.selCount += 1
                song[MpMusic.SELECTED] = True
        UpdateStatusWidget(0,MpGlobal.Player.selCount)    
        registerNewListAsPlayList(self.objectList[3].DataSrc,autoLoad = True)
        
class TableFileExplorer(widgetTable.Table):
    """
        Main controller for a File System Explorer tab
    """
    # use data as the main store
    type = 0 # type of record
    name = 1 # name part of path
    path = 2 # path of record
    flag = 3 # True when already in library
    song = 4 # the matching song with any entry
    f_none=0
    f_exists = 1
    f_invalid = 2
    f_pending = 4 #TODO new value
    t_dir = 1
    t_mp3 = 2
    t_otr = 4
    __act_dir1__ = ""
    __act_dir2__ = ""
    __act_row__ = 0
    
    currentPath = "C:\\"
    textEditor = None
    icon_dir = None
    icon_mp3 = None
    brush_highlight1 = QBrush(QColor(200,200,0,48))
    brush_highlight2 = QBrush(QColor(200,0,0,48))
    brush_highlight3 = QBrush(QColor(0,0,200,48))
    
    #edit = None;
    contextMenu = None # for songs
    
    cut_file = []   # the list of [path,SONG=None] items that will be pasted somewhere new
    cut_folder = "" # the path to the folder that will be moved on paste
    
    def __init__(self,parent,textEdit):
        header = ("   ","Path")
        super(TableFileExplorer,self).__init__(parent,header)
        self.textEditor = textEdit
        self.__load_Directory__(self.currentPath)

        self.rowSpacing = 4
        self.table.horizontalHeader().hide()
        #myHeader = self.table.horizontalHeader()
        #myHeader.setClickable(False)
        #myHeader.setDefaultAlignment(Qt.AlignLeft)
        #myHeader.setResizeMode(1,QHeaderView.Stretch)
        self.table.resizeColumnToContents(0)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.manageDriveList()
        self.textEditor.activated.connect(self.__index_Change__)
        
    def FillTable(self,offset=-1):    
        """fill the table with data, starting at index offset, from the Display Array"""
        R = []
        k=0;
        if offset < 0 :
            offset = self.scrollbar.value()

        size = len(self.data) # in case size is zero, prevent any drawing to it
        for i in range(self.rowCount):
            k = i+offset; # the k'th element of the data array
            
            if k < len(self.data) and size > 0:
                R = self.FillRow(k)
                brush = self.FillRowColor(k)
                self.model.setData(self.model.index(i,0),R[0],Qt.DecorationRole)
                self.model.setData(self.model.index(i,1),R[1])
                
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),brush,Qt.BackgroundRole)
            else:
                self.model.setData(self.model.index(i,0),None,Qt.DecorationRole)
                self.model.setData(self.model.index(i,1),"")
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),self.brush_default,Qt.BackgroundRole)
            
    def FillRow(self,index):
        if self.data[index][self.type] == self.t_dir:
            return [MpGlobal.icon_Folder,self.data[index][self.name]]
        else:
            return [MpGlobal.icon_None,self.data[index][self.name]]
    
    def FillRowColor(self,index):
        if index in self.selection:
            if self.table.hasFocus() :
                return self.brush_selected
            else:
                return self.brush_selectedOOF
        elif self.data[index][self.flag] == self.f_pending:
            return self.brush_highlight3
        elif self.data[index][self.flag] == self.f_invalid :
            return self.brush_highlight2
        elif self.data[index][self.flag] == self.f_exists :
            return self.brush_highlight1
        return self.brush_default
    
    def rightClickEvent(self,event):
    
    
        self.FillTable()
        
        item = self.table.indexAt(event.pos())
        row = item.row() + self.getDisplayOffset()
            
        if len(self.selection) > 0 and row < len(self.data):

        # modify the context menu based on click context
            t = self.data[row][self.type]
            contextMenu = QMenu(self.table)
            
            #contextMenu.addSeparator()
            self.__act_dir1__ = self.data[row][self.path]
            self.__act_dir2__ = self.currentPath
            self.__act_row__  = row;
            if t == self.t_mp3:
                contextMenu.addAction("Play Song",self.__Action_play_song__)
                contextMenu.addAction("Add to Library",self.__Action_load_song__)
                contextMenu.addSeparator()    
                contextMenu.addAction("Rename File",self.__Action_Rename_File)
                if len(self.cut_file) > 0:
                    contextMenu.addAction("paste %d File%s Here"%(len(self.cut_file),'s' if len(self.cut_file)>1 else ""),self.__Action_paste_file)
                elif self.cut_folder != "":
                    contextMenu.addAction("paste Folder",self.__Action_paste_folder)
                contextMenu.addAction("cut File%s"%('s' if len(self.selection) > 1 else ""),self.__Action_cut_file)
                
                contextMenu.addAction("New Folder",self.__Action_NewFolder)
            else:
                contextMenu.addAction("Open "+self.data[row][self.name],self.__Action_open_dir__)
                contextMenu.addSeparator()    
                contextMenu.addAction("Rename Folder",self.__Action_Rename_Folder)
                contextMenu.addAction("New Folder",self.__Action_NewFolder)
                if len(self.cut_file) > 0:
                    contextMenu.addAction("paste %d File%s Here"%(len(self.cut_file),'s' if len(self.cut_file)>1 else ""),self.__Action_paste_file)
                elif self.cut_folder != "":
                    contextMenu.addAction("paste Folder",self.__Action_paste_folder)
                if len(self.selection) == 1 :
                    contextMenu.addAction("cut Folder",self.__Action_cut_folder)
                    
                
                
            contextMenu.addSeparator()
            contextMenu.addAction("Open Directory",self.__Action_explore_folder) #+dirGetParentDirName(self.currentPath)
            
            #contextMenu.addAction("Explore "+self.parentFolderName)
            #self.__Show_Context_Menu__(event.globalPos(),row)
            # iconText returns the text used in constructing the menu
            
            action = contextMenu.exec_( event.globalPos() )
                #if action != None:
                #    text = action.iconText()
                #    print text
                #self.FillTable()  
            #self.table.removeChild(contextMenu)
            del contextMenu
            
    def DoubleClick(self,item):
        offset = self.getDisplayOffset()
        index = offset+item.row()
        
        path = self.data[index][self.path]
        
        if os.path.isdir(path):
            #self.parentFolderName = self.data[index][self.name]
            self.__load_Directory__(path)
            
        elif pathMatchExt(path):
            self.__Action_play_song__(path)
        
    def resizeEvent(self,event):
        self.resize_Column()
        
    def resize_Column(self):
        w1 = self.table.columnWidth(0)
        w2 = self.table.width()
        self.table.setColumnWidth(1,w2-w1-1)   
        
    def __sortData__(self,reverse=False):
        g = lambda x: x[self.name]
        h = lambda x: x[self.type]
        
        self.data.sort(key = g, reverse=reverse )
        self.data.sort(key = h, reverse=reverse )
        
    def __load_Directory__(self,path):

        path = unicode(path)
        self.data = []
        
        self.currentPath = path
        
        self.selection= set()
        
        try :
            R = os.listdir(path)
            # with the files found in the directory set the data array to contain
            
            self.__manage_FileList__(R,path)
                
            if len(self.data) == 0 :
                self.data = [ [self.t_otr,"No Files","",False] ,]
                
            self.textEditor.setEditText(self.currentPath)

            #self.textEditor.setCurrentIndex(0)
            # update the table with the new data, and move the offest to zero    
            self.UpdateTable(0)
            
            self.manageDriveList()
        except:
            pass
        
    def __manage_FileList__(self,R,path):
        """ R, as list of fname in path
            small list is roughly 200 items or less
            a large list needs special work
        """
        for fname in R:
            temppath = os.path.join(path,fname)
            # append new folders to the pathlist
            # append files to the file list
            tempsong = None
            #TODO reset checkattrib
            if os.path.isdir(temppath) :#and dirCheckAttribNormal(temppath):
                self.data.append( [self.t_dir,"%s"%fname,temppath,False,None] ) 
            elif pathMatchExt(fname):
                value = self.f_none
                # we know that the path is a song, check if it is in the library
                
                for song in MpGlobal.Player.library:
                    if comparePath(song[MpMusic.PATH],temppath) :
                        value = self.f_exists
                        tempsong = song
                        break;
                #TODO NOT REALLY SURE THIS APPIES ANYMORE:
                # i used to pend songs then load them later, but no longer
                if tempsong == None and len(MpGlobal.Player.external) > 0:
                    for ex_path in MpGlobal.Player.external:
                        if comparePath(ex_path,temppath) :
                            value = self.f_pending
                            break;
                    
                #if not pathIsUnicodeFree(temppath):
                #    value = self.f_invalid 
                self.data.append( [self.t_mp3,fname,temppath,value,tempsong] ) 
        
            MpGlobal.Application.processEvents()
        self.__sortData__();
             
    def __Goto_ParentDir__(self):
        dir = fileGetParentDir(self.currentPath)
        
        if dir != "":
            self.__load_Directory__(dir)
    
    def __Goto_NewDir__(self):
        path = self.textEditor.currentText();
        if os.path.isdir(path):
            self.__load_Directory__(path)
            
    def __index_Change__(self,index):
        path = self.textEditor.itemText(index);
        if os.path.isdir(path):
            self.__load_Directory__(path)
            
    def __Action_play_song__(self,path=None):
        if path == None and len(self.selection) > 0:
            path = self.getSelection()[0][self.path]
            
        if path != None:# and pathIsUnicodeFree(path):
            MpGlobal.Player.playState = MpMusic.PL_NO_PLAYLIST
            temp = id3_createSongFromPath(path)
            if MpGlobal.Player.load(temp) :
                MpGlobal.Player.play()
                
    def __Action_load_song__(self):
        """ add the selected songs to the list of songs to load"""
        self.cut_folder = ""
        self.cut_file = []
        
        for i in self.selection:
            f = self.data[i][self.flag]
            if f != self.f_exists and f != self.f_invalid and f != self.f_pending and self.data[i][self.type] == self.t_mp3:
                self.data[i][self.flag] = self.f_pending
                MpGlobal.Player.external.append(self.data[i][self.path])
                
        external_Load_Start()
        Player_set_unsaved();
        
    def __Action_open_dir__(self):
        self.__load_Directory__(self.__act_dir1__)
    
    def __Action_explore_folder(self):
        """ open the folder contained in __act_dir2__
            act is special variable set when a context menu is opened
        """
        try:
            os.startfile(self.__act_dir2__)
        except:
            pass

    def __Action_NewFolder(self):
        """
            create a new folder with the given name
        """
        dialog = dialogRename("New Folder","Create Folder")
        
        if not dialog.exec_():
            print "Folder Creation Reject"
            return;

        name = dialog.edit.displayText();
        
        name = OS_FileName_Correct(name).strip() 

        path = os.path.join(self.currentPath,name);
        
        if not os.path.exists(path):
            self.data.insert(0, [self.t_dir,name, path ,False,None] ) 
            os.mkdir(path);
            self.FillTable();
    
    def __Action_Rename_File(self):
        """
            Rename a single file or a group of files.
        """
        self.cut_folder = ""
        self.cut_file = []
        
        R = list(self.selection)
        print len(R)
        fprompt = "";
        new_name = ""

        #determine the prompt for the new file name
        if len(R) == 0:  
            print "No Items Selected to rename"
            return
        else:
            fprompt = fileGetName(self.data[R[0]][self.name])
        
        prompt = 'Pattern Rename songs:\ne.g. $art => artist_name\nAll standard search terms apply except dates.'    
        dialog = dialogRename(fprompt,'Rename File',prompt)  
        
        #get the new file name
        if dialog.exec_():
                new_name = dialog.edit.displayText();
        else: 
            debug("User canceled rename request")
            return;    
        
        # enough for now, this should be expanded into renaming multiple songs
        # by using the already defined .art .ttl etc. ~ 
        # then appending incrementing numbers for any colliding songs.
        
        # a template song is used to check the pattern renaming, and then
        # askthe user if this is what they want.
        template_song = None
        for row in R: 
            s = self.data[row][self.song]
            if s != None:
                template_song = s;
                break;
            # if template_song != None and s != None and template_song != s:
            #     template_song = None;
            #     break;  
            continue;
            
        sample = OS_FileName_Correct( MpMusic.expandExifMacro(new_name,'$',template_song) )
        
        if sample != new_name: # show a second prompt if the user wants pattern replacement
            message = 'Songs to Modify: %d\n'%len(R)
            message += 'Rename Pattern:\n%s\n'%new_name
            message += 'Sample:\n%s\n'%sample
            message += 'Continue?:'
            msgBox = QMessageBox(MpGlobal.Window)
            msgBox.setWindowTitle('Confirm Rename')
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText(message)
            #    "Delete Song Confirmation", message,
             #   QMessageBox.NoButton, self)
            msgBox.addButton("Rename", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            
            if msgBox.exec_() != QMessageBox.AcceptRole:
                debug("Rename Request Canceled By User")
                return;
        #
        filepath = self.__act_dir2__ # root path is the same for all selected songs
        
        for row in R:

            song = self.data[row][self.song]
            
            if song == None:
                continue;
                
            if song == MpGlobal.Player.CurrentSong:
                debug("File is currently in use")
                continue;

            fileext  = fileGetExt(self.data[row][self.name])
            
            name = MpMusic.expandExifMacro(new_name,'$',song)
            
            name = OS_FileName_Correct(name).strip() # strip illegal characters with a sudo whitlist
            
            if name != '':
                path = os.path.join(filepath,name+'.'+fileext)
                
                debug(path)

                if path != "" and not os.path.exists(path):
                    self._rename_file_(row,song[MpMusic.PATH],path)
            
        return;
        Player_set_unsaved();
        
    def __Action_Rename_Folder(self):
        
        #print "Current Folder: %s"%self.currentPath
        #print "Target  Folder: %s"%self.__act_dir1__ 
        #print "Working Folder: %s"%self.__act_dir2__ 
        #print "Renaming: %s"%self.__act_dir2__
        
        self.cut_folder = ""
        self.cut_file = []
        
        R = [] # list of songs in the target folder, and all sub folders
        
        folder_path = self.__act_dir1__   # root path to change
        root_path = self.__act_dir2__
        #TODO UNIX PATH CORRECT on root_path
        if isPosix:
            root_path = UnixPathCorrect(root_path)
        
        if root_path == "" or not os.path.exists(root_path):
            debug("Error Path Does Not Exist on File System:\n%s\n"%root_path)
            return;
            
        dirlist = [self.__act_dir1__, ]
        
        # this loop will gather all songs in the current library
        # that exist in child folders of the selected folder from the explorer window
        flag_AccessError = False # can't rename a folder if a child song is in use
        while len(dirlist) > 0:
            path = dirlist.pop()
            dir = os.listdir(path)
            
            for fname in dir:
                temppath = os.path.join(path,fname)
                # append new folders to the pathlist
                # append files to the file list
                tempsong = None
                #TODO reset checkattrib
                if os.path.isdir(temppath) :#and dirCheckAttribNormal(temppath):
                    dirlist.append( temppath )
                elif pathMatchExt(fname): # file is a playable song file

                    for song in MpGlobal.Player.library:
                        if comparePath(song[MpMusic.PATH],temppath) :
                            #print song
                            R.append(song)
                            if song == MpGlobal.Player.CurrentSong:
                                flag_AccessError = True;
                            break;
                    MpGlobal.Application.processEvents();
                    
            debug("%d Folders remaining"%len(dirlist))
        print " %d Songs will be affected"%len(R) 
        
        
        
        if flag_AccessError:
            debug("File is currently in use")
            return;
        
        # get the new folder name, and whether the user will commit to this 
        
        dialog = dialogRename(self.data[self.__act_row__][1],"Rename Folder")
        
        if dialog.exec_():
            print "accepted"
        else: 
            flag_AccessError = True
        
        new_name = dialog.edit.displayText();
        
        print flag_AccessError, new_name
        
        if flag_AccessError:
            debug("User canceled rename request")
            return;

        new_path = os.path.join(root_path,new_name)
        
        print "New Name: %s"%new_path
        
        try:
        
            os.rename(folder_path,new_path)
        
        except Exception as e:
            for i in e:
                debug("%s"%str(i))
                
        else:
            print "folder renamed..."
            self.data[self.__act_row__][1] = new_name;
            for song in R:
                song_path = song[MpMusic.PATH][len(folder_path):]
                # on unix/POSIX the player will do a PATHFIX then next time it is played
                song[MpMusic.PATH] = new_path+song_path
                print song[MpMusic.PATH]
        
        finally:
            self.FillTable()
        
        Player_set_unsaved();
        return;
    
    def __Action_cut_file(self):
        self.cut_folder = ""
        self.cut_file = []

        R = list(self.selection)
        for row in R: 
            p = self.data[row][self.path]
            s = self.data[row][self.song]
            self.cut_file.append([p,s])
        
    def __Action_paste_file(self):
        """
            take the selected files that were 'cut'
            and paste them to the target folder
        """
    
        dst = self.__act_dir2__
        
        for file,song in self.cut_file:
            self._paste_one_file(file,dst,song);
            
        self.cut_folder = ""
        self.cut_file = []
        #self.FillTable();
        self.__load_Directory__(self.currentPath);
        Player_set_unsaved();

    def _paste_one_file(self,src,dst_folder,song=None):
    
        src_name = fileGetFileName(src)
        src_dir  = fileGetPath(src)
        
        if not comparePath(src_dir,dst_folder):
        
            dst = os.path.join(dst_folder,src_name);
            
            try:
                os.rename(src,dst);
                print dst
                if song!=None:
                    song[MpMusic.PATH] = dst
            except:
                print "could not move file"
            else:
                self.data.insert(0, [self.t_mp3,src_name, dst,song!=None,song] ) 
    
    def __Action_cut_folder(self):
        """
            cutting a folder is as easy as saving the current selected folder
        """
        R = list(self.selection)
        
        self.cut_folder = ""
        self.cut_file = []
        
        if len(R) == 1:
            self.cut_folder = self.data[R[0]][self.path]
            
        print self.cut_folder
        
    def __Action_paste_folder(self):
            
        tar_dir  = self.__act_dir2__
        cut_name = fileGetFileName(self.cut_folder)
        cut_dir  = fileGetPath(self.cut_folder)
               
        if not comparePath(tar_dir,cut_dir) and \
            not comparePathLength(self.cut_folder,tar_dir) : # paths are not identicle , and src folder is not parent of child folder
            
            new_dir = os.path.join(tar_dir,cut_name);
            
            print new_dir
            
            try:
                os.rename(self.cut_folder,new_dir)
            except:
                print "could not move folder"
            else:
                self.data.insert(0, [self.t_dir,cut_name, new_dir,False,None] ) 
                self.FillTable();
        else:
            print "paste error"
        # clear the cut variables
        self.cut_folder = ""
        self.cut_file = []
        Player_set_unsaved();
    
    def _rename_file_(self,row,filepath,newpath):
        try:
            #debug(file)
            #debug(path)
            os.rename(filepath,newpath)
        
        except Exception as e:
            for i in e:
                debug("%s"%str(i))  
        else:
            song = self.data[row][self.song]
            if song != None:
                song[MpMusic.PATH] = newpath
            self.data[row][1] = fileGetFileName(newpath);
        finally:
            self.FillTable()
      
    def manageDriveList(self):
        drives = systemDriveList()
        #sub1 = ['%s/music/' % d for d in drives if os.path.exists('%s/music/' % d)]
        #sub2 = ['%s/player/' % d for d in drives if os.path.exists('%s/player/' % d)]
        if self.textEditor != None:
            # add some custom paths to the default list of drives
            # most of these are convenient for me, no one else has my file system
            sub = ['%smusic\\' % d for d in drives if os.path.exists('%s/music/' % d)]
            sub += ['%splayer\\' % d for d in drives if os.path.exists('%s/player/' % d)]
            sub += ['%sdiscography\\' % d for d in drives if os.path.exists('%s/discography/' % d)]
            sub += ['%sjapanese\\' % d for d in drives if os.path.exists('%s/japanese/' % d)]
            sub += ['%smisc\\' % d for d in drives if os.path.exists('%s/misc/' % d)]
        
        
            R = drives+sub
            R.sort()
            self.textEditor.clear()
            
            index = 0;
            if self.currentPath in R:
                index = R.index(self.currentPath)
            else:
                R = [self.currentPath,]+R
                
            for item in R:
                self.textEditor.addItem(item)

            self.textEditor.setCurrentIndex(index)
    
class ButtonPlay(widgetPlayButton.PlayButton):
    def sizeHint(self):
        return QSize(32, 32)
    def clickEvent(self):
        # there is a slight lag on the Player functions
        # query the state first and set to the opposite of that
        if self.location == 0 :
            self.state_btn1 = (MpGlobal.Player.state() == MpMusic.PLAYING)
            MpGlobal.Player.playPause()
        else:
            MpGlobal.Player.cont()
            self.state_btn2 = MpGlobal.Player.stopNext
            
    def updateDisplay(self, state = True):
        if state == True:
            self.state_btn1 = (MpGlobal.Player.state() == MpMusic.PLAYING)
        else:
            self.state_btn1 = True # show the play arrow
        self.state_btn2 = MpGlobal.Player.stopNext
        self.update()
        
class CurrentSongDisplay(widgetInfoDisplay.InfoDisplay):
    def mouseReleaseEvent(self,event):
        w = self.width()
        h = self.height()
        x = event.x()
        y = event.y()
        if x > w-16 and event.button() == Qt.LeftButton: # and left click
            if MpGlobal.Player.CurrentSong != None:
                MpGlobal.Player.CurrentSong[MpMusic.RATING] = self.int_rating
                if Settings.LOG_HISTORY:
                    history_log(MpGlobal.FILEPATH_HISTORY,MpGlobal.Player.CurrentSong,MpMusic.RATING)
        elif event.button() == Qt.RightButton:
            

            if MpGlobal.Player.CurrentSong != None:
                contextMenu = QMenu(MpGlobal.Window)
                contextMenu.addAction("Find Lyrics",self.__Action__GoTo_Lyrics__)
                contextMenu.addAction("Artist Wiki Page",self.__Action__GoTo_Wiki__)
                contextMenu.addAction("Explore Containing Folder",self.__Action__EXPLORE__)
                contextMenu.addAction("Search for Album",self.__Action_searchALBUM__)
                
                contextMenu.exec_( event.globalPos() )
                 
                del contextMenu             
        else: # left region left click
            # reset scrolling
            pass
    def __Action__GoTo_Wiki__(self):
        s = "http://en.wikipedia.org/w/index.php?search="
        s += MpGlobal.Player.CurrentSong[MpMusic.ARTIST][:].replace(" ","+")
        os.startfile(s)
    def __Action__GoTo_Lyrics__(self):
        s = "http://www.songmeanings.net/query/?q="
        s += MpGlobal.Player.CurrentSong[MpMusic.ARTIST][:].replace(" ","+")
        s += "&type=artists"
        os.startfile(s)
    def __Action__EXPLORE__(self):
        if MpGlobal.Player.CurrentSong != None:
            path = fileGetPath(MpGlobal.Player.CurrentSong[MpMusic.PATH])
            MpGlobal.Window.tbl_explorer.__load_Directory__(path)
            MpGlobal.Window.tabMain.setCurrentIndex(MpGlobal.Window.tab_Explorer)
    def __Action_searchALBUM__(self):
        if MpGlobal.Player.CurrentSong != None:
            s = ".art \""+MpGlobal.Player.CurrentSong[MpMusic.ARTIST][:]+"\""
            s += "; .abm \""+MpGlobal.Player.CurrentSong[MpMusic.ALBUM][:]+"\""
            
            MpGlobal.Window.tbl_library.updateDisplay(s);

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

class MpTimeBar(QScrollBar):

    mouseDown = False
    
    def __init__(self,parent):
        super(MpTimeBar,self).__init__(Qt.Horizontal,parent);
        
        self.actionTriggered.connect(self.actionEvent)
        self.sliderReleased.connect(self._sliderReleased);
        
    def periodicUpdate(self,value):
        if not self.mouseDown:
            self.setValue(value)
    
    def mousePressEvent(self,event):
        super(MpTimeBar,self).mousePressEvent(event)
        self.mouseDown = True;
    def mouseReleaseEvent(self,event):
        super(MpTimeBar,self).mouseReleaseEvent(event)
        self.mouseDown = False;
        s = 13  # width of one button
        x = event.x()-s;
        w = self.width()-s
        if x < w and MpGlobal.Player.CurrentSong != None:
            f = x/float(w)
            t = MpGlobal.Player.CurrentSong[LENGTH]
            p = int(f*t)
            MpGlobal.Player.setTime( p )
            
            #print "mouse release - %d/%d * %d = %d"%(x,w,t,p)
        
    def leaveEvent(self,event):
        super(MpTimeBar,self).leaveEvent(event)
        self.mouseDown = False;
        
    def actionEvent(self,action):
        #QAbstractSlider.SliderToMinimum
        #QAbstractSlider.SliderToMaximum
        #QAbstractSlider.SliderMove

        if action == QAbstractSlider.SliderSingleStepAdd:
            MpGlobal.Player.setTime(self.value()+15)
        elif action == QAbstractSlider.SliderSingleStepSub:
            MpGlobal.Player.setTime(self.value()-15)
            
        #elif action == QAbstractSlider.SliderPageStepSub:
        #    MpGlobal.Player.setTime(self.value()-5)
        
        #elif action == QAbstractSlider.SliderPageStepAdd:
        #    MpGlobal.Player.setTime(self.value()+5)
            

    def _sliderReleased(self):
        state = MpGlobal.Player.state()
        bar = MpGlobal.Window.bar_time

        if state == MpMusic.PLAYING:
            MpGlobal.Player.setTime(bar.value())
        elif state == MpMusic.PAUSED or state == MpMusic.NOTHINGSPECIAL:
            MpGlobal.Player.play()
            MpGlobal.Player.setTime(bar.value())
        else:
            bar.setValue(0)

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

class MpSTDDebug():

    def __del__(self):
        #sys.stdout = self.stdout
        pass
        
    def write(self, data):
        uni = unicode(data).strip()
        if len(uni) > 0:
            MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),uni)
        #self.stdout.write(data)         
   
class dialogRename(QDialog):
    def __init__(self,text='',title='Rename', prompt='', parent=None):
    
        super(dialogRename,self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 50)
        
        hbox = QHBoxLayout();
        vbox = QVBoxLayout(self);
        self.edit = LineEdit()

        self.btna = QPushButton("Accept")
        self.btnc = QPushButton("Cancel")
        
        hbox.addWidget(self.btnc)
        hbox.addWidget(self.btna)
        
        vbox.addWidget(self.edit)
        
        
        if len(prompt) > 0:
            vbox.addWidget(QLabel(prompt))
            
        vbox.addLayout(hbox)
        
        self.btna.clicked.connect(self.accept)
        self.btnc.clicked.connect(self.reject)
        self.edit.returnPressed.connect(self.accept)
        
        self.edit.setText(text)
    
   
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
    
    MpGlobal.Player.library = musicLoad(MpGlobal.FILEPATH_LIBRARY)
    MpGlobal.Player.playList = playListLoad(MpGlobal.FILEPATH_PLAYLIST_CURRENT,MpGlobal.Player.library)
    
    #(MpGlobal.Hiragana,MpGlobal.Katakana) = init_KanaTables()

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
        

        window.menu_Pref.addAction("Preferences",open_Settings)
        
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
    

def newPlayListEditor(self,name = "PlayList Editor"):
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
            
        #index = self.tabMain.addTab(pagem,MpGlobal.icon_file,name)
        index = self.tabMain.addTab(pagem,name)
        
        
        #vbox = QVBoxLayout(page)
        #vboxl = QVBoxLayout(pagel)
        #vboxr = QVBoxLayout(pager)
        
        hbox = QHBoxLayout()
        edit = LineEdit(pagem)
        btn1 = QPushButton(MpGlobal.icon_open,"",pagem)
        btn2 = QPushButton(MpGlobal.icon_save,"",pagem)
        #btn3 = QPushButton(MpGlobal.icon_AutoPLO,"",pagem) 
        btn4 = QPushButton("Play",pagem) 
        btnX = CloseTabButton(self);
        
        
        #hbox.addWidget(btn3) # close
        hbox.addWidget(btn1) # open
        hbox.addWidget(btn2) # save
        hbox.addWidget(edit)
        hbox.addWidget(btn4) # play   
        self.tabMain.tabBar().setTabButton (index,QTabBar.LeftSide,btnX)
        
        
        splitter = QSplitter(pagem)
        
        #lname = "Left_%d"%len(self.editorTabs)
        #rname = "Right_%d"%len(self.editorTabs)
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
        
        self.editorTabs.append( object )
        
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
        #else:
        #    super(QLineEdit,MpGlobal.Window.txt_searchBox).keyPressEvent(event)
        #pri nt event.key()
        
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
        

def open_Settings():
    dialog = SettingsWindow(None)


    if dialog.exec_():
        # save everything
        On_Close_Save_Data()
        

        
        
from MpScripting import *
from MpScriptingAdvanced import *
from MpCommands import *
from MpFileAccess import *
from MpPlayer import *
from MpEventHook import disableHook
from UnicodeTranslate import Translate
from MpThreading import Thread_LoadMedia
from dialogNewPlayList import *  
from dialogHelp import helpDialog     
        
