#!/usr/bin/env python

from PyQt4 import QtCore, QtGui

class PlayButton(QtGui.QWidget):
    state_btn1 = True      # play / pause
    state_btn2 = False      # stop playback / continue playback on song end
    state_hvr1 = True   # mouse over
    state_hvr2 = False  # mouse over
    state_mouseDown = False # mouse held down
    location = 0 # which button the mouse is over
    def __init__(self):
        super(PlayButton, self).__init__(None)

        self.path = QtGui.QPainterPath()
        self.path.addEllipse(QtCore.QRectF(5,5,90,90))
        
        self.cont_size = 40;         # size of inner circle
        l = 95 - self.cont_size      # place the inner circle on the right edge
        t = 50 - self.cont_size/2    # to make a cresent moon
        self.path2 = QtGui.QPainterPath()
        
        self.path2.addEllipse(QtCore.QRectF(l,t,self.cont_size,self.cont_size))

        points = [QtCore.QPointF(0,0),QtCore.QPointF(0,100),QtCore.QPointF(100,50)]
        poly = QtGui.QPolygonF(points)
        
        self.path_play = QtGui.QPainterPath()
        self.path_play.addPolygon(poly)
        self.path_play.closeSubpath()
        self.path_play.translate(-50,-50)
        
        self.path_pause = QtGui.QPainterPath()
        self.path_pause.addRoundRect(0,0,33,100,3)
        self.path_pause.addRoundRect(66,0,33,100,3)
        self.path_pause.translate(-50,-50)
        
        points = [QtCore.QPointF(0,0),QtCore.QPointF(0,100),QtCore.QPointF(66,50)]
        poly = QtGui.QPolygonF(points)
        
        self.path_cont = QtGui.QPainterPath()
        self.path_cont.addPolygon(poly)
        self.path_cont.closeSubpath()
        self.path_cont.addRoundRect(66,0,33,100,3)
        self.path_cont.translate(-50,-50)
        
        self.penWidth = 2
        
        self.rotationAngle = 0
        self.setBackgroundRole(QtGui.QPalette.Base)
        
        self.penColor = QtGui.QColor(0, 0, 0)
        self.fillColor1 = QtGui.QColor(  76,  99, 200) # play, bright
        self.fillColor2 = QtGui.QColor(  24,  58, 125) # play, dark
        self.fillColor4 = QtGui.QColor( 225,  31,   0) # cont, bright
        self.fillColor3 = QtGui.QColor( 121,   2,   0) # cont, dark
        
        self.fillColor5 = QtGui.QColor(  24,  30, 100) # play, darker
        self.fillColor6 = QtGui.QColor(  64,   2,   0) # cont, darker
        self.fillColorlg = QtGui.QColor(112, 112, 112) # light gray
        self.fillColordg = QtGui.QColor(64, 64, 64) # dark gray
        self.fillColordg2 = QtGui.QColor(32, 32, 32) # darker gray
        self.rotationAngle = 0
        
        self.setMouseTracking(True)

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(100, 100)

    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        side = min(w,h)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.scale( side / 100.0, side / 100.0)

        painter.setPen(QtGui.QPen(self.penColor, self.penWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # draw the play button:
        f = (90 - self.cont_size) / 2
        gradient = QtGui.QRadialGradient(50, 50, 75, f, 50)

        c1 = self.fillColor1
        c2 = self.fillColor2
        c3 = self.fillColor5
            
        if self.state_hvr1 :
            if self.state_mouseDown :
                gradient.setColorAt(0.0, c2)
                gradient.setColorAt(.80, c3)
            else:
                gradient.setColorAt(0.0, c1)
                gradient.setColorAt(.80, c2)
        else:
            gradient.setColorAt(0.0, c2)
            gradient.setColorAt(.80, c1)
            
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawPath(self.path)
        
        # draw the continue button:
        self.cont_size = 40;         # size of inner circle
        c = 95 - self.cont_size/2      # place the inner circle on the right edge
        r = self.cont_size/2    # to make a cresent moon
        gradient = QtGui.QRadialGradient(c, 50, r, c, 50)

        if self.state_btn2 :
            c1 = self.fillColor3
            c2 = self.fillColor4
            c3 = self.fillColor6
        else:
            c1 = self.fillColorlg
            c2 = self.fillColordg
            c3 = self.fillColordg2
        
        
        if self.state_hvr2 :  
            if self.state_mouseDown :
                gradient.setColorAt(0.0, c2)
                gradient.setColorAt(.80, c3)
            else:
                gradient.setColorAt(0.0, c2)
                gradient.setColorAt(.80, c1)
        else:
            gradient.setColorAt(0.0, c1)
            gradient.setColorAt(.70, c2)
        
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawPath(self.path2)

        # draw the play / pause icon
        # we need to center it in w, the lengeth from the left
        # edge of the play button, to the start of the cont button
        # we want some padding, say 10 or so pixels on each side
        painter.setBrush(QtGui.QBrush(self.penColor))
        
        s = 90 - self.cont_size/2
        scale = ((s / 100.0) * (side/100.0)) / 2.5
        l = (((s/2)) / 100.0) * side
        painter.resetTransform()
        painter.translate(l, side/2)
        painter.scale( scale , scale ) # scale after translation
        if self.state_btn1 :
            painter.drawPath(self.path_play)
        else:
            painter.drawPath(self.path_pause)
        
        # draw the cont icon
        s = self.cont_size
        # scale the length down to units per cent, and scale the 
        # width of the widget down to units per cent, and then half scale
        scale = ((s/ 100.0) * (side/100.0)) / 2
        l = (((s)/2.0 + 5) / 100.0)
        l = side - l*side
        painter.resetTransform()
        painter.translate(l, side/2)
        painter.scale( scale, scale) # scale after translation

        painter.drawPath(self.path_cont)
     
    #def enterEvent(self,event):
    #    self.stat_mouseDown = False;
    #    self.update()
        
    def leaveEvent(self,event):
        self.state_hvr1 = False
        self.state_hvr2 = False
        self.stat_mouseDown = False;
        self.update()
        
    def mouseMoveEvent(self,event):
        local = self.getLocation(event)
        if (self.location != local):
            self.location = local
            if self.location == 0 :
                self.state_hvr1 = True
                self.state_hvr2 = False
            else:
                self.state_hvr1 = False
                self.state_hvr2 = True
            self.update()
    
    def mousePressEvent(self,event):
        self.state_mouseDown = True
        self.update()
        
    def mouseReleaseEvent(self,event):
        self.state_mouseDown = False
        self.clickEvent()
        self.update()
        
    def getLocation(self,event):
        w = self.width()
        h = self.height()
        side = float(min(w,h))
        x = event.x()
        y = event.y()
        
        # bounding box, start x,y, and dimension d as a percentage length
        bx=(95-self.cont_size)/100.0
        by=(50-(self.cont_size/2))/100.0
        bd=(self.cont_size)/100.0
        
        localx = x/side
        localy = y/side

        if  localx > bx and localy > by and \
            localx < bx+bd and localy < by+bd :
            return 1
        
        return 0 # mouse is not inside middle button

    def clickEvent(self):
        if self.location == 0 :
            self.state_btn1 = not self.state_btn1
        else:
            self.state_btn2 = not self.state_btn2

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    
    window = PlayButton()
    window.show()
    sys.exit(app.exec_())
