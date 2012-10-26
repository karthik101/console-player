#! python $this

from PyQt4.QtCore import *
from PyQt4.QtGui import  *

import math,cmath

import zbdesign
import linalg
# proof
# in the time domain:
# x*h1 + x*h2 + x*h3 = y
# x*(h1 + h2 + h3)
# in the freq domain
# X(H1 + H2 + H2)

octave_ranges = [
        [   32,   64],
        [   64,  128],
        [  128,  256],
        [  256,  512],
        [  512, 1024],
        [ 1024, 2048],
        [ 2048, 4096],
        [ 4096, 8192],
    ]
  
def frange(s,e,step):
    # range doesnt take floats, this is all i need.
    i = s;
    while i < e:
        yield i
        i += step;
 
"""
    convert frequency to a bin index or the reverse of.
    size was chosen to divide evenly with 8
    i evenly plot the range from 2^5 to 2^13, and 13-5 = 8
""" 
def f2i(f,size=256):
    return int(size/8.0*(math.log(f,2)-5))
def i2f(i,size=256):
    return 2**( 5 + i*8.0/size) 
    
def mag(b,a,fc,fs=16000):
    # return the magnitude of coefficients b,a at frequency fc in db.
    # TODO it would be interesting to find a way that
    # i could write this in C. only thing stoping me is
    # I need to know the runtime on cost of exp
    z = cmath.exp(-complex(0,1)*2.0*math.pi*fc/fs)
    c=1.0;
    n=d=0.0;
    for i,j in zip(b,a):
        n += i*c; 
        d += j*c; 
        c = c*z;
    if d == 0.0: return 0.0;
    return 20.0*math.log( abs(n/d), 10 )
    
def system_coeff(fs,fc,bw,fc_list):
    # scaling by 3.0 then dividing by 3.0 gives
    # a better output than using 1.0, but it's not significant
    # when the range is -6 to 6, the average is ~3 *waves hands* over logic
    p = zbdesign.zbpeak_param(fs,fc,bw,3.0)
    return  [ mag(p.b_num,p.a_den,f,fs)/3.0 for f in fc_list ]
    
def system_solve(fs,fc_list,bw_list,gdb_list,max_gdb=6):
    # return the gain coefficients that will better represent the
    # system that the user input
    # build a row matrix with coeffcients for a representative
    F = [ system_coeff(fs,f,bw,fc_list) for f,bw in zip(fc_list,bw_list) ]
    
    G0 = linalg.solve(F,gdb_list)

    G0 = [ min(max_gdb,max(-max_gdb,g)) for g in G0 ]
    
    return G0
 
def system_parameters():    
    """
    returns a pair of center frequencies and bandwidth
    each roughly covering a musical octave.
    """    
    # roughly matches the octaves
    fc_list = []
    bw_list = []
    for s,e in octave_ranges:
        w = e-s;
        fa = s + (1.0/2)*w
        fc_list.append(fa)
        bw_list += [w,]
    return fc_list,bw_list
 
def system_build(gdb_list,size=256,max_gdb=6):
    """
        return a set of bins that can be plotted.
    """
    fs = 44100.0
    fc_list,bw_list = system_parameters()
    #print fc_list
    #print bw_list
    g0_list = system_solve(44100,fc_list,bw_list,gdb_list,max_gdb)
    
    
    
    print g0_list
    bins = [0]*size
    
    for fc,bw,gdb in zip(fc_list,bw_list,g0_list):
    #for fc,bw,gdb in ( (fc_list[3],bw_list[3],g0_list[3]), ):
        ag = abs(gdb);
        # 3/ag cuts the bw by .5 at a |gdb|=6, .25 at |gdb|=12, and .125 at |gdb|=24.
        # approximatley, the zbpeak filter
        #bw = bw if ag < 3 else bw*(2.0/ag);
        for i in range(size):
            p = zbdesign.zbpeak_param(fs,fc,bw,gdb)
            # this regression provides a value f
            # distributed evenly on a logarithmic scale
            # across all of the octaves
            bins[i] += mag(p.b_num,p.a_den,i2f(i),fs)
    return (bins,g0_list)
    
class WidgetOctaveEquilizer(QWidget):
    
    gain_updated = pyqtSignal(list)
    
    def __init__(self,parent=None):
        super(WidgetOctaveEquilizer, self).__init__(parent)
        
        self.max_value = 20 # scale value to this
        self.max_gdb = 18
        fcl,_ = system_parameters()
        
        self.gain = [0,0,0,0,0,0,0,0]
        self.bins,_ = system_build(self.gain,max_gdb=self.max_gdb)

        self.ctrl_index = [ f2i(f) for f in fcl] 
        print fcl
        print self.ctrl_index
        
        #self.color_log_line = QColor(212,212,212);
        #self.color_bg_line = QColor(192,192,192);
        #self.color_gain_line = QColor(0,0,0);
        
        self.color_log_line = QColor(44,44,44);
        self.color_bg_line = QColor(64,64,88);
        self.color_zero_line = QColor(64,64,88);
        self.color_gain_line = QColor(12,192,64);
    def setColors(self):
        app_palette =QApplication.instance().palette()
        
        bg = app_palette.background().color()
        #print bg.red(),bg.green(),bg.blue();
        bgr,bgg,bgb = bg.red(),bg.green(),bg.blue();
        factor = .33
        r = int( min(255,bgr*(1.0+factor)) if bgr < 127 else bgr*(1.0-factor) )
        g = int( min(255,bgg*(1.0+factor)) if bgg < 127 else bgg*(1.0-factor) )
        b = int( min(255,bgb*(1.0+factor)) if bgb < 127 else bgb*(1.0-factor) )
        self.color_bg_line = QColor(r,g,b);
        
        factor = .15
        r = int( min(255,bgr*(1.0+factor)) if bgr < 127 else bgr*(1.0-factor) )
        g = int( min(255,bgg*(1.0+factor)) if bgg < 127 else bgg*(1.0-factor) )
        b = int( min(255,bgb*(1.0+factor)) if bgb < 127 else bgb*(1.0-factor) )
        self.color_log_line = QColor(r,g,b);
        
        factor = .75
        r = int( min(255,bgr*(1.0+factor)) if bgr < 127 else bgr*(1.0-factor) )
        g = int( min(255,bgg*(1.0+factor)) if bgg < 127 else bgg*(1.0-factor) )
        b = int( min(255,bgb*(1.0+factor)) if bgb < 127 else bgb*(1.0-factor) )
        self.color_zero_line = QColor(r,g,b);
        
        r =  25 if bgr < 127 else  32
        g = 255 if bgg < 127 else   0
        b =  32 if bgb < 127 else 255
        self.color_gain_line = QColor(r,g,b);
        
    def paintEvent(self, event= None):
        w = self.width()
        h = self.height()
        m = h/2
        p = QPainter(self)
        
        yscale = (.5*h*.9)/self.max_value
        size = float(len(self.bins))
        
        self.setColors()
        
        ####################################################################    
        # draw the log scale in the background
        p.setPen(self.color_log_line)  
        for f in range(10,100,10) + range(100,1100,100) + range(2000,10000,1000):
            x = f2i(f)*w/size
            p.drawLine(x,0,x,h)
            
        ####################################################################        
        # draw the gain axis: lines are 3db apart
        p.setPen(self.color_bg_line)
        for y in range(5,int(math.ceil(self.max_gdb/5.0)*5+1),5):
            p.drawLine(0,m-y*yscale,w,m-y*yscale)
            p.drawLine(0,m+y*yscale,w,m+y*yscale)
          
        ####################################################################    
        # draw slider guidelines for each filter
        step_size = 1
        for i in self.ctrl_index:
            x = i*w/size
            p.drawRoundedRect(x-5,m-self.max_gdb*yscale+1,10,(2*self.max_gdb*yscale-2),5,5)
            k=-self.max_gdb + step_size;
            while k < self.max_gdb:
                p.drawLine(x-5,m-k*yscale,x+5,m-k*yscale)
                k += step_size
                
        ####################################################################    
        # draw the zero line
        p.setPen(self.color_zero_line)
        p.drawLine(0,m,w,m)  
        ####################################################################        
        # paint the graph, starting with the second point
        # draw a line from that point to the previous point
        # scale all of the bins across the width of the object
        # this will produce a continuous line
        pen = QPen(self.color_gain_line)
        pen.setWidth(2)
        p.setPen(pen)
        i=1;
        p.setRenderHint(QPainter.Antialiasing)
        while i < size:
            a = (i-1)*w/size # scales bin index across x axis of widget
            b = yscale*self.bins[i-1] #bins hold gain values
            c = (i)*w/size
            d = yscale*self.bins[i]
            p.drawLine(a,m-b,c,m-d)
            i += 1
            
        ####################################################################    
        # draw the handles for the current user selection
        # not that the line may not pass through the handles.
        pen = QPen(QColor(0,0,0))   
        pen.setWidth(2)
        p.setPen(pen)
        
        grad =  QLinearGradient()
        grad.setSpread(QGradient.ReflectSpread 	)
        grad.setStops(
                    [(0.0,QColor(72,72,72)),
                     (0.5,QColor(192,192,192)),
                     (1.0,QColor(72,72,72))]
                     );
        brush = QBrush(grad)
        
        p.setBrush(brush)
        for i,j in enumerate(self.ctrl_index):    
            a=(j)*w/size-6
            b=m-yscale*self.gain[i]-4
            p.drawRoundedRect(a,b,12,8,3,3)
        
        
        # draw text if w > 12*4*8, wid per char, num char, num words
        return
    def mouseReleaseEvent(self,event=None):
        x = event.x()
        y = event.y()
        t = len(self.bins)*x/self.width()
        # get the index of which grip was selected
        # x = i*width/size
        i=-1;
        for ci in self.ctrl_index:
            if ci-5 < t < ci+5:
                i = self.ctrl_index.index(ci)
        # get the magnitude of that grip
        # y = m - g*s
        m = self.height()/2
        s = (.5*self.height()*.9)/self.max_value
        g=(m-y)/s;
        g = .5*(round((g)/.5)) # step size
        g = min(self.max_gdb,max(-self.max_gdb,g))
        if i != -1:
            print i,g
            self.gain[i] = g
            self.bins,gdb_list = system_build(self.gain,max_gdb=self.max_gdb)
            self.gain_updated.emit(gdb_list)
            self.update()
               
if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    
    window = WidgetOctaveEquilizer()
    window.show()
    sys.exit(app.exec_())