#! python $this
from widgetLargeTable import *
from Song_Object import *
from SystemDateTime import DateTime

from TableEditColumn import *

class SongTable(LargeTable):
    """
        This is the default implementation for representing Songs in a Table Layout
        
        This is an extention to the LargeTable class, where each row of the table is a Song.
        And a Song has been implemented as a special type of List, this yeilds
        that the data for the table is still a 2d array of strings or integers
        
        This class initilizes a new LargeTable with all of the required
        columns to display information about a Song.
        
        It includes a way to highlight the DateStamp, but is turned off by default
        
        It also includes a way to edit the rating of a song by clicking within the row
        column, this can be turned off
    """
    color_text_played_recent = QColor(200,0,200)
    color_text_played_not_recent = QColor(200,0,0)
    color_text_banish = QColor(128,128,128)
    

    date_mark_1 = 0 # time corresponding to the start of the day
    date_mark_2 = 0 # time corresponding to 14 days ago or so.

    rating_mouse_tracking = True;
    
    modify_song = pyqtSignal(Song)      # emitted whenever the table updates a row value
                                        # since each row is a reference to a Song
                                        # this is a modification of Song Data
                                        
    def __init__(self,parent=None):
    
        super(SongTable,self).__init__(parent)
        
        # enable highlighting of the current song
        self.rule_selected = lambda row: self.data[row][EnumSong.SELECTED]  
        self.rule_banish = lambda row: self.data[row].banish
        
        # highlight songs that are selected
        self.addRowHighlightComplexRule(self.rule_selected,self.color_text_played_recent)

        # change text color for banished songs
        self.addRowTextColorComplexRule(self.rule_banish,self.color_text_banish)
   
    def setRuleColors(self,rc_recent,rc_not_recent,rc_banish,rc_selected):
        self.color_text_played_recent     = rc_recent
        self.color_text_played_not_recent = rc_not_recent
        self.color_text_banish            = rc_banish
        
        for i in range(len( self.getRowHighlightComplexRule() ) ):
            if self.getRowHighlightComplexRule()[i][0] == self.rule_selected:
                self.setRowHighlightComplexRule(i,None,rc_selected)
                
        for i in range(len( self.getRowTextColorComplexRule() ) ): 
            if self.getRowTextColorComplexRule()[i][0] == self.rule_banish:
                self.setRowTextColorComplexRule(i,None,self.color_text_banish)
        
    def initColumns(self):
        self.columns.append( TableColumn(self,EnumSong.PLAYCOUNT,"Play Count") )
        self.columns[-1].setShortName("#")
        self.columns[-1].setWidthByCharCount(3)
        self.columns[-1].setMinWidthByCharCount(2)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns.append( EditColumn(self,EnumSong.ARTIST   ,"Artist") )
        self.columns[-1].setWidthByCharCount(30)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( EditColumn(self,EnumSong.TITLE    ,"Title") )
        self.columns[-1].setWidthByCharCount(30)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( EditColumn(self,EnumSong.ALBUM    ,"Album") )
        self.columns[-1].setWidthByCharCount(20)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( TableColumn(self,EnumSong.LENGTH   ,"Length") )
        self.columns[-1].setWidthByCharCount(7)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].text_transform = lambda row_data,cell_item: DateTime.formatTimeDelta(cell_item);
        self.columns.append( TableColumn_Rating(self,EnumSong.RATING   ,"Rating") )
        self.columns[-1].setWidthByCharCount(10)
        self.columns[-1].setMinWidthByCharCount(7)
        self.columns[-1].setTextAlign(Qt.AlignCenter)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns.append( EditColumn(self,EnumSong.GENRE    ,"Genre") )
        self.columns[-1].setWidthByCharCount(15)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( TableColumn(self,EnumSong.FREQUENCY,"Frequency") )
        self.columns[-1].setShortName("Freq")
        self.columns[-1].setWidthByCharCount(4)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns.append( TableColumn_DateStamp(self,EnumSong.DATESTAMP,"Last Played") )
        self.columns[-1].setWidthByCharCount(16)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns.append( TableColumn(self,EnumSong.FILESIZE ,"File Size") )
        self.columns[-1].setWidthByCharCount(9)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns.append( TableColumn(self,EnumSong.SKIPCOUNT,"Skip Count") )
        self.columns[-1].setWidthByCharCount(10)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns[-1].setTextAlign(Qt.AlignCenter)
        self.columns.append( EditColumn(self,EnumSong.COMMENT  ,"Comment") )
        self.columns[-1].setWidthByCharCount(20)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( TableColumn(self,EnumSong.DATEADDED,"Date Added") )
        self.columns[-1].text_transform = lambda song,index: song[EnumSong.DATEADDEDS]
        self.columns[-1].setWidthByCharCount(16)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns.append( TableColumn(self,EnumSong.YEAR     ,"Year") )
        self.columns[-1].setWidthByCharCount(4)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns.append( TableColumn(self,EnumSong.SONGINDEX,"Album Index") )
        self.columns[-1].setWidthByCharCount(11)
        self.columns.append( TableColumn(self,EnumSong.SONGID   ,"ID#") )
        self.columns[-1].text_transform = lambda song,index: unicode(song.id)
        self.columns[-1].setWidthByCharCount(22)
        self.columns.append( EditColumn(self,EnumSong.PATH     ,"Path") )
        self.columns[-1].setWidthByCharCount(30)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( TableColumn(self,EnumSong.EQUILIZER,"Volume Eq") )
        self.columns[-1].setShortName("Eq")
        self.columns[-1].setWidthByCharCount(10)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns.append( TableColumn(self,EnumSong.SPECIAL,"Special") )
        self.columns[-1].setWidthByCharCount(7)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns.append( TableColumn_Score(self,EnumSong.SCORE,"Score") )
        self.columns[-1].setWidthByCharCount(7)
        self.columns[-1].setTextAlign(Qt.AlignRight)
        self.columns[-1].setDefaultSortReversed(True)
        self.columns.append( EditColumn(self,EnumSong.LANG    ,"Language") )
        self.columns[-1].setShortName("LANG")
        self.columns[-1].setWidthByCharCount(15)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( EditColumn(self,EnumSong.COMPOSER    ,"Composer") )
        self.columns[-1].setWidthByCharCount(15)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        self.columns.append( EditColumn(self,EnumSong.SOURCELIB,"Source Library") )
        self.columns[-1].setShortName("Src")
        self.columns[-1].setWidthByCharCount(15)
        self.columns[-1].cell_modified.connect(self.text_cell_modified)
        
        self.columns_setDefaultOrder( self.columns_getOrder() )
        
    def getColumn(self,song_enum,check_hidden=False):
        """
            return the associated column for a song enum, EnumSong.Artist. EnumSong.Title, etc
            
            when check_hidden is false:
                returns None when the table is not currently displayed
            otherwise returns the column
        """
        for col in self.columns:
            if col.index == song_enum:
                return col
        if check_hidden:
             for col in self.columns_hidden:
                if col.index == song_enum:
                    return col   
        return None
        
    def sortColumn(self,col_index):
        """
            TODO: move MpSort to Song_Sort and
            sortLibrary to MpScripting
            
        """
        index=  self.columns[col_index].index
        
        rev = self.setSortColumn(col_index) == -1
        
        g = lambda x : x[index]
        if index < EnumSong.NUMTERM:
            self.data.sort(key = g, reverse=rev)
        
        self.update()
     
    def text_cell_modified(self,rows,text):
        #print rows,text
        for row in rows:
            self.modify_song.emit(self.data[row])
     
class TableColumn_Rating(TableColumn): 
    """
        A custom table column for displaying the current rating
        as a collection of stars also handles editing rating
        by clicking with the cell.
    """
    suggested_rating = -1
    suggested_rating_row = -1
    
    def __init__(self,parent,index,name=""):
        super(TableColumn_Rating,self).__init__(parent,index,name)


        #qc1 = QColor(200,0,0)
        #self.star_brush = QBrush(qc1)
        
    def paintItem(self,col,painter,row,item,x,y,w,h):
    
        #if isinstance(item,int):
        #    if self.suggested_rating_row == row:
        #        item = self.suggested_rating
        #    _w = item/5.0 * w
        #    painter.fillRect(x,y,_w,h,self.parent.color_rating);
        #Qt.WindingFill
        if row == self.suggested_rating_row:
            item = self.suggested_rating
            
        _c = 2          # top/bottom padding constant
        _h = h-(2*_c)   # height is height minus padding
        _w = _h         # 5 point star is fit inside a square
        _step = (w-5*_w)/5 # a step is the distance between each star
        _hstep = _step/2   # half step
        if _step < 0:
            if item == 0:
                self.paintItem_text(col,painter,row,item,x,y,w,h)
            else:
                self.paintItem_text(col,painter,row,item/2.0,x,y,w,h)
            
            return
        
        #pf = u"\u2605" # full BLACK STAR
        #ph = u"\u2606" # half WHITE STAR
        #pe = u"\u2022" # empty BLACK DOT 
        #text = pf*(item/2) + (ph if item%2==1 else '') + pe*((10-item)/2)   
        #self.paintItem_text(col,painter,row,text,x,y,w,h)
        #return
          
        if item < 1:
            return
          
        ps = QPointF( 0   , .35*_h   ) # start point
        
        #    order of points ( 1 is start/finish)
        #           3
        #        12   45
        #          086
        #         9   7
        #painter.setRenderHint( QPainter.Antialiasing )
        star_shape = QPolygonF( 
            [
            ps, \
            QPointF(  .4 *_w , .35*_h   ), \
            QPointF(  .5 *_w ,    0     ), \
            QPointF(  .6 *_w , .35*_h   ), \
            QPointF(      _w , .35*_h   ), \
                                  
            QPointF(  .65*_w , .55*_h   ), \
            QPointF(  .8 *_w ,     _h   ), \
            QPointF(  .5 *_w , .7 *_h   ), \
            QPointF(  .2 *_w ,     _h   ), \
            QPointF(  .35*_w , .55*_h   ), \

            ps, \
            ]
        )
        #star_shape.toPolygon()

        #star_shape.translate(x+5,y+4)
        #print star_shape.isClosed()
        path = QPainterPath()
        path.addPolygon(star_shape)
        
        #path.closeSubpath()
        path.translate(x+_hstep,y+2)
        
        # _hstep then:
        #   _w+_step
        # _c2 = starting offset + # full stars + half star if needed
        _cw = _hstep + (_w+_step)*(item/2) + (_w/2)*(item%2) + 1
        if x < self.parent.data_cell_clip_x:
            _cw = x + _cw - self.parent.data_cell_clip_x 
            x = self.parent.data_cell_clip_x
        painter.setClipRect(x,y,_cw,h)
                
        for i in range((item+1) / 2):
            #painter.drawPolygon(star_shape,Qt.WindingFill)
            painter.fillPath(path,painter.pen().color())
            path.translate(_w+_step,0)
        #painter.setRenderHint(0) # QPainter.Antialiasing    
            
    def mouseClick(self,row_index,posx,posy):
        if not self.parent.rating_mouse_tracking:
            return False
        self.parent.data[row_index][EnumSong.RATING] = self.suggested_rating
        self.parent.modify_song.emit(self.parent.data[row_index])
        return True#blocking return
        
    def mouseHover(self,row_index,posx,posy):
        if not self.parent.rating_mouse_tracking:
            return False
            
        _c = 2       
        _w = self.parent.row_height-(2*_c)
        _step = ((self.width-4)-5*_w)/5 
        _hstep = max(_step/2,4) # determines padding for getting zero value
        # the calculation for _cw cannot be reversed 
        # therefore a forloop is used to guess and check the value
        value = 0
        for i in range(1,11): # test 1-10
            _cw = _hstep + (_w+_step)*((i-1)/2) + (_w/2)*((i-1)%2) 
            if posx > _cw:
                value = i
            else:
                break
        self.suggested_rating = value           # 
        self.suggested_rating_row = row_index   # used in drawing
        return True # blocking return
        
    def mouseHoverExit(self,event):            
        self.suggested_rating = -1
        self.suggested_rating_row = -1
    
class TableColumn_DateBase(TableColumn): 
    """
        Base class for displaying date information.
        
        the format for input/output of a date can be set
        
        the 'input' date is the cell item from the index
        of the parent tables' data.
        
        the 'output' can use any of the symbols found in input
        in a different order.
        
        the allowed symbols are:
            %Y - year   %H - hour
            %m - month  %M - minute 
            %d - day   
            %y - 2 digit year
            if %Y is defined, then %y will be autofilled
        
    """
    
    def __init__(self,parent,index,name=""):
        super(TableColumn_DateBase,self).__init__(parent,index,name)
        
        self.datefmt_in  = ""
        self.datefmt_out = ""
        
        self.text_transform = self.format
        
        self.setDateInputFormat("%Y/%m/%d %H:%M")
        #self.setDateOutputFormat("%m/%d/%y %H:%M")
        
    def setDateInputFormat(self,fmt):
        """ expected string input format for the date/time display of this cell"""
        self.datefmt_in = fmt
        
    def setDateOutputFormat(self,fmt):
        """ if set, input date/time data will be transformed by output defined here
            set the output format to an empty string to disable date transforms.
        """
        self.datefmt_out = fmt
     
    def format(self,row_data,cell_item):
       if self.datefmt_out != "" and cell_item != "":
           return DateTime.reformatDateTime(self.datefmt_in,self.datefmt_out,cell_item)
       else:
            return cell_item
        
class TableColumn_DateStamp(TableColumn_DateBase): 
    """
        A custom table column for changing the color of the
        text used when drawing the date for the last
        time the song was played
    """
    
    def paintItem(self,col,painter,row,item,x,y,w,h):
        default_pen = painter.pen()
        
        song = self.parent.data[row]
        
        new_pen = default_pen
        if self.parent.date_mark_1 != 0 and self.parent.date_mark_2 !=0 and not song.banish:
            if song[EnumSong.DATEVALUE] > self.parent.date_mark_1:
                new_pen = self.parent.color_text_played_recent
            elif song[EnumSong.DATEVALUE] < self.parent.date_mark_2:
                new_pen = self.parent.color_text_played_not_recent
        
        painter.setPen(new_pen)
        
        self.paintItem_text(col,painter,row,item,x,y,w,h)
        
        painter.setPen(default_pen)

class TableColumn_Score(TableColumn): 
    """
        A custom table column for changing the color of the
        text used when drawing the date for the last
        time the song was played
    """
    
    def paintItem(self,col,painter,row,item,x,y,w,h):
      

        self.paintItem_text(col,painter,row,"%6.3f"%(item/100.0 ),x,y,w,h)
  
        
if __name__ == "__main__":

    import sys
    
    app = QApplication(sys.argv)
    
    #style_set_custom_theme("D:\\Dropbox\\Scripting\\PyModule\\GlobalModules\\src\\","default",app)

    from Song_LibraryFormat import *
    path = r"D:\Dropbox\ConsolePlayer\user\music.libz"
    
    t1 = SongTable()
    t1.setData(musicLoad_LIBZ(path))
    t1.container.resize(800,320)
    t1.container.show()
   
    #p = QApplication.palette()
    #CR = [QPalette.Light,QPalette.Midlight,QPalette.Mid,QPalette.Dark,QPalette.Shadow]
    #for cr in CR:
    #    c = p.color(QPalette.Active,cr)
    #    print c.red(),c.blue(),c.green()
    
    sys.exit(app.exec_())     