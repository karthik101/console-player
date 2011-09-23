#!/usr/bin/env python

from PyQt4 import QtCore, QtGui

class InfoDisplay(QtGui.QWidget):
    mousex=0    # last registered mouse position
    
    Timer  = None
    Timer2 = None
    # the formatted text to display
    text_artist = ""
    text_album  = ""
    text_title  = ""
    text_playcount = ""
    text_time   = ""
    text_index  = ""
    text_date = ""
    
    # value to use for the rating bar
    int_rating  = 0
    int_freq = 0
    
    disp_date = False # toggle display of time/date
    
    # text scrolling parameters
    w_art = 0   # text width
    w_abm = 0
    w_ttl = 0
    w_ind = 32  # width of playlist index text
    
    v_art = False   # whether to scroll this line
    v_abm = False
    v_ttl = False
    
    v_posa = 0  # text position ( less than w_--- )
    v_posb = 0
    v_post = 0 
    
    spercent  = 1.0 # precentage before stop scroll
    svelocity = 2 # speed at which text should scroll, pixels per 1/8 second
    tvelocity = 0 # 0,1,2 for art abm or ttl, change speed for each

    brush_barfill = QtGui.QBrush(QtGui.QColor(200,150,0));
    
    def __init__(self):
        super(InfoDisplay, self).__init__(None)

        self.Timer = QtCore.QTimer(self)
        self.Timer.timeout.connect(self.__Timer_Event__)
        self.Timer.setInterval(125)
        self.Timer.setSingleShot(False)
        
        self.Timer2 = QtCore.QTimer(self)
        self.Timer2.timeout.connect(self.__Timer_Event_Restart__)
        self.Timer2.setSingleShot(True)
        
        self.path = QtGui.QPainterPath()
        self.path.addRect(QtCore.QRectF(0,5,10,10))
        
        self.penWidth = 0
        
        self.rotationAngle = 0
        self.setBackgroundRole(QtGui.QPalette.Base)
        
        self.penColor = QtGui.QColor(0, 0, 0)
        
        self.fillColor1 = QtGui.QColor(  127,  127, 150) # play, bright
        self.fillColor2 = QtGui.QColor(   64,   64, 150) # play, dark

        self.fillColorB = QtGui.QColor(  0,  0, 0) # play, dark
        
        self.setMouseTracking(True)

    def minimumSizeHint(self):
        return QtCore.QSize(60, 48)

    def sizeHint(self):
        return QtCore.QSize(200, 48)

    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        rh = h/4.0
        rw = self.w_ind + 16 + 2 # right aligned width
        cw = w - rw
        
        painter = QtGui.QPainter(self)
        fh = painter.fontMetrics().height()
        fl = rh/2.0 + fh/2.0 - 2
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.scale( 1.0, 1.0)

        #painter.setPen(QtGui.QPen(self.penColor, self.penWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

        #painter.drawText(cw,fl+3*rh,self.text_playcount)
        #painter.drawText(cw,fl,w,h,QtCore.Qt.AlignRight,self.text_index) 
        painter.drawText(cw-7,fl-fh+2,rw-7,rh,QtCore.Qt.AlignRight,self.text_index)
        
       
        if self.disp_date == False:
            painter.drawText(0,fl+3*rh,self.text_time)
            painter.drawText(cw-7,fl+3*rh-fh+2,rw-7,rh,QtCore.Qt.AlignRight,self.text_playcount)
        else:
            painter.drawText(0,fl+3*rh,self.text_date)
            painter.drawText(cw-7,fl+3*rh-fh+2,rw-7,rh,QtCore.Qt.AlignRight,u"\u0192%d"%self.int_freq)
        
        painter.setClipping(True)
        
        painter.setClipRegion(QtGui.QRegion(0,0,w-16,h))
        painter.drawText(-self.v_post,fl+rh,self.text_title)
        painter.drawText(-self.v_posb,fl+2*rh,self.text_album)
        
        painter.setClipRegion(QtGui.QRegion(0,0,cw+3,h))
        painter.drawText(-self.v_posa,fl,self.text_artist)
        
        
        #-------------------------------------------------------
        painter.setClipRegion(QtGui.QRegion(w-16,0,16,h))
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(self.brush_barfill)
        
        painter.drawRect(w-13,1,12,h-2)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(100,100,100)))
        vi = 5-self.int_rating
        if vi != 0 :
            painter.drawRect(w-13,1,12,((h-2)/5)*vi) 
            
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
        
        #rh = h/5 - 1
        #painter.drawLine(w-14,rh,  w-2,rh)
        #painter.drawLine(w-14,rh*2,w-2,rh*2)
        #painter.drawLine(w-14,rh*3,w-2,rh*3)
        #painter.drawLine(w-14,rh*4,w-2,rh*4)
        
        
    def mouseMoveEvent(self,event):
        w = self.width()
        h = self.height()
        x = event.x()
        y = event.y()
        
        btn = int(event.buttons())
        
        if x > w-16 and btn == QtCore.Qt.LeftButton:
            self.int_rating = 5 - int(float(y) / (h-2) * 5)
            self.update()
        elif x < w-16:

            pos = max(0,x-8)
            per = pos/float(w-24)
            
            if y <= h/4:
                ypos = 0
            elif y <= h/2:
                ypos = 1
            else:
                ypos = 2
            
            
            self.v_posa = 0
            self.v_post = 0
            self.v_posb = 0
            
            if ypos == 0 and self.v_art:
                self.v_posa = int( self.w_art * per )
            if ypos == 1 and self.v_ttl:
                self.v_post = int( self.w_ttl * per )
            if ypos == 2 and self.v_abm:
                self.v_posb = int( self.w_abm * per )
                
            self.update()
            
    def mousePressEvent(self,event):
        w = self.width()
        h = self.height()
        x = event.x()
        y = event.y()
        
        mse_down = True
        
        if x > w-16:
            self.int_rating = 5 - int(float(y) / (h-2) * 5)
            self.update()
        
    def mouseReleaseEvent(self,event):
        pass
    
    def enterEvent(self,event):
        self.disp_date = True
        self.stopScrolling()
        self.update()
        
    def leaveEvent(self,event):
        self.disp_date = False
        self.v_posa = 0
        self.v_post = 0
        self.v_posb = 0
        
        self.setScrolling()
        
        self.update()
        
    def resizeEvent(self,event):
        w = event.size().width()
        
        self.v_art = (self.w_art >= (w - self.w_ind - 18) )
        self.v_abm = (self.w_abm >= (w - 18))
        self.v_ttl = (self.w_ttl >= (w - 18))
        
        if not (self.v_art or self.v_abm or self.v_ttl):
            self.stopScrolling()
        else:
            self.setScrolling()

    def getMousePosition(self,event):
        pass
        
    def updateInfo(self,a,t,b,pc,rt):
        self.text_artist = a
        self.text_album  = b
        self.text_title  = t
        self.text_playcount = str(pc)
        self.int_rating = rt

        self.update();
        
    def updateIndex(self,str):
        self.text_index  = str       
        self.update();
    
    def updateTime(self,str):
        self.text_time   = str
        self.update();
    
    def setScrolling(self):
        w = self.width()
        
        fm = QtGui.QFontMetrics(self.font())
        
        self.w_art = fm.width(self.text_artist)
        self.w_abm = fm.width(self.text_album)
        self.w_ttl = fm.width(self.text_title)
        self.w_ind = fm.width(self.text_index)
        
        self.v_art = (self.w_art >= (w - self.w_ind - 18) )
        self.v_abm = (self.w_abm >= (w - 18))
        self.v_ttl = (self.w_ttl >= (w - 18))
             
        self.v_posa = 0
        self.v_posb = 0
        self.v_post = 0

        if (self.v_art or self.v_abm or self.v_ttl):
            self.tvelocity = self._first_Scroll_Target_()
            self._DelayScroll_(2000)
        elif self.Timer.isActive() :
            self.Timer.stop()
            self.stopScrolling()
        
    def stopScrolling(self):
        if self.Timer.isActive() :
            self.Timer.stop()
        if self.Timer2.isActive() :
            self.Timer2.stop()
        
        #self.v_art = False
        #self.v_abm = False
        #self.v_ttl = False
        
        self.v_posa = 0
        self.v_posb = 0
        self.v_post = 0
        
        self.tvelocity = -1
        
    def __Timer_Event__(self):
    
        
        if self.tvelocity == 0 :
            self.v_posa += self.svelocity
            if self.v_posa >= self.w_art*self.spercent:
                self.v_posa = 0
                self.tvelocity = self._next_Scroll_Target_()
                self._DelayScroll_(1000)
                
        elif self.tvelocity == 1 :
            self.v_post += self.svelocity
            if self.v_post >= self.w_ttl*self.spercent:
                self.v_post = 0
                self.tvelocity = self._next_Scroll_Target_()
                self._DelayScroll_(1000)
                
        elif self.tvelocity == 2 :
            self.v_posb += self.svelocity
            if self.v_posb >= self.w_abm*self.spercent:
                self.v_posb = 0
                self.tvelocity = self._next_Scroll_Target_()
                self._DelayScroll_(1000)
      
        self.update()
    
    def _DelayScroll_(self,msec):
        # stop the timer, set up a oneshot, delay for length
        # when resume is called normal scrolling will continue
        if self.Timer.isActive() :
            self.Timer.stop()
        
        if not self.Timer2.isActive() :
            self.Timer2.start(msec)
    
    def __Timer_Event_Restart__(self):
        self.Timer.start()
    
    def _next_Scroll_Target_(self):
        if self.tvelocity == 0 and self.v_ttl:
            return 1
        elif self.tvelocity == 0 and self.v_abm:
            return 2
            
        elif self.tvelocity == 1 and self.v_abm:
            return 2
        elif self.tvelocity == 1 and self.v_art:
            return 0
        
        
        elif self.tvelocity == 2 and self.v_art:
            return 0
        elif self.tvelocity == 2 and self.v_ttl:
            return 1    
            
        else: # or no change
            return self.tvelocity
    
    def _first_Scroll_Target_(self):
        if self.v_art :
            return 0
        elif self.v_ttl :
            return 1
        elif self.v_abm :
            return 2
        return 0
    
    def _debug_(self):
        print "--"
        print self.v_art, self.v_posa
        print self.v_abm, self.v_posb
        print self.v_ttl, self.v_post
    
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    
    window = InfoDisplay()
    window.show()
    
    window.text_artist = "Luke James and the firewaterband"
    window.text_album  = ""
    window.text_title  = ""
    window.text_playcount = "41"
    window.text_time   = "1:45/5:45 -4:00"
    window.text_index  = "117/150"
    window.int_rating  = 4

    window.setScrolling()
    
    print window.w_art
    print window.w_abm
    print window.w_ttl
    print window.w_ind
    sys.exit(app.exec_())
