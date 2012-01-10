

# def tabbar_tab_changed(index=0):
#     """ already in MpApplication, and will need to be moved here"""
#     
    
import sys
import os

isPosix = os.name == 'posix'    
 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
 
import dialogSongEdit
import dialogColumnSelect
import dialogSync 
 
from widgetLineEdit import LineEdit

from MpGlobalDefines import *
from Song_Object import Song
from Song_LibraryFormat import * 
 
from datatype_hex64 import *

from widgetLargeTable import LargeTable

from widget_playbutton import *
from widget_currentSongDisplay import *
from widget_currentTimeDisplay import *

from table_playlist import * 
    
#TODO the auto playlist button needs one more button state
# a state for randomly picking one of the presets
    
class Frame_Main(QWidget):
    """
        set the layout for the main frame of the applicatiopn
        this will contain the command text box,
        display for the current song,
        and the playlist along with everything else
        
    """
    def __init__(self,parent):
        super(Frame_Main,self).__init__(parent)
        self.parent = parent 
        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(0)
        self.vbox.setMargin(0)
    
        # create all of the widgets
        self.init_TextEdit()
        self.init_TimeBar()
        self.init_DisplaySong()
        self.init_Table()
        self.init_Buttons()
    
    def init_TextEdit(self):
        window = self.parent # TODO convert this function
        
        window.txt_main = LineEditHistory(window)
        window.txt_main.keyReleaseEnter = processTextInput
        window.txt_main.setPlaceholderText("Command Input <Ctrl+K>")
        window.txt_main.setObjectName("Console")
        
        window.txt_main.setMinimumHeight(20)
        
        self.vbox.addWidget(self.parent.txt_main)
    
    def init_TimeBar(self):
        window = self.parent # TODO convert this function
    
        window.bar_time = MpTimeBar(window)
        #window.bar_time = QSlider(window)
        window.bar_time.setObjectName("MpMediaTime")
        window.bar_time.setPageStep(0)# slider is of length 'page step'
        
        # prev/next buttons
        window.btn_prev = QPushButton(window)#ButtonArrow(True) # mirror vertically
        window.btn_next = QPushButton(window)#ButtonArrow()

        window.btn_prev.setObjectName("MpMediaPrev")
        window.btn_next.setObjectName("MpMediaNext")
        
        window.btn_prev.setToolTip("Previous Song")
        window.btn_next.setToolTip("Next Song")
        
        window.hbox_timeBar = QHBoxLayout()
        window.hbox_timeBar.setSpacing(0)
        
        window.hbox_timeBar.addWidget(window.btn_prev)
        window.hbox_timeBar.addWidget(window.bar_time)
        window.hbox_timeBar.addWidget(window.btn_next)
    
        window.btn_prev.setFixedWidth(32)
        window.btn_next.setFixedWidth(32)
        window.btn_prev.setFixedHeight(16)
        window.btn_next.setFixedHeight(16)
    
    
        self.vbox.addLayout(self.parent.hbox_timeBar)
        self.vbox.addSpacing(4)
        
    def init_DisplaySong(self):
        window = self.parent
        # #########################################
        # Play Button, Display Labels
        window.hbox_playbutton = QHBoxLayout()

        window.btn_playstate = ButtonPlay()
        window.dsp_info = CurrentSongDisplay()
        window.dsp_info.text_title = "Select a Song to Play"
        window.dsp_info.text_album = "Drag and Drop music to Load"
        window.dsp_info.stopScrolling()
        window.dsp_info.setFixedHeight(48)
        window.dsp_info.update()
        
        window.btn_playstate.setToolTip("Play/Pause Current Song\nStop playback when current song finishes")
        # add button and vbox to the hbox
        window.hbox_playbutton.addWidget(window.btn_playstate)
        window.hbox_playbutton.addWidget(window.dsp_info)
        window.hbox_playbutton.setSpacing(0)
        
        window.btn_playstate.setFixedHeight(48)
        window.btn_playstate.setFixedWidth(48)
        
        self.vbox.addLayout(self.parent.hbox_playbutton)
        self.vbox.addSpacing(4)
        
    def init_Table(self):    
        window = self.parent
        window.tbl_playlist = LTable_PlayList(window) #TablePlayList(window)
        
        self.vbox.addWidget(self.parent.tbl_playlist.container)
        self.vbox.addSpacing(2)
        
    def init_Buttons(self):    
        window = self.parent
        #window.hbox_playbutton.addWidget(window.dsp_rate)
        # add the time bar and display to the vbox
        
        # set sizing for newly created widgets

        #window.dsp_rate.setFixedHeight(48)
        #window.dsp_rate.setFixedWidth(8)
        
        window.hbox_btn = QHBoxLayout()
        window.btn_clr = QPushButton(MpGlobal.icon_Trash,"",window)
        window.btn_sfl = QPushButton("Shuffle",window)
        window.btn_spn = QSpinBox(window)
        window.btn_apl = QPushButton(MpGlobal.icon_AutoPL,"",parent=window)
        
        window.btn_spn.setRange(0,9)
        window.btn_spn.setFixedWidth(32)
        window.hbox_btn.setSpacing(0)
        window.btn_clr.setToolTip("Clear current Playlist")
        s="Shuffle the remaining songs to be played\nIf songs in the playlist are selected, they will be shuffled in place"
        window.btn_sfl.setToolTip(s)
        s="Auto make a new playlist when\nthe current one finishes.\nNew Playlist will be made from a pool\nof songs from the indicated preset"
        window.btn_spn.setToolTip(s)
        window.btn_apl.setToolTip(s)
        # we need equal spacing on either side of the shuffle button
        # add spacers to make up for the width of widgets on the other side
        # don't argue with the AlignRight on the shuffle button, it just works to center
        window.hbox_btn.addWidget(window.btn_clr)
        
        if not isPosix: # adding a volume bar here instead
            window.hbox_btn.addSpacing(32) # equal to width of spinbox
        
        #window.hbox_btn.addSpacing(4)
        window.hbox_btn.addWidget(window.btn_sfl,0,Qt.AlignRight)
        window.hbox_btn.addWidget(window.btn_spn,0,Qt.AlignRight)
        window.hbox_btn.addWidget(window.btn_apl)
        #window.hbox_btn.addSpacing(4)
        
        window.btn_clr.setFixedWidth(24)
        #window.btn_sfl.setFixedWidth(50)
        window.btn_apl.setFixedWidth(24)
        
        window.btn_clr.clicked.connect(button_PlayList_Clear)
        window.btn_sfl.clicked.connect(button_PlayList_Shuffle)
        window.btn_apl.clicked.connect(button_PlayList_AutoPlayList)
        
        self.vbox.addLayout(self.parent.hbox_btn)
        self.vbox.addSpacing(2)
        
def button_PlayList_Clear():
    MpGlobal.Player.playList = []
    MpGlobal.Window.tbl_playlist.updateTable(0,MpGlobal.Player.playList)
    
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
    MpGlobal.Window.tbl_playlist.updateTable(-1,MpGlobal.Player.playList)
    
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
 
 
from MpScripting import *
from MpSort import *
from Song_Search import *
from MpCommands import *

from MpApplication import *

from SystemPathMethods import *
from MpPlayer import *
from MpEventHook import initHook,disableHook
from UnicodeTranslate import Translate
from dialogNewPlayList import *  
from dialogHelp import helpDialog     
from MpEventMethods import *        
from MpPlayerThread import MediaPlayerThread        
        
        