
import sys
import os

isPosix = os.name == 'posix'

import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import widgetInfoDisplay
from SystemPathMethods import *
from Song_Object import Song
from datatype_hex64 import *

from MpGlobalDefines import *

from MpSongHistory import *

class CurrentSongDisplay(widgetInfoDisplay.InfoDisplay):
    def mouseReleaseEvent(self,event):
        w = self.width()
        h = self.height()
        x = event.x()
        y = event.y()
        if x > w-16 and event.button() == Qt.LeftButton: # and left click
            if MpGlobal.Player.CurrentSong != None:
                MpGlobal.Player.CurrentSong[MpMusic.RATING] = self.int_rating
                MpGlobal.Window.tab_library.table.update()
                if Settings.LOG_HISTORY:
                    history_log(MpGlobal.FILEPATH_HISTORY,MpGlobal.Player.CurrentSong,MpMusic.RATING)
                    
        elif event.button() == Qt.RightButton:
            

            if MpGlobal.Player.CurrentSong != None:
                contextMenu = QMenu(MpGlobal.Window)
                contextMenu.addAction("Find Lyrics",self.__Action__GoTo_Lyrics__)
                contextMenu.addAction("Artist Wiki Page",self.__Action__GoTo_Wiki__)
                contextMenu.addAction("Explore Containing Folder",self.__Action__EXPLORE__)
                contextMenu.addAction("Search for Artist",self.__Action_searchARTIST__)
                contextMenu.addAction("Search for Album",self.__Action_searchALBUM__)
                
                contextMenu.exec_( event.globalPos() )
                 
                del contextMenu             
        else: # left region left click
            # reset scrolling
            pass
    def __Action__GoTo_Wiki__(self):
        s = "http://en.wikipedia.org/w/index.php?search="
        s += MpGlobal.Player.CurrentSong[MpMusic.ARTIST].replace(" ","+")
        explorerOpen(s)
    def __Action__GoTo_Lyrics__(self):
        s = "http://www.songmeanings.net/query/?q="
        s += MpGlobal.Player.CurrentSong[MpMusic.ARTIST].replace(" ","+")
        s += "&type=artists"
        explorerOpen(s)
    def __Action__EXPLORE__(self):
        if MpGlobal.Player.CurrentSong != None:
            path = fileGetPath(MpGlobal.Player.CurrentSong[MpMusic.PATH])
            MpGlobal.Window.tab_explorer.load_directory(path)
        MpGlobal.Window.tabMain.setCurrentIndex(MpGlobal.Window.tab_explorer.getCurrentIndex())
    def __Action_searchARTIST__(self):
        if MpGlobal.Player.CurrentSong != None:
            s = ".art \""+MpGlobal.Player.CurrentSong[MpMusic.ARTIST]+"\""
            
            MpGlobal.Window.tab_library.table.updateDisplay(s);
    def __Action_searchALBUM__(self):
        if MpGlobal.Player.CurrentSong != None:
            s = ".art \""+MpGlobal.Player.CurrentSong[MpMusic.ARTIST]+"\""
            s += "; .abm \""+MpGlobal.Player.CurrentSong[MpMusic.ALBUM]+"\""
            
            MpGlobal.Window.tab_library.table.updateDisplay(s);
