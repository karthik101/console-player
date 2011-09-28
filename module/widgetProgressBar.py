from PyQt4.QtCore import *
from PyQt4.QtGui import *

print "getting things done"
class ProgressBar(QProgressBar):
    
    _text = ""
    textHeight = 0
    
    def __init__(self,parent=None):
        super(ProgressBar, self).__init__(parent)
        self.setTextVisible(False)
        
        fm = QFontMetrics(self.font())
        
        self.textHeight = fm.height()
        
    def paintEvent(self,event):
        w = self.width()
        h = self.height()
        
        y = h/2
        y_ = self.textHeight/2
        
        super(ProgressBar, self).paintEvent(event)
        
        painter = QPainter(self)
        painter.drawText(3,y-y_,w,y+y_,0,self._text)
    
    def setText(self,string):
        fm = QFontMetrics(self.font())
        self.textHeight = fm.height()
        
        self._text = unicode(string)
        self.update()
        
    def setValue(self,v):
        super(ProgressBar, self).setValue(v);
        
        
if __name__ == '__main__':

    import sys
    
    app = QApplication(sys.argv)
    timer = QTimer()
    timer.setInterval(250)
    
    def __Timer_Event__():
        v = pbar.value() + 1
        if v > pbar.maximum():
            v = 0
        pbar.setValue( v )

    timer.timeout.connect(__Timer_Event__)
    
    #window = QMainWindow()
    pbar = ProgressBar()
    pbar.setRange(0,100)
    pbar.setValue(0)
    pbar.setText("Display Text")
    pbar.show()
    
    timer.start()
    
    sys.exit(app.exec_())