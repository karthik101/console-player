

import sys
import os

isPosix = os.name == 'posix'

import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import widgetPlayButton

from MpGlobalDefines import *


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