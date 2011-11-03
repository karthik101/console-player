import sys
import os

isPosix = os.name == 'posix'

import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *
from MpSong import Song
from datatype_hex64 import *


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
            t = MpGlobal.Player.CurrentSong[MpMusic.LENGTH]
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
