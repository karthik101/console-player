#! python $this
import os,sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Leaf import Leaf
from widgetLargeTable import *


class LargeTree(LargeTable):
    
    def __init__(self,parent=None):
        super(LargeTree,self).__init__(parent)
        self.columns = [ TreeColumn(self,Leaf.column_token,""), ] + self.columns
        self.columns[0].setWidthByCharCount(48)
        
        self.setSelectionRule(LargeTree.SELECT_ONE)
        print self.selection_rule
        
        self.setRowHeight(19)
        self.showRowHeader(False)
        
        
        
    def initColumns(self):
        pass # this disables the creation of a column by LargeTable
    
    def setRoot(self,root):
        self.root = root
        
        self.data = root.toList()
      
class TreeColumn(TableColumn):

    def __init__(self,parent,index,name=None):
        super(TreeColumn,self).__init__(parent,index,name)
        self.text_transform = lambda row_item,cell_item : unicode(row_item.text)
        self.bool_display_root = True
        self.paint_control_width = 14; # width of drawing area for tree controls
        #self.text_transform = lambda r,i : "%04X : %d : %d : %s"%(r.fold,r.tempid,len(r.children),i)
    def paintItem(self,col,painter,row,item,x,y,w,h):
        # get how much space the text should be offset by
        row_item = self.parent.data[row]

        
        #for i in range(0,row_item.depth):
        #    offset = ((i - (not self.bool_display_root) ) * self.paint_control_width)/2
        #    xmid = x +  self.paint_control_width/2 +(offset)
        #    painter.drawLine(xmid,y+1,xmid,y+h-1)
            
        offset = ((row_item.depth - (not self.bool_display_root) ) * self.paint_control_width)/2
        xmid = x +  self.paint_control_width/2 +(offset)
        ymid = y+(h/2)
        wxh = self.parent.row_height-3
        ################################################
        # draw the icon
        if row_item.icon != None:
            x_ = x+offset+self.paint_control_width
            painter.drawPixmap(x_+2,y+2,wxh,wxh,row_item.icon)
        ################################################
        # draw text
        self.paintItem_text(col,painter,row,item,x+wxh+offset+self.paint_control_width+4,y,w,h)
        # rect is ...
        # x+self.parent.row_height+(((row_item.depth - (not self.bool_display_root) ) * self.paint_control_width)/2)self.paint_control_width+1
        
        default_pen = painter.pen()  
        linecolor = QColor(164,164,164)
        
        ################################################
        # draw the visual aid
        if row_item.fold&(1<<Leaf.fold_HAS_CHILDREN) or row_item.folder_empty:
            # draw box
            painter.drawRect(xmid-4,ymid-4,8,8)
            # draw --
            if not row_item.folder_empty:
                # draw a minus when not empty
                painter.drawLine(xmid-2,ymid,xmid+2,ymid)
            if row_item.fold&(1<<Leaf.fold_COLLAPSED):
                # turn the minus into a plus
                painter.drawLine(xmid,ymid-2,xmid,ymid+2)
            elif not row_item.folder_empty:
                painter.setPen(linecolor) 
                # draw 'has children and expanded' '7'
                painter.drawLine(xmid+5,ymid,xmid+9,ymid)
                painter.drawLine(xmid+7,ymid,xmid+7,y+h-1)
            # draw 'has sibling above', req'd
            painter.setPen(linecolor) 
            if row_item.parent != None:
                painter.drawLine(xmid,y+1,xmid,ymid-5)
            # draw 'has sibling below'
            if row_item.fold&(1<<Leaf.fold_SIBLINGB):
                painter.drawLine(xmid,ymid+5,xmid,y+h-1)
        else:
            painter.setPen(linecolor) 
            #  draw 'is'
            painter.drawLine(xmid,ymid,xmid+2,ymid)
            # draw 'has sibling above'
            painter.drawLine(xmid,y+1,xmid,ymid)
            if row_item.fold&(1<<Leaf.fold_SIBLINGB):
                painter.drawLine(xmid,ymid,xmid,y+h-1)

        ################################################
        # draw continuation decender for higher leaves
        i = row_item.depth-1
        p = row_item.parent
        while p != None:
            
            if p.fold&(1<<Leaf.fold_SIBLINGB):
                offset = ((i - (not self.bool_display_root) ) * self.paint_control_width)/2
                xmid = x +  self.paint_control_width/2 +(offset)
                painter.drawLine(xmid,y+1,xmid,y+h-1)
            p = p.parent
            i -= 1;
        painter.setPen(default_pen)  
        
            
    def mouseHover(self,row_index,posx,posy): 
        #print posx,posy
        if row_index  < len(self.parent.data):
            row_item = self.parent.data[row_index]
            depth = row_item.depth
        #print depth,posx,posy
        return False
        
        
    def mouseClick(self,row_index,posx,posy):
        if row_index  < len(self.parent.data):
            row_item = self.parent.data[row_index]
            if row_item == None: return False;
            depth = row_item.depth
            offset = ((depth - (not self.bool_display_root) ) * self.paint_control_width)/2   
            xmid = self.paint_control_width/2 +(offset)
            if xmid - 4 < posx < xmid + 4:
                if len(row_item.children) > 0:
                    row_item.collapsed = not row_item.collapsed
                    self.parent.setData( self.parent.root.toList() )
                return True
        return False
if __name__ == '__main__':    
    
    app = QApplication(sys.argv)

    table = LargeTree()
    items = [ ("art","abm1","ttl1"), ("art","abm1","ttl2"), ("art","abm2","ttl3"), ("art2","abm3","ttl4") ]     
    
    from Song_Object import *
    import Song_LibraryFormat
    song_list = Song_LibraryFormat.musicLoad_LIBZ(r"D:\Dropbox\ConsolePlayer\user\music.libz")
    
    leaf = Leaf.items_to_tree([EnumSong.ARTIST,EnumSong.ALBUM],lambda x : x[EnumSong.TITLE], song_list)
    p = leaf
    for i in range(10):
        p=Leaf(p,"-%d"%i,[])
    table.setRoot(leaf)
    table.container.resize(640,320)
    table.container.show()
    
    sys.exit(app.exec_())