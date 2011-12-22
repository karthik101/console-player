
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from SystemDateTime import DateTime
from Qt_CustomStyle import *

from math import ceil,floor

# http://wiki.python.org/moin/TimeComplexity not sure if i should use set,dict,or list for selection, using set for now
class LargeTableCore(QWidget):
    """
        LargeTableCore
        
        A Table widget for handling very large data sets
        
        LargeTableCore handles all of the rendering and mouse events associated with the table
        
        all values required for drawing are initialized in __init__
        
        see LargeTableBase for the implementation of all getter/setters of variables used
        for drawing and rendering data in the table
        
        LargeTableCore cannot be instantiated by itself.
    """
    
    column_header_resize = pyqtSignal() #emit this when the headers are resized
    column_header_sort_request = pyqtSignal('int') # emit this, when a header needs to be sorted
    
    def __init__(self,parent=None):
        if type(self) == LargeTableCore:
            raise RuntimeError("Cannot instantiate a LargeTableCore Class, use LargeTableBase or LargeTable instead")
        self.parent = parent
        super(LargeTableCore, self).__init__(None)

        self.painter_brush_default = None
        
        self.data_x = 0   #set by resize events, 
        self.data_y = 0   # the x,y and width/height of the data drawing region
        self.data_w = 100 # the visible 'cells' of the table
        self.data_x = 100 # These values are dummy until the first resize occurs
        self.data_x2= 100 # after __init__
        self.data_y2= 100 # x2,y2 is the bottom right corner
        
        self.padding_top    = 0; # padding from widget boundaries to start drawing
        self.padding_bottom = 0; # padding from widget boundaries to start drawing
        self.padding_left   = 0; # padding from widget boundaries to start drawing
        self.padding_right  = 0; # padding from widget boundaries to start drawing
        
        self.text_padding_top    = 2; # distance from top border of a cell
        self.text_padding_bottom = 2; # distance from bottom border of a cell
        self.text_padding_left   = 3; # distance from left border of a cell
        self.text_padding_right  = 3; # distance from right border of a cell
        
        self.offset_col_horizontal = 0;     # x adjustment for start drawing of columns. can take negative values
        self.offset_col_rowheader = 32;     # col offset due to have row headers on.
        self.offset_row_index = 0;          # which element in data to draw in the first row
        self.cell_line_width = 1;
        
        self.enable_autoset_row_height = True
        self.enable_last_column_expanding = False # last column will expand to will visible region of table, always
        self.row_height = 18;
        
        self.col_header_height = 18    # height of the col header or zero for off
        self.row_header_width = 32  # width of the row header or zero for off
        self.showAlternateRowColors = True # toggle visibility of alternate row colors
        self.showGridLines = True
        self.enableSortColumn = True # set to true to be able to click and sort columns
        
        self.tolerance_grips = 3;
        
        self.mouse_resize_col = -1; # set 0-X for which col to resize on mouse drag
        self.mouse_resize_col_enable = False
        self.mouse_resize_col_owidth = 0; # original width for the colu,m being resized
        self.mouse_move_col = -1;   # which column to relocate on mouse release
        self.mouse_move_col_target = -1 # where to drop the column
        self.mouse_move_col_enable = False
        self.mouse_move_col_start  = False
        self.mouse_col_header_hover_index = -1; # set to the value of the current header the mouse is over
        self.mouse_pos_drag_start_x = 0;
        self.mouse_pos_drag_start_y = 0;
        self.mouse_tracking_column_index = -1 # used in tracking the mouse, and determining it has left a cell
        self.mouse_disable_release = False
        self.mouse_disable_col_click_event = False # used when column resizing takes affect
        self.drag_start_enable = False # whether a drag is being performed
        
        self.columns = []      # columns are defined as an array of Column objects
        self.columns_hidden = []    # list of hidden columns - not being rendered
        self.initColumns()
        
        self.selection = set();     # set of selected rows
        self.selection_clone = None;    # copy of the selected row set
        self.selection_last_row_added = 0
        self.selection_first_row_added = 0
        self.selection_defer = False # when true, selection update waits until mouse release
                                     # by defering, we can check for and handle mouse drags on selected data
        self.data=[]
        
        self.text_display_none = "<No Data>"

        self.draw_debug = False
        
        self.data = []
        
        self.brush_default = QBrush(QColor(0,0,0,0));
        
        self.setMouseTracking(True);
        self.setFocusPolicy(Qt.WheelFocus)

        self.rowHighlight_complex1_exp = None             # define complex row highlighters, lambda expressions
        self.rowHighlight_complex2_exp = None             # that return Truethy or Falsey expresions - True to highlight
        self.rowHighlight_complex1_color = QColor(200,0,0)
        self.rowHighlight_complex2_color = QColor(200,0,200)
        
        self.rowHighlight_simple1_list  = []             # define simple row highlighters, lists,
        self.rowHighlight_simple2_list  = []             # row is highlighted if it appears in the list of rows to highlight
        self.rowHighlight_simple1_color = QColor(0,0,200)
        self.rowHighlight_simple2_color = QColor(0,200,0)
        
        self.rowHighlight_complex_list = []
        self.rowHighlight_simple_list  = []
        self.rowTextColor_complex_list = [] # define a list of complex textColor items,
                                            # this list is a list of tuples.
                                            # the first item in the tuple is a lambda or function that accepts a row index
                                            # the second item in the tuple is a QColor
        self.rowTextColor_simple_list  = []
    def initColumns(self):
        """
            Overload this method to initilize columns
        """
        self.columns = [TableColumn(self,0),]
    def calculateGeometry(self):
        w = self.width()
        h = self.height()
        
        # this way these ranges do not need to be calculated in each
        # method that requires knowing the ranges
        # data_x does not include the width of the row header
        self.data_x = self.padding_left
        self.data_y = self.padding_top + self.col_header_height
        self.data_w = w - self.data_x - self.padding_right  - self.padding_left - self.cell_line_width
        self.data_h = h - self.data_y - self.padding_bottom - self.padding_top - self.cell_line_width
        
        # this corresponds to the true start of the cell data, and the right boundary
        # of the row header, including the offset contribution to the horixontal scrollbar

        self.data_x2 = self.data_x+self.data_w # right x pos boundary
        self.data_y2 = self.data_y+self.data_h # bottom y pos boundary
        
        if self.data_x2 < self.data_x:  # fix bounding issues
            self.data_x2 = self.data_x
            self.data_w = 0
            
        if self.data_y2 < self.data_y:
            self.data_y2 = self.data_y
            self.data_h = 0
            
    def resizeEvent(self,event):  
    
        self.calculateGeometry();
        
    def paintEvent(self, event):
        #self.dt.timer_start();
        w = self.width()
        h = self.height()
        
        painter = QPainter(self)
        self.setPaletteGroup() # set colors to active/inactive/disabled versions
        painter.setRenderHint(0) # QPainter.Antialiasing
        painter.setFont(self.font())
        self.painter_brush_default = painter.brush()
        self.painter_brush_font = self.palette_brush(QPalette.WindowText)
        self.painter_color_text_selected = self.palette_brush(QPalette.HighlightedText).color()
        
        if self.enable_autoset_row_height:
            self.row_height = QFontMetrics(self.font()).height() + self.text_padding_top + self.text_padding_bottom
        if self.row_header_width: # auto adjust row header width to always be able to contain the number value
            self.row_header_width = QFontMetrics(self.font()).width("%d"%len(self.data))+4
        
        # set the default text color for each row
        # the column renderer does not have to obey this list, but it is recommended
        self.row_text_colors = [None]*self.rowCount()
        for ii in range(self.rowCount()):
            jj = ii + self.offset_row_index
            self.row_text_colors[ii] = self.getRowTextColor(jj) 
            
        #painter.setBackground(self.palette_brush(QPalette.Window))
                
        painter.setClipping(True)     
        # paint the background color
        painter.fillRect( 0,0,self.width(),self.height(),self.palette_brush(QPalette.Base));
        
        self.paint_rowHighlights(painter,self.data_x,self.data_y,self.data_w,self.data_h)
        self.paint_gridLines(painter,self.data_x,self.data_y,self.data_w,self.data_h)
        
        self.paint_header_row(painter,self.data_x,self.data_y,self.row_header_width,self.data_h)
        self.paint_header_col(painter,self.data_x,self.padding_top,self.data_w,self.data_h)
       
        self.paint_data(painter,self.data_x,self.data_y,self.data_w,self.data_h)
        
        painter.setClipping(False) 
        
        if self.draw_debug:
            self.paint_debug(painter,self.data_x,self.data_y,self.data_w,self.data_h)
        
        
        
        
        #self.dt.timer_end()
        #self.dt.timedelta - 630
        #self.data[0][0] = self.dt.formatTimeDeltams(self.dt.timedelta)
        #self.data[1][0] = self.dt.timedelta,w,h,w*h
        
        return;
        
    def paint_debug(self,painter,x,y,w,h):
        #_x = 
        _x = x - self.offset_col_horizontal + self.row_header_width
        _y = y - self.col_header_height
        
        col_list = self._paint_get_col()
        
        for col in col_list:
            _x += col.width
            if _x < self.padding_left+self.row_header_width:    # skip any col that will be invisible on the left side
                    continue
            if _x > self.data_x2:
                break
            # draw the region used to detect column resize
            painter.fillRect(_x-self.tolerance_grips,_y,self.tolerance_grips*2,self.col_header_height,QColor(255,0,0,96))

            #
        # if i got the following working, which is an attempt to use QStyle to draw
        # a scroll bar, i would not need to implement the LargeTable Code the way i did
        # and any code that uses self.container to add to a layout, would be changed to just 'self'
        # further-more, column headers could be rendered using the QStyle-button methods
        # which would allow for e to use css to style buttons
        # any widget would be LargeTable::ScrollBar
        # qsp = QStylePainter( self ) 
        # 
        # qos = QStyleOptionSlider()
        # qos.state = QStyle.State_Active
        # qos.maximum = 100
        # qos.minimum = 0
        # qos.pageStep = 5
        # qos.singleStep = 1
        # qos.sliderValue = 50
        # qos.rect = QRect( QPoint(100,100) , QSize(20,200))
        # qos.palette = self.palette()
        # # qos.direction = Qt.LeftToRight
        # qos.orientation = Qt.Vertical
        # qos.state = QStyle.State_Active
        # qos.subControls= QStyle.SC_ScrollBarAddLine | QStyle.SC_ScrollBarSubLine | \
        #                  QStyle.SC_ScrollBarAddPage | QStyle.SC_ScrollBarSubPage | \
        #                  QStyle.SC_ScrollBarFirst   | QStyle.SC_ScrollBarLast    | \
        #                  QStyle.SC_ScrollBarSlider
        # qos.activeSubControls = QStyle.SC_ScrollBarAddLine
        # 
        # qcs = app.style()
        # painter.fillRect (qos.rect,Qt.blue) # the scrollbar should cover this rectangle
        # qcs.drawComplexControl(QStyle.CC_ScrollBar,qos,painter)    
        
        return
            
    def paint_gridLines(self,painter,x,y,w,h):
        """
            draw gridlines, corresponding to rows and cols 
            starting at x,y, and for width w and height h.
        """
         ##############################
        # paint alternate row colors

        
        pen = QPen();
        pen.setWidth(self.cell_line_width)
        painter.setPen(pen)
        painter.drawRect(x,y,w,h)
        
        if self.col_header_height: # draw a top border line along the top of all col-headers
            painter.drawLine(x+ self.row_header_width,y-self.col_header_height,x+w,y-self.col_header_height)
            #painter.drawLine(x,y-self.col_header_height,x,self.col_header_height) # close the left-most col header box
            painter.drawLine(x+w,y-self.col_header_height,x+w,y) # close the rightmost col header box
        if self.row_header_width: # draw a border line between col-0 and the header
            painter.drawLine(x+ self.row_header_width,y-self.col_header_height,x+ self.row_header_width,y+h)
        else:
            painter.drawLine(x,y-self.col_header_height,x,self.col_header_height)
            
        if self.showGridLines:
            
            col_list = self._paint_get_col()
            if self.enable_last_column_expanding:
                col_list = col_list[:-1]
            # ##############################
            # draw col lines
            _x = self.data_x - self.offset_col_horizontal + self.row_header_width
            for col in col_list:
                _x += col.width
                if _x <= self.padding_left+self.row_header_width: 
                    continue; # skip columns on the left that will not be drawn
                if _x >= self.data_x2: 
                    break;  # stop drawing when we run out of room
                painter.drawLine(_x,self.data_y-self.col_header_height,_x,self.data_y2)
                
            # ##############################
            # draw row lines
            _y = self.data_y+self.row_height
            while _y < y+h:
                painter.drawLine(self.data_x,_y,self.data_x+self.data_w,_y)     
                _y += self.row_height
       
        painter.setPen(QPen())
        
    def paint_rowHighlights(self,painter,x,y,w,h):
        _y = y 
        i=0;
        brush_alt_row = self.palette_brush(QPalette.AlternateBase)
        while _y < y+h and self.offset_row_index+i < len(self.data):
            _h = self.row_height
            if _y+_h >= y+h: _h = y+h-_y # cap the region for the last row or min(row_height,y+h-_y)
            
            brush = self.getRowHighlight(self.offset_row_index+i)
 
            if brush != None:
                painter.fillRect( x,_y,w,_h,brush); 
            elif i%2 == 1 and self.showAlternateRowColors:
                painter.fillRect( x,_y,w,_h,brush_alt_row); 
                
            i+=1;
            _y += self.row_height
            
    def paint_header_row(self,painter,x,y,w,h):
        c = self.offset_row_index;        
        _y = y;
        
        
        while c < len(self.data) and _y < y+h:
        
            _ch = self.row_height
            if _y + _ch > self.data_y2:
                _ch = self.data_y2 - _y
                
            painter.setClipRect(x,_y,w,_ch)    

            painter.setPen( self.row_text_colors[c-self.offset_row_index] )

            painter.drawText( x,_y,self.row_header_width,self.row_height,Qt.AlignCenter,
                          str(c+1)
                        )
            #check if this row is selected
            # if it is draw a colored rectangle highlighting it.
            #if c in self.selection:
            #    painter.fillRect( x,_y+1,w-1,self.row_height-1,self.palette_brush(QPalette.Highlight) )
            _y += self.row_height
            c+=1;
        painter.setPen(self.painter_brush_default.color())
    
    def paint_header_col(self,painter,x,y,w,h):
    
        _x = x - self.offset_col_horizontal + self.row_header_width
        
        col_list = self._paint_get_col()
                
        for i in range(len(col_list)):
            col = col_list[i]
            _cx = _x+self.cell_line_width
            _cy = y+self.cell_line_width
            _cw = col.width 
            _ch = self.row_height 

            if _x + _cw < self.padding_left + self.row_header_width :    # skip any col that will be invisible on the left side
                _x += col.width;                # increment x for the next column
                continue
            if _x > self.data_x2:                        # stop drawing when there is no more room
                break;
                
            if col.width < col.minimum_width:   # best place to check minimum width
                col.width = col.minimum_width   # requirements
                
            col_width = col.width
            
            if i == len(col_list)-1 and self.enable_last_column_expanding: # the last row
                _cw = x+w-_cx
                col_width = max(_cw,col_width)
                
            if _cx <= self.padding_left+self.row_header_width: 
                _cx = self.padding_left+self.row_header_width+1 # clip text that will appear on the left side outside of a cell

            if _cy + _ch >= self.data_y: # clip the last row if it will draw outside the cell region
                _ch = self.data_y - _cy + 1   # height is only the remaining height of the row
            if _cx + _cw >= self.data_x2: # clip the last col if it will draw outside the cell region
                _cw = x+w-_cx    # width is capped at remaining width in display area
                
            painter.setClipRect(_cx,_cy,_cw,_ch)
            col.paintHeader(painter,_x,y,col_width,_ch)
            
            _x += col.width; # increment x for the next column
    
    def paint_data(self,painter,x,y,w,h): 
        """
            paint each row available for
            paint each column, from left to right. and skip any columns that will not be visible
            where:
               (x,y) is the top left of the drawing region
               w is the width
               h is the height
        """
               

        col_list = self._paint_get_col()

        _x = x - self.offset_col_horizontal + self.row_header_width

        for col in col_list:
            
            
            _cx = _x+self.cell_line_width # generate the co'ords for cell boundaries and widths
            
            _cw = col.width
            _ch = self.row_height
            
            if _x + _cw < self.padding_left:    # skip any col that will be invisible on the left side
                _x += col.width;                # increment x for the next column
                continue
            if _x > x+w:                        # stop drawing when there is no more room
                break;

            if _cx <= self.padding_left+self.row_header_width: _cx = self.padding_left+self.row_header_width # clip text that will appear on the left side outside of a cell

            _y = y
            c = 0
            while self.offset_row_index+c < len(self.data) and _y < y+h:
                item_row = self.offset_row_index+c
                item = self.getItem(item_row,col.index)
                
                col_width = col.width
                if col == col_list[-1] and self.enable_last_column_expanding: # the last row
                    _cw = x+w-_cx
                
                _cy = _y+self.cell_line_width
        
                if _cy + _ch >= y+h: # clip the last row if it will draw outside the cell region
                    _ch = y+h-_cy    # height is only the remaining height of the row
                if _cx + _cw >= x+w: # clip the last col if it will draw outside the cell region
                    _cw = x+w-_cx    # width is capped at remaining width in display area
                    
                # set a region so that the item cannot paint outside of it's own cell    
                painter.setClipRect(_cx,_cy,_cw,_ch)
                # let the col paint the item
                #TODO calling with col as first argument is a workaround
                # to be able to override this function with arbitrary functions
                # that would accept the same arguments

                painter.setPen( self.row_text_colors[c] )
                
                col.paintItem(col,painter,item_row,item,_x,_y,max(_cw,col.width),self.row_height)
                
                _y += self.row_height
                c+=1;

            _x += col.width; # increment x for the next column
         
        painter.setPen(self.painter_brush_default.color())
         
    def _paint_get_col(self):    
        """
            private method used for painting
            returns the list of columns to be used when painting
            
            different internal events have the ability to change the order
        """
        col_list = self.columns
        if self.mouse_move_col_enable:
            if self.mouse_move_col != self.mouse_move_col_target :
                temp = self.columns[self.mouse_move_col]
                col_list = self.columns[:]
                col_list.remove(temp)
                col_list.insert(self.mouse_move_col_target,temp)
        return col_list
        
    def palette_brush(self, color_type , alt=False ):
        """
            return a brush for a given color_type
            
            the color_group is determined automatically, by setPaletteGroup at the begining of paintEvent
            
            the color_type determines which color to draw and is set by the global palette
            
            however alpha values need to be set on a by-color basis, and while i am at it
            i can customize some colors by changing the brush besfore it is returned
            
            alt can be set to a non-Falsey value to control colors to an even greater degree
            
        """
        brush = self.palette().brush(self.color_group,color_type)
        color = brush.color()
        
        #if color_type == QPalette.AlternateBase:
            # AlternateBase is used as an alternate row color in this widget
            #color = QApplication.palette().brush(self.color_group,QPalette.AlternateBase).color()
            #color.setRed( color.red()/1.25) # 20% darker than Base color
            #color.setBlue( color.blue()/1.25)
            #color.setGreen( color.green()/1.25)
        if color_type == QPalette.Button:
            app_palette =QApplication.palette()
            g = QLinearGradient(0,0,0,1)
            

            if alt: 
                g = QLinearGradient(0,0,0,1)
                c1 = app_palette.color(self.color_group,QPalette.Light)
                c2 = app_palette.color(self.color_group,QPalette.Midlight)
                c3 = app_palette.color(self.color_group,QPalette.Mid)
                g.setColorAt(0   ,c1)
                g.setColorAt(0.5 ,c2)
                g.setColorAt(1   ,c3)
            else:
                g = QLinearGradient(0,0,0,1)
                c1 = app_palette.color(self.color_group,QPalette.Midlight)
                c2 = app_palette.color(self.color_group,QPalette.Dark)
                g.setColorAt(0,c1)
                g.setColorAt(1,c2)
            
            g.setCoordinateMode(QGradient.ObjectBoundingMode)     
            
            return QBrush(g)
        elif color_type == QPalette.Highlight:   
            if not self.hasFocus():
                color.setAlpha(64)
            else:
                color.setAlpha(190)
            
        brush.setColor(color)
        return brush
 
    def setPaletteGroup(self):
        """
            the palette group is state dependant and modifies colors used when drawing
        """
        if self.isEnabled():
            if self.hasFocus():
                self.color_group = QPalette.Active
            else:
                self.color_group = QPalette.Inactive
        else:
            self.color_group = QPalette.Disabled
            
    def mouseMoveEvent(self,event=None):
        w = self.width()
        h = self.height()
        mx = event.x()
        my = event.y()

        cx,cy = self._mousePosToCellPos(mx,my)
        cur_r,cur_c = self.positionToRowCol(mx,my)
        cell_capture = False
        
        _x = self.data_x - self.offset_col_horizontal + self.row_header_width#self.data_xl
        _y = self.data_y - self.col_header_height
        
        # for when user is moving the mouse over a column that has mouse tracking enabled
        if self.mouse_tracking_column_index >= 0 and cur_c != self.mouse_tracking_column_index:
            self.columns[self.mouse_tracking_column_index].mouseHoverExit(event)
            self.mouse_tracking_column_index = -1
            self.update()
            return
            
        # user is resizign a column by draging the mouse    
        if self.mouse_resize_col_enable == True:
            
            self.mouse_disable_col_click_event = True
            delta = event.x() - self.mouse_pos_drag_start_x
            new_width = self.mouse_resize_col_owidth + delta
            if new_width >= self.columns[self.mouse_resize_col].minimum_width:
                self.columns[self.mouse_resize_col].width = new_width
                self.column_header_resize.emit()
                self.update();
            return;
        # useris moving a column    
        elif self.mouse_move_col_start == True:
            # toggle the mode from column drag can start
            # to column drag is now enabled when the user drags a minimum distance
            # same concept is used in mouse dragging, and prevents drags from starting
            # under odd conditions of mouse click
            delta = ( float(self.mouse_pos_drag_start_x -mx)**2 + float(self.mouse_pos_drag_start_y-my)**2 ) ** .5
            if delta > 5.0:
                self.mouse_move_col_start  = False
                self.mouse_move_col_enable = True
                self.setCursor(Qt.ClosedHandCursor)
                return
        elif self.mouse_move_col_enable == True:
            #self.setCursor(Qt.ClosedHandCursor)
            #col_list = self._paint_get_col() seems to work better without this
            self.mouse_disable_col_click_event = True
            for i in range(len(self.columns)):
                _xl = _x
                _x += self.columns[i].width
                if _x < self.padding_left+self.row_header_width:    # skip any col that will be invisible on the left side
                        continue
                if mx > _xl and mx < _x:
                    if self.mouse_move_col_target != i:
                        self.mouse_move_col_target = i   
                        self.update();   
            return;
        # mouse is within the column header structure
        elif my > _y and my < _y+self.col_header_height-2: # use a 2 pixel buffer on mouse detection
            #enable draw to resize column by setting mouse_resize_col to the col
            # to resize whenever the mouse enters a mouse grip region,
            # tell the user it is a valid region by changing the mouse icon
            col_list = self.columns
            #if self.enable_last_column_expanding:
            #    col_list = col_list[:-1]
                
            for i in range(len(col_list)):
                _xl = _x    #  _xl = left side boundary x position of column header
                flag_skip_grip=False
                temp_w = col_list[i].width
                if _x + temp_w >= self.data_x2: # clip the last col if it will draw outside the cell region
                    temp_w = self.data_x2-_x-1    # width is capped at remaining width in display area
                    flag_skip_grip = True
                _x += temp_w   # _x = right side boundary x position of column header  
                
                if _x < self.padding_left+self.row_header_width:    # skip any col that will be invisible on the left side
                    continue
                if _xl > self.data_x2:  # stop when we are outside the drawing region
                    break

                #check that the mouse is hovering over resize grips
                if mx > _x-self.tolerance_grips and mx < _x+self.tolerance_grips and not flag_skip_grip and \
                        ( (i < len(col_list)-1 and self.enable_last_column_expanding) or not self.enable_last_column_expanding):
                    self.setCursor(Qt.SplitHCursor)
                    self.mouse_resize_col = i
                    self.mouse_move_col = -1
                    self.mouse_col_header_hover_index = i
                    self.update();
                    return;
                # check  that the mouse is within the column header
                elif mx > _xl+self.tolerance_grips and mx < _x-self.tolerance_grips:
                    #self.setCursor(Qt.OpenHandCursor) # then Qt.ClosedHandCursor
                    #self.setCursor(	Qt.PointingHandCursor )
                    self.setCursor(Qt.ArrowCursor)
                    self.mouse_resize_col = -1
                    self.mouse_move_col = i
                    self.mouse_col_header_hover_index = i
                    self.update();
                    return;
                    
            self.mouse_resize_col = -1
            self.mouse_move_col = -1
            #self.mouse_col_header_hover_index = -1
        
        elif my > _y+self.col_header_height:
            
            
            if cur_c != -1:
                cell_capture = self.columns[cur_c].mouseHover(cur_r,cx,cy)
                
            if cell_capture:
                self.mouse_tracking_column_index = cur_c
            else:
                if event.buttons() == Qt.LeftButton:
                    self.dragStart(event);
        
        if self.mouse_col_header_hover_index != -1 or cell_capture:
            self.mouse_col_header_hover_index = -1
            self.update()
            
        self.setCursor(Qt.ArrowCursor)
    
    def mouseDoubleClickEvent(self,event=None):
        """
            if you want to reimplement double click on a mouse row 
            see the method mouseDoubleClick
        """
        w = self.width()
        h = self.height()   
        mx = event.x()
        my = event.y()
        self.mouse_resize_col_enable = False
        self.mouse_resize_col = -1       
        
        if my < self.col_header_height:
            _x = self.data_x - self.offset_col_horizontal + self.row_header_width#self.data_xl
            for i in range(len(self.columns)):
                _xl = _x
                _x += self.columns[i].width
                if _x < self.padding_left+self.row_header_width:    # skip any col that will be invisible on the left side
                        continue
                # check for double click on resize grips
                if mx > _x-self.tolerance_grips and mx < _x+self.tolerance_grips:
                    self.columns[i].width = self.columns[i].preferredWidth()
                    self.mouse_disable_release = True
                    self.column_header_resize.emit()
                    self.update();
        elif mx > self.data_x and mx < self.data_x2 and my > self.data_y and my < self.data_y2:
            row,col = self.positionToRowCol(mx,my)
            self.mouseDoubleClick(row,col)
            self.update()
            
    def mousePressEvent(self,event=None):
        w = self.width()
        h = self.height()
        mx = event.x()
        my = event.y()
        _shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier     # this generates a boolean type
        _ctrl = event.modifiers()&Qt.ControlModifier == Qt.ControlModifier
        
        self.mouse_disable_col_click_event = False
        self.mouse_disable_release = False
        self.selection_defer = False
        
        self.drag_start_enable = False;
        
        if event.buttons() != Qt.LeftButton:
            return
        
        if my > self.data_y:
            self.mouse_move_col_enable=False
            self.mouse_move_col_start =False
            self.mouse_move_col = -1
            self.mouse_move_col_target = -1
                
                
        if self.mouse_resize_col >= 0:
            self.mouse_pos_drag_start_x = event.x()
            self.mouse_pos_drag_start_y = event.y()
            self.mouse_resize_col_owidth = self.columns[self.mouse_resize_col].width
            self.mouse_resize_col_enable = True
        elif self.mouse_move_col >= 0:
            self.mouse_pos_drag_start_x = event.x()
            self.mouse_pos_drag_start_y = event.y()
            self.mouse_move_col_start=True
        # check for a row click - press
        elif mx > self.data_x and mx < self.data_x2 and my > self.data_y and my < self.data_y2:
            cx,cy = self._mousePosToCellPos(mx,my)
            r,c = self.positionToRowCol(mx,my)
            cell_capture = False
            if c != -1:
                cell_capture = self.columns[c].mouseClick(r,cx,cy)
                if cell_capture: # end this function if the cell captured the click
                    return
            self.mouse_pos_drag_start_x = mx; # used when trying to start a drag
            self.mouse_pos_drag_start_y = my;
        
            row = (my-self.data_y) / self.row_height # each row is row_height tall, so row calculation is easy
            row += self.offset_row_index
            
            if row in self.selection:
                self.selection_defer = True # update selection on mouse release intead
            else:    
                self.__modify_selection(_shift,_ctrl,row)
          
    def mouseReleaseEvent(self,event=None):    
         
        
        self.mouse_resize_col_enable = False
        self.mouse_resize_col = -1
        
        if event.button() == Qt.LeftButton:
            self.__mouseReleaseLeft(event)
        elif event.button() == Qt.RightButton:
            self.__mouseReleaseRight(event)
        else:
            print "middle click"
            
        self.mouse_disable_release = False
        self.mouse_disable_col_click_event =False
        self.mouse_move_col_enable=False
        self.mouse_move_col_start =False
        self.mouse_move_col = -1
        self.mouse_move_col_target = -1
        #self.mouse_col_header_hover_index = -1
        self.setCursor(Qt.ArrowCursor)   
            
        return
       
    def __mouseReleaseLeft(self,event):
    
        w = self.width()
        h = self.height()  

        mx = event.x()
        my = event.y()
        
        _shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier      # this generates a boolean type
        _ctrl = event.modifiers()&Qt.ControlModifier == Qt.ControlModifier  

        if my < self.col_header_height and not self.mouse_disable_release:
            # column move 
            if self.mouse_move_col_enable and self.mouse_move_col_target != -1 and self.mouse_move_col != self.mouse_move_col_target :
                    temp = self.columns[self.mouse_move_col]
                    self.columns.remove(temp)
                    self.columns.insert(self.mouse_move_col_target,temp)
                    # update the variable which controls drawing of hover state for columns
                    self.mouse_col_header_hover_index = self.mouse_move_col_target
                    self.update();
            # column header was clicked
            elif self.mouse_col_header_hover_index >= 0 and self.enableSortColumn and not self.mouse_disable_col_click_event:
                flag = False # true when mouse is within resize region
                _x = self.data_x - self.offset_col_horizontal + self.row_header_width#self.data_xl
                for i in range(len(self.columns)):
                    _xl = _x
                    _x += self.columns[i].width
                    if _x < self.padding_left+self.row_header_width:    # skip any col that will be invisible on the left side
                            continue
                    #checkt that the mouse is hovering over resize grips
                    if mx > _x-self.tolerance_grips and mx < _x+self.tolerance_grips:
                        flag = True
                if not flag: #user clicked within a column header
                    self.column_header_sort_request.emit(self.mouse_col_header_hover_index)
                #self.setSortColumn(self.mouse_col_header_hover_index)
        
        # check for a row click - release
        elif mx > self.data_x and mx < self.data_x2 and my > self.data_y and my < self.data_y2:
            row = (my-self.data_y) / self.row_height # each row is row_height tall, so row calculation is easy
            row += self.offset_row_index
            if self.selection_defer:# update selection on mouse release intead
                self.__modify_selection(_shift,_ctrl,row)
 
    def __mouseReleaseRight(self,event):
        #w = self.width()
        #h = self.height()  
        
        mx = event.x()
        my = event.y()
        
        #_shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier      # this generates a boolean type
        #_ctrl = event.modifiers()&Qt.ControlModifier == Qt.ControlModifier  
        if my < self.col_header_height:
            self.mouseReleaseRightHeader(event)
        elif mx > self.data_x and mx < self.data_x2 and my > self.data_y and my < self.data_y2:
            self.mouseReleaseRight(event)
            
    def _mousePosToCellPos(self,mx,my):
        cell_x = 0
        cell_y = 0
        _ystart = self.padding_top + self.col_header_height
        cell_y = (my-_ystart)%self.row_height
        
        _x = self.data_x - self.offset_col_horizontal + self.row_header_width
        col_list = self._paint_get_col()
        for col in col_list:
            if _x+col.width > mx:
                cell_x = mx-_x
                break;   
            _x += col.width
            if _x < self.padding_left+self.row_header_width:    # skip any col that will be invisible on the left side
                    continue
        return cell_x,cell_y
        
    def positionToRowCol(self,x,y):
        """
            x,y as logical co'ords within the widget
            returns the appropriate row col or -1
            
            return type is tuple (row,col)
        """
        row = -1
        if y > self.data_y and y < self.data_y2:
            row = (y-self.data_y) / self.row_height # each row is row_height tall, so row calculation is easy
            row += self.offset_row_index
            
        col = -1
        _x = self.data_x - self.offset_col_horizontal + self.row_header_width
        if x > _x and x < self.data_x2:
            
            col_list = self._paint_get_col()
            col = 0
            for i in range(len(col_list)):
                _x += col_list[i].width
                col = i
                if _x < self.padding_left+self.row_header_width:    # skip any col that will be invisible on the left side
                    continue
                if x < _x:
                    break
            else: # if it breaks naturally set it back to -1
                col = -1
        return (row,col)
        
    def dragStart(self,event):
        mx = event.x()
        my = event.y()
        
        if not self.drag_start_enable and len(self.selection) > 0:
            
            # distance formula - drag a minimum distance to initiate the drag event
            # this will prevent starting a drag when the user double clicks
            delta = ( (self.mouse_pos_drag_start_x -mx)**2 + (self.mouse_pos_drag_start_y-my)**2 ) **.5
            if delta > 5: # 5 is an arbitrary small value
                self.drag_start_enable = True;
                mimeData = MimeData()
                mimeData.setList(self.getSelection())
                mimeData.setText(self.getSelectionString())
                drag = QDrag(self)
                drag.setMimeData(mimeData)
                drag.start()
                
    def leaveEvent(self,event=None):
        self.mouse_resize_col_enable = False
        self.mouse_resize_col = -1

        self.mouse_move_col_enable=False
        self.mouse_move_col_start =False
        self.mouse_move_col = -1
        self.mouse_move_col_target = -1
        
        self.setCursor(Qt.ArrowCursor)
    
    def keyReleaseEvent(Self,event=None):
        """

        """
        _shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier     # this generates a boolean type
        _ctrl = event.modifiers()&Qt.ControlModifier == Qt.ControlModifier
        
        print "%X"%event.key(),_shift,_ctrl
    
    def __modify_selection(self,_shift,_ctrl,row):
        """
            private method
            called on mouse press or release to modify the current selection state
        """
        if row < len(self.data):
            if _ctrl and _shift:
                # for shift click select the range from the LAST click to current row
                # ctrl&shift requires remember the previous selection so that the user
                # can edit this selection after clicking - (try this and see what happens)
                if self.selection_clone == None:
                    self.selection_clone = set(self.selection)
                _s = min(self.selection_last_row_added,row)
                _e = max(self.selection_last_row_added,row)+1
                temp = set ( range(_s,_e) )
                self.selection = self.selection_clone | temp # union of both sets
            elif _shift:
                # for shift click select the range from the FIRST click to current row
                _s = min(self.selection_first_row_added,row)
                _e = max(self.selection_first_row_added,row)+1
                self.selection = set ( range(_s,_e) )
                
                self.selection_last_row_added = row
                self.selection_clone = None
            elif _ctrl:
                if row in self.selection:
                    self.selection.remove(row)
                else:
                    self.selection.add(row)
                
                self.selection_last_row_added = row
                self.selection_clone = None
            else:
                self.selection = {row}
                self.selection_first_row_added = row
                self.selection_last_row_added = row
                self.selection_clone = None
                
            self.update()

class LargeTableBase(LargeTableCore):
    """
        A Table widget for handling very large data sets
        
        instead of a standard table with columns and rows, this table
        only has columns. Each column handles drawing for data with the
        cells for that column. A Sliding viewport is used to only 
        represent a small amount of data at a time.
    """
    # signal types as string of c++ types, 'int' 'char' 'QString' 'float' etc
    
    def __init__(self,parent=None):
        super(LargeTableBase,self).__init__(parent)
        self.setAutoFillBackground(True)        
        self.dt = DateTime()

    def setData(self,data):
        self.data = data
     
    def setRowHeight(self,row_height):
        self.row_height = row_height
    
    def setCellPadding(self,l,t,r,b):
        """
            set the cell padding for rendering text,
            left top right bottom
        """
        self.text_padding_top    = t; # distance from top border of a cell
        self.text_padding_bottom = b; # distance from bottom border of a cell
        self.text_padding_left   = l; # distance from left border of a cell
        self.text_padding_right  = r; # distance from right border of a cell
    
    def showColumnHeader(self,bool):
        if bool:
            self.col_header_height = self.row_height
        else:
            self.col_header_height = 0
        self.update()
        
    def showRowHeader(self,bool):
        if bool:
            self.row_header_width = 32 # will be modified again in paint event
        else:
            self.row_header_width = 0 
        self.update()

    def setLastColumnExpanding(self,bool):
        """set whether to auto expand the last column to use all remainging space in the table"""
        self.enable_last_column_expanding = bool
        
    def getLastColumnExpanding(self):
        """ return whether the last column  is set to auto expand"""
        return self.enable_last_column_expanding
        
    def addColumn(self,col_index=-1,index=-1):
        """
            col_index can take one of two type, either TablColumn or integer value
            for the index or it can be left blank
            
            addColumn(TableColumn,index)  - add TableColumn to end of column list
            addColumn(index)        - insert column into index
            addColumn()             - add new column to end of column list
            
            add a new column to the end of the column list.
            or add a pre-defined column to the end of the list
        """
        if isinstance(col_index,TableColumn):
            col_index.parent = self
            if index < 0:
                self.columns.append(temp)
            else:
                self.columns.insert(index,temp)
        else:    
            index = col_index
            if index < 0:
                index = len(self.columns)
                temp = TableColumn(self,index)
                self.columns.append(temp)
            else:
                temp = TableColumn(self,index)
                self.columns.insert(index,temp)
    
    def column(self,index):
        return self.columns[index]
    
    def colCount(self):
        return len(self.columns)
   
    def rowCount(self):
        """
            return the number of rows currently being displayed
            
            this function returns even partial rows counted as a whole row
        """
        _ystart = self.padding_top + self.col_header_height
        _h = self.height() - _ystart - self.padding_bottom - self.padding_top
        return int(ceil(float(_h)/self.row_height))
        
    def rowCountFloor(self):
        """
            return the number of rows currently being displayed
            
            this function returns the number of whole rows displayed
        """
        _ystart = self.padding_top + self.col_header_height
        _h = self.height() - _ystart - self.padding_bottom - self.padding_top
        return _h/self.row_height
        
    def colWidth(self):
        """
            Return the combined width of all columns
        """
        w = 0
        for col in self.columns:
            w+=col.width
        return w
    
    def addRowTextColorComplexRule(self,fncptr,color):
        self.rowTextColor_complex_list.append( (fncptr,color) )
    def setRowTextColorComplexRule(self,index,fncptr,color):
        if fncptr == None:  # allow for updateing color only
            fncptr = self.rowTextColor_complex_list[index][0]
        self.rowTextColor_complex_list[index] = (fncptr,color) # intentional exception chance  
    def countRowTextColorComplexRule(self):
        return len(self.rowTextColor_complex_list)   
    def removeRowTextColorComplexRule(self,index):
        self.rowTextColor_complex_list.pop(index)
    def clearRowTextColorComplexRule(self):
        self.rowTextColor_complex_list = []
        
    def addRowTextColorSimpleRule(self,list_of_rows,color):
        if isinstance(list_of_rows,int):    # convert integer to list
            list_of_rows = [list_of_rows,]
        self.rowTextColor_simple_list.append( (list_of_rows,color) )
    def setRowTextColorSimpleRule(self,index,list_of_rows,color): 
        if list_of_rows == None:  # allow for updateing color only
            list_of_rows = self.rowTextColor_simple_list[index][0]
        if isinstance(list_of_rows,int):    # convert integer to list
            list_of_rows = [list_of_rows,]
        self.rowTextColor_simple_list[index] =  (list_of_rows,color) # intentional exception chance  
    def countRowTextColorSimpleRule(self):   
        return len(self.rowTextColor_simple_list)
    def removeRowTextColorSimpleRule(self,index):
        self.rowTextColor_simple_list.pop(index)
    def clearRowTextColorSimpleRule(self):   
        self.rowTextColor_simple_list = []
    
    def addRowHighlightComplexRule(self,fncptr,color):
        self.rowHighlight_complex_list.append( (fncptr,QBrush(color)) )
    def setRowHighlightComplexRule(self,index,fncptr,color):
        if fncptr == None:  # allow for updateing color only
            fncptr = self.rowHighlight_complex_list[index][0]
        self.rowHighlight_complex_list[index] = (fncptr,QBrush(color)) # intentional exception chance  
    def countRowHighlightComplexRule(self): 
        return len(self.rowHighlight_complex_list)
    def removeRowHighlightComplexRule(self,index):
        self.rowHighlight_complex_list.pop(index)
    def clearRowHighlightComplexRule(self):
        self.rowHighlight_complex_list = []
        
    def addRowHighlightSimpleRule(self,list_of_rows,color):
        if isinstance(list_of_rows,int):    # convert integer to list
            list_of_rows = [list_of_rows,]
        self.rowHighlight_simple_list.append( (list_of_rows,QBrush(color)) )  
    def setRowHighlightSimpleRule(self,index,list_of_rows,color):
        if list_of_rows == None:  # allow for updateing color only
            list_of_rows = self.rowHighlight_simple_list[index][0]
        if isinstance(list_of_rows,int):    # convert integer to list
            list_of_rows = [list_of_rows,]
        self.rowHighlight_simple_list[index] = (list_of_rows,QBrush(color))
    def countRowHighlightSimpleRule(self,list_of_rows,color):
        return len(self.rowHighlight_simple_list)
    def removeRowHighlightSimpleRule(self,index):
        self.rowHighlight_simple_list.pop(index)
    def clearRowHighlightSimpleRule(self,list_of_rows,color):
        self.rowHighlight_simple_list = []
        
    def getRowTextColor(self,row):  
        """
            return the color to use for text in the current row.
            ctc is defined as a tuple of lambda or function and a Qcolor
            
            the function in the ctc should return true or false
        """
        
        if row < len(self.data):
        
            for ctc in self.rowTextColor_complex_list:
                if ctc[0](row):
                    return ctc[1]
                    
            for stc in self.rowTextColor_simple_list:
                if row in stc[0]:
                    return stc[1]

            if row in self.selection:
                return self.painter_color_text_selected
         
        return self.painter_brush_font.color()
        
    def getRowHighlight(self,row):  
        """
            return the color to use for highlight in the current row.
            cth is defined as a tuple of lambda or function and a Qcolor
            sth is defined as a tuple of list,QColor
                where the list is a list of row indexes
            the function in the ctc should return true or false
        """
        
        if row in self.selection:
            return self.palette_brush(QPalette.Highlight)
        
        for cth in self.rowHighlight_complex_list:
            if cth[0](row):
                return cth[1]
                
        for sth in self.rowHighlight_simple_list:
            if row in sth[0]:
                return sth[1]
                
        return None
    
    def mouseDoubleClick(self,row,col):
        print row,col
        
    def mouseReleaseRightHeader(self,event):
        print "header click"
        
    def mouseReleaseRight(self,event):
        #print self._mousePosToCellPos(event.x(),event.y())
        pass
        
    def setSortColumn(self,col_index,direction=0):
        """
            set which column to sort by
            by default, if the column is not already being sorted by
            then the column is set to be sorted by it's default direction
            otherwise, the sort direction is toggled
            
            col_index can either be an integer value as an index into the VISIBLE columns
                or it can be an actual column reference, If using as a column and not an index
                then the column can be either hidden or visible
            
            set the argument direction to a non-zero value (1 or -1)
            to change the sort direction to a specific state
        """
        if isinstance(col_index,TableColumn):
            temp = col_index.column_sort_indicator
            
            for col in self.columns:
                col.column_sort_indicator = 0
                
            if direction != 0:
                col_index.column_sort_indicator = direction 
            elif temp != 0:   
                col_index.column_sort_indicator = temp * -1
            else:
                col_index.column_sort_indicator = col_index.column_sort_default
            
            return col_index.column_sort_indicator
        else:
            #save the indicator value
            temp = self.columns[col_index].column_sort_indicator
            # clear all indicators
            for col in self.columns:
                col.column_sort_indicator = 0

            col = self.columns[col_index]
            # restore or set the indicator of the selected row    
            if direction != 0:
                col.column_sort_indicator = direction 
            elif temp != 0:   
                col.column_sort_indicator = temp * -1
            else:
                col.column_sort_indicator = col.column_sort_default
        
            return col.column_sort_indicator
      
    def getItem(self,i,j):
        """
            Return the item to be displayed at true co'ords i,j
            
            i,j are indexes into the data, and are not indexes in the displayed table
            
            if there is no data at that position "No Data" is returned
        """
        item = None  
        if i < len(self.data):
            if j < len(self.data[i]):
                item = self.data[i][j]
      
        return item
        
    def getSelection(self):
        """
            Return a  new array containing all selected elements
        """
        l = len(self.selection)
        if l == 0:
            return []
            
        temp = [None]*l # create an array with l elements
        
        sel = list(self.selection)
        sel.sort()
        
        count = 0
        for item in sel:
            temp[count] = self.data[item]
            count += 1
        
        return temp
        
    def getSelectionString(self):
        """
            return a comma separated value string with one line per row
            uses the column renderer to take each data item and turn it
            into a string.
        """
        l = len(self.selection)
        if l == 0:
            return []
            
        temp = ""
        
        count = 0
        for row in self.selection:
            R = ""
            for i in range(len(self.columns)):
                item = self.getItem( row, self.columns[i].index)
                s = self.columns[i].itemToString(row,item)
                R += s+"," 

            temp += R+"\n"
            count += 1
        
        return temp    
        
    def clearSelection(self):
        """
            clear the current selection
        """
        self.selection = set()
        self.update()

class TableColumn(object):
    """
        class object provides information on each column
    """
    def __init__(self,parent,index,name=""):
        self.parent = parent;
        self.width = 100;   # requested width for drawing
        self.index = index; # index of data from parent this column is responsible for drawing
        if name == "":
            self.name = "Column %d"%index      # what to draw in the column header
        else:
            self.name = name
        
        self.short_name = None  # if name will not fit in the header width draw this instead, None to disable
            
        self.minimum_width = 14;
        
        self.text_H_align = Qt.AlignLeft; 
        self.text_V_align = Qt.AlignTop; 
        
        self.text_transform = lambda row_data,cell_item: unicode(cell_item);
        
        self.column_sort_indicator = 0 # use 0 for off, -1 for up and 1 for down
        self.column_sort_default = 1 # set to 1/-1, this is the initial direction this column sorts
        
    def setTextAlign(self,halign,valign=Qt.AlignTop):
        """
            halign = Qt.AlignLeft, Qt.AlignRight, Qt.AlignHCenter    
            valign = Qt.AlignTop, Qt.AlignBottom, Qt.AlignVCenter  
            optionally call with a single argument:
            Qt.AlignCenter  - center in both H and V directions
        """
        self.text_H_align = halign; 
        self.text_V_align = valign;
      
    def setTextTransform(funcptr):
        """
            Set the text transformation function when when drawing an item.
            
            by default the transform is a lambda expression transforming
            an item value into a unicode object for painting as a text object
            
            funcptr can either be a function which excepts a single parameter, an item
            or a lambda expression.
            
            the function of lambda must return a unicode text object.
            
            use this to format data before it is displayed in the table cell.
            
        """
        self.text_transform = funcptr
     
    def setWidthByCharCount(self,char_count):
        """
            set the width of the column to be able to display
            char_count characters
        """
        # after testing all printing characters with a few fonts,
        # the letter A tends to be about average, or 1 more than average
        # in how many pixels wide it is and on average it is 7 pixels wide
        # where the average for all characters is 5.8
        self.width = QFontMetrics(self.parent.font()).width("A")*(char_count)+4
        
    def setMinWidthByCharCount(self,char_count):
        self.minimum_width = QFontMetrics(self.parent.font()).width("A")*(char_count)+4
         
    def setMinimumWidth(self,width):
        self.minimum_width = width
         
    def setShortName(self,name):
        """
            set what text should be drawn in the header when the width
            will not be able to contain the full name.
        """
        self.short_name = name
     
    def setDefaultSortReversed(self,reverse):    
        """
            Change the default direction for sorting
            
            By default python sorts lists from smallest value to largest
            and a reverse sort is defined as largest to smallest
            
            when sorting columns the data will be sorted first by 
            Smallest to largest, and clicking again will sort large to small
            
            setting the default to reverse will flip this effect, so that 
            the first click is L-S and the second is S-L
            
            It sometimes makes sense to set this for dates, so that
            sorting puts more recent dates to the top of the list first
            
            default value is False, normal sorting direction
        """
        self.column_sort_default = -1 if reverse else 1
     
    def paintItem(self,col,painter,row,item,x,y,w,h):
        """
            the item 'item' has bin given a rectangle at point x,y with width and height w,h
            this item corresponds to self.index in self.parent.data[row]
            
            paintItem is responsible for rendering this item within the provided space
            if needed the painter item's clipping region could be adjusted.
            
            by overloading this function it will be possible to paint to change how the
            rendering of item occurs. 
            
            By default this method transforms item into a unicode string object and paints
            the text within the given region. If you only want to change how the item is changed
            into a string object modify the method text_transform 
            
            if needed this function can be overloaded to provide custom
            paint events.
            for example, overload it to draw shapes instead of text
            
            a custom paintItem function should not change the clipping regions
        """
        self.paintItem_text(col,painter,row,item,x,y,w,h)
        
    def paintItem_text(self,col,painter,row,item,x,y,w,h):
        """
            this is a helper function for painting item data within a cell
            
            this is the standard method for painting an item within the given area.
            
            this automatically handles positioning and text transforms
        """
        _x = x+self.parent.text_padding_left
        #     y+self.parent.row_height-self.parent.text_padding_bottom
        _y = y+self.parent.text_padding_top
        _h = h-self.parent.text_padding_bottom
        _w = w - self.parent.text_padding_right
        if item == None:
            item = self.parent.text_display_none
        painter.drawText( _x,_y,_w,_h,self.text_H_align|self.text_V_align,
                          self.text_transform(self.parent.data[row],item)
                        )
                        
    def paintHeader(self,painter,x,y,w,h):
    
        if self.parent.columns[self.parent.mouse_col_header_hover_index] == self and \
            self.parent.mouse_col_header_hover_index != -1:
            painter.fillRect(x,y,w,h,self.parent.palette_brush(QPalette.Button,alt=True) );
        else:
            painter.fillRect(x,y,w,h,self.parent.palette_brush(QPalette.Button));
        _w = w    
        # determine if an arrow indicator is in use, if it is draw it
        if self.column_sort_indicator != 0 and self.parent.enableSortColumn:
            _w = w-12 # modify the remaining width for the name
            self._paintSortIndicator(painter,x,y,w,h)
        # if there is room, paint the header name
        painter.setBrush(self.parent.palette_brush(QPalette.ButtonText))
        
        text = self.name
        if QFontMetrics(self.parent.font()).width(text)+4 > _w and self.short_name != None:
            text = self.short_name
            
        if _w > 2:
            painter.drawText( x,y,_w,h,Qt.AlignCenter, text )
            
        painter.setBrush(self.parent.painter_brush_default)               
    
    def _paintSortIndicator(self,painter,x,y,w,h):
        """
            Private method for painting a  sort indicator arrow
            
            TODO: allow user to set a pixmap for the arrows
            index pixmap list using indicator_index+1
            draw the pixmap when set otherwise call this function
        """
        
        # arrow is drawn centered, with the tip +/- 4 pixels from the center
        arrow_point_y = y+h/2+4*self.column_sort_indicator
        arrow_base_y = y+h/2
        # use a 2 pixel thick pen to draw the arrow
        pen = QPen();
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(x+w-11,arrow_base_y,x+w-7,arrow_point_y)
        painter.drawLine(x+w- 3,arrow_base_y,x+w-7,arrow_point_y)
        painter.setPen(QPen())                    
        
    def preferredWidth(self):
        """
            Define the preferred width of the column as the width of the
            text for the widest element currently being displayed in this column
            
            if is better to store the result of this value than to call it repeatedly
            if makes several calls to QFontMetrics.width(...), which is notoriously
            a very slow function
        """
        max_width = self.minimum_width;
        for row in range(self.parent.offset_row_index,self.parent.offset_row_index+self.parent.rowCount()):
            item = self.parent.getItem(row,self.index)
            row_data = None
            if row < len(self.parent.data):
                row_data = self.parent.data[row]  
                text = self.text_transform(row_data,item)
            else:
                text = ""
            item_width = QFontMetrics(self.parent.font()).width(text)
            if item_width > max_width:
                max_width = item_width
        # by adding in the padding, then adding 2, we ensure a default minimum padding around text
        # making the cell width look nicer when set
        return max_width + self.parent.text_padding_left + self.parent.text_padding_right + 2      
        
    def itemToString(self,row,item):
        """
            given a table item, return a string representing that item,
            as it would be displayed as text for in a cell of the table
        """
        row_data = None
        if row < len(self.parent.data):
            row_data = self.parent.data[row]
            return self.text_transform(row_data,item)
        else:
            return ""
     
    def mouseHover(self,row_index,posx,posy): 
        """
            respond to mouse hover
            
            if the current column wants to track mouse movement
            across the cells within the column
            
            returning true will prevent further mouse tracking by the table
            for this column, and cause an update for the table
            
            While On Column Exit is supplied, there is no true way to implement 
            on row exit for mouse tracking. the best way to implement checks for
            row exit would be to monitor row_index and check for changes
            
            the height for any row is  : self.parent.row_height
            the width for the column is: self.width
            the height of the entire column (all rows) is : self.parent.data_y2
        
        """
        return False
    
    def mouseHoverExit(self,event): 
        """
            
            if mouseHover() returns True, enabling mouse tracking
            within this column, this will be called whenever the mouse
            leaves the column.
        """
        pass
    
    def mouseClick(self,row_index,posx,posy):
        """
            Perform a mouse click on a cell
            
            if the current column wants to enable mouse clicks
            on the data within the cell this function should perform
            those actions and then return True to block further mouse
            actions by the table.
            
            the height for any row is  : self.parent.row_height
            the width for the column is: self.width
            the height of the entire column (all rows) is : self.parent.data_y2
        """
        return False
     
class LargeTable(LargeTableBase):
    """
        create a new Table, with scrollbars.
        to add this to a display, add the widget self.container
    """
    # other note-worthy methods
    # setAcceptDrops()
    def __init__(self,parent=None):
    
        super(LargeTable, self).__init__(parent)
        
        self.sbar_alwayshide_hor = False
        self.sbar_alwayshide_ver = False
        self.sbar_autohide_hor = False
        self.sbar_autohide_ver = False
        
        self.container = QWidget();
        self.sbar_hor  = QScrollBar(Qt.Horizontal)
        self.sbar_ver  = QScrollBar(Qt.Vertical)

        # organize all of the widgets and containers together
        self.vbox = QVBoxLayout(self.container)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget( self  )
        self.hbox.addWidget( self.sbar_ver  )
        self.vbox.addLayout( self.hbox )
        self.vbox.addWidget( self.sbar_hor )
        self.vbox.setSpacing(0)
        self.vbox.setMargin(0)
        self.hbox.setSpacing(0) 
        self.hbox.setMargin(0) 
        
        self.sbar_hor.setPageStep(100)
        self.sbar_hor.setSingleStep(10)
        
        self.sbar_ver.setSingleStep(1) # page step set in resize event
        #connect signals for scroll bars
        #hbar.sliderMoved.connect(hbar_update)
        self.sbar_ver.valueChanged.connect(self.sbar_move_ver)
        self.sbar_hor.valueChanged.connect(self.sbar_move_hor)
    
        self.column_header_resize.connect(self._sbar_hor_setrange)
        self.column_header_sort_request.connect(self.sortColumn)
        
        self.setAcceptDrops(True)
        
        self.menu_column_remove_index = -1;
        
        self.container.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))

    def updateTable(self,new_row_index=-1,data=None):
        """
            Cause the table to redraw all cells
            
            both arguments are optional
            
            new_row_index - move the vertical scrollbar so that this index is shown first in the table
            data - override the current data with this new 2 dimensional array
        """
        
        if data != None:
            self.data = data
            self._sbar_ver_setrange()
            
        if self.enable_last_column_expanding:
            self.columns[-1].width = self.columns[-1].preferredWidth()
            self._sbar_hor_setrange()
            
        if new_row_index >= 0:
            self.sbar_ver.setValue(new_row_index)

        self.update();
            
    def setAlwaysHideScrollbar(scrollbar_vertical,scrollbar_horizontal):
        """
            set whether the vertical or horizontal scrollbars should always
            be hidden, even if they would be needed to scroll through data
            
            this corresponds to Qt.ScrollBarAlwaysOff
            
            the default is False, and stacks with setAutoHideScrollbar
                they will be shown only when needed or all of the time
        """
        self.sbar_alwayshide_hor = scrollbar_vertical
        self.sbar_alwayshide_ver = scrollbar_horizontal
        
        if self.sbar_alwayshide_ver:
            self.sbar_ver.hide();
        else:
            self.sbar_ver.show();
            
        if self.sbar_alwayshide_hor:
            self.sbar_hor.hide();
        else:
            self.sbar_hor.show();
        
    def setAutoHideScrollbar(scrollbar_vertical,scrollbar_horizontal):
        """
            set whether the vertical or horizontal scrollbars automatically hide
            when there range becomes insignificant
            
            this corresponds to Qt.ScrollBarAsNeeded
            
            the default is True, to only show them when needed
        """
        self.sbar_autohide_hor = scrollbar_vertical
        self.sbar_autohide_ver = scrollbar_horizontal
        
    def sbar_move_ver(self,value):
        """
            action taken when the veritical scroll bar changes
        """
        self.offset_row_index = value
        
        if self.enable_last_column_expanding:
            self.columns[-1].width = self.columns[-1].preferredWidth()
            self._sbar_hor_setrange()
            
        self.update();
        
    def sbar_move_hor(self,value):
        """
            action taken when the h scroll bar changes
        """
        self.offset_col_horizontal = value
        self.update();
        
    def _sbar_ver_setrange(self):
        l = len(self.data)
        l -= self.rowCount()*3/4 # this will cause some empty rows to be drawn when scrolled down all the way
                                 # it will show between one half and up to 3/4 data, with the remaining rows empty
        l = max(0,l)
        self.sbar_ver.setRange(0,l)
        
        # note that the < 0 is so that the scroll bar is still displayed when data length = rowcount
        if self.sbar_autohide_ver and len(self.data)-self.rowCount() < 0:# and self.sbar_ver.isHidden() == False:
            self.sbar_ver.hide();
        elif self.sbar_ver.isHidden() and not self.sbar_alwayshide_ver:
            self.sbar_ver.show();
            
    def _sbar_hor_setrange(self):

        col_w = self.colWidth() 

        # the 100 s a padding for the scroll bar so that the last columns grips may be used
        if col_w > self.data_w-self.row_header_width:
            col_w += 100
        _w = max(0,col_w-self.data_w)
        
        self.sbar_hor.setRange(0,_w)
        
        if self.sbar_autohide_hor and col_w-w <=0:# and self.sbar_hor.isHidden() == False:
            self.sbar_hor.hide();
        elif self.sbar_hor.isHidden() and not self.sbar_alwayshide_hor:
            self.sbar_hor.show();

    def setData(self,data):
        self.data = data    
        l = len(data)
        
        if self.enable_last_column_expanding:
            self.columns[-1].width = self.columns[-1].preferredWidth()
        
        self._sbar_hor_setrange()

    def addColumn(self,col_index=-1,index=-1):    
        """
            Reimplementation of addColumn from LargeTableBase
            
            updates scrollbars when a column is added
        """
        super(LargeTable,self).addColumn(col_index,index)
        
        self._sbar_hor_setrange()
        
    def resizeEvent(self,event=None):
        super(LargeTable,self).resizeEvent(event)
        self.sbar_ver.setPageStep(self.rowCountFloor())
        self._sbar_hor_setrange()
        self._sbar_ver_setrange()
      
    def sortColumn(self,col_index):
        """
            col_index - column index that user clicked, requesting to sort by this column
            
            to enable sorting, call:
                dir = self.setSortColumn(col_index)
            direction will be set to either 1 or -1, and should be used
            when sorting the data list
            
            setSortColumn will automatically manage the arrow indicator, for the 
            selected column, toggling when needing, or changing to a new column
        """
        self.setSortColumn(col_index)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("data/list"):
            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("data/list"):
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):

        if event.mimeData().hasFormat("data/list"):
            data = event.mimeData().retrieveData("data/list",None)
            event.accept()
            x,y = event.pos().x(),event.pos().y()
            _ystart = self.padding_top + self.col_header_height
            row = (y-_ystart) / self.row_height # each row is row_height tall, so row calculation is easy
            row += self.offset_row_index
            self.processDropEvent(event.source(),row,data)
            self.update()
        else:
            event.ignore()

    def processDropEvent(self,source,row,data):
        """
            called when a drop happens on row 'row' with data 'data'
            the drop came from the object 'source', which is none if the
            drop came from outside the widget
            
            this method is provided for a convenience,
            without modifing any other drop functions, and setting enable drag and drop to True,
            source will always be another LargeTable and data will always be a list of elements
            that are used to format that table
        """
        #print row
        pass
        
    def wheelEvent(self,event):
        
        velocity = (event.delta()/120)*-1
        
        # out of bounds exceptions will be taken care of
        # when the value is asigned to the scroll bar
        if event.orientation() == Qt.Horizontal:
            h = self.offset_col_horizontal + velocity*10
            self.sbar_hor.setValue( h )
        else:
            v = self.offset_row_index + velocity
            self.sbar_ver.setValue( v )
   
    def mouseReleaseRightHeader(self,event):
        
        cur_r,cur_c = self.positionToRowCol(event.x(),event.y())
        self.menu_column_remove_index = cur_c
        name = self.columns[cur_c].name
        
        contextMenu = QMenu(self)
          
        rem_act = contextMenu.addAction("Hide \"%s\""%name,self._remove_column)

        contextMenu.addSeparator()

        # addAction(Qicon,QString)
        for col in self.columns_hidden:
            contextMenu.addAction("Show \"%s\""%col.name)

        action = contextMenu.exec_( event.globalPos() )
        
        if action != rem_act and action != None:
            name = action.text()
            for col in self.columns_hidden:
                if col.name in name:
                    self.columns.insert(cur_c,col)
                    self.columns_hidden.remove(col)
                    break;

        self._sbar_hor_setrange()
        
    def _remove_column(self):
        """
            takes the column at self.menu_column_remove_index
            and appends it to the columns_hidden list
        """
        if self.menu_column_remove_index != -1:
            
            col = self.columns.pop(self.menu_column_remove_index)
            self.columns_hidden.append(col)
            self.menu_column_remove_index = -1;
        
    def mouseReleaseRight(self,event):
        pass
        
    def keyReleaseEvent(self,event=None):
        """
            

        """
        #_shift = event.modifiers()&Qt.ShiftModifier == Qt.ShiftModifier     # this generates a boolean type
        
        
        # for PageUp/PageDown, Home and End i abuse the fact that setting the value of
        # the scroll bar does 2 things: range check and an update()
        if event.key() == Qt.Key_PageUp:
            self.sbar_ver.setValue(self.sbar_ver.value()-self.rowCount())
        elif event.key() == Qt.Key_PageDown:
            self.sbar_ver.setValue(self.sbar_ver.value()+self.rowCount())
        elif event.key() == Qt.Key_Home:
            self.sbar_ver.setValue(0)
        elif event.key() == Qt.Key_End:
            self.sbar_ver.setValue(len(self.data))
        elif event.key() == Qt.Key_Escape:
            self.selection = set()
            self.update()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return :
            self.keyReleaseEnter(event)
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace :
            self.keyReleaseDelete(event)
            self.update()
        elif event.key() == Qt.Key_Up:
            self.keyReleaseUp(event)
        elif event.key() == Qt.Key_Down:
            self.keyReleaseDown(event)
        else:
            self.keyReleaseOther(event)
            self.update()
            
    def keyReleaseOther(self,event):
        """
            reimplement in any subclass
            
            this is called whenever a key is pressed, but it is not handled by any
            of the cases found in keyReleaseEvent
            
            by default this method does nothing
        """
        #print "<%X=%s>"%(event.key(),event.text());
        pass
     
    def keyReleaseUp(self,event):
        """
            performs the action required when the up arrow key is pressed
            
            this automatically handles selection of table data and adjusting of the scollbar
        """
        _ctrl = event.modifiers()&Qt.ControlModifier == Qt.ControlModifier
        
        if _ctrl:
            _n = self.selection_last_row_added - 1
            _n = min(len(self.data)-1,_n)
            if self.selection_last_row_added <= self.selection_first_row_added:
                self.selection_last_row_added = _n
                self.selection |= {_n,}
            else:
                self.selection -= {self.selection_last_row_added,}
                self.selection_last_row_added = _n
                #print _n in self.selection
                if _n not in self.selection:
                    self.selection_first_row_added = _n
                    self.selection |= {_n,_n+1}
        else:
            _n = self.selection_last_row_added - 1
            _n = max(0,_n)
            self.selection_last_row_added = _n
            self.selection = {_n,}
        if _n < self.sbar_ver.value():
            self.sbar_ver.setValue(_n)  # triggers update
        else:
            self.update()
    
    def keyReleaseDown(self,event):
        """
            performs the action required when the down arrow key is pressed
            
            this automatically handles selection of table data and adjusting of the scollbar
        """
        
        _ctrl = event.modifiers()&Qt.ControlModifier == Qt.ControlModifier
        
        if _ctrl:
            _n = self.selection_last_row_added + 1
            _n = min(len(self.data)-1,_n)
            if self.selection_last_row_added >= self.selection_first_row_added:
                self.selection_last_row_added = _n
                self.selection |= {_n,}
            else:
                self.selection -= {self.selection_last_row_added,}
                self.selection_last_row_added = _n
                #print _n in self.selection
                if _n not in self.selection:
                    self.selection_first_row_added = _n
                    self.selection |= {_n,_n-1}
                
        else:
            _n = self.selection_last_row_added + 1
            _n = min(len(self.data)-1,_n)
            self.selection_last_row_added = _n
            self.selection = {_n,}
            
        if _n >= self.sbar_ver.value()+self.rowCountFloor()-1:
            self.sbar_ver.setValue(_n-self.rowCountFloor()+1)  # triggers update
        else:
            self.update()
    
    def keyReleaseDelete(self,event):
        """
            reimplement in any subclass
            
            clears selection by default
        """
        self.selection = set()
        self.update()
        
    def keyReleaseEnter(self,event):
        """
            reimplement in any subclass
            
            
            The following is the default behavoir without reimplementing:
            
            calls double click whenever there is data selected with:
                row = last selected row
                col = 0 
            if no data is currently selected when enter is pressed nothing happens  
        """
        if len(self.selection) > 0:
            self.mouseDoubleClick(self.selection_last_row_added,0)

class MimeData(QMimeData):
    custom_data = {}    # dictionary which houses the mimetype=>data
    custom_types= ["data/list","data/varient"] # list of supported types
    
    def retrieveData(self,mimetype,prefered):
        if mimetype in self.custom_types:
            return self.custom_data.get(mimetype,None);
        else:
            return super(MimeData,self).retrieveData(mimetype,prefered)
            
    def hasFormat (self, mimetype):
        if mimetype in self.custom_types:
            return mimetype in self.custom_data
        else:
            return super(MimeData,self).hasFormat(mimetype)
            
    def formats(self):
        f = super(MimeData,self).formats()
        for key in self.custom_data.keys():
            f.append(key)
        return f   
    
    def setList(self,list_data):
        self.custom_data["data/list"] = list_data
    
    def getList(self):
        return self.custom_data.get("data/list",None);
        
    def setVarient(self,list_data):
        self.custom_data["data/varient"] = list_data
    
    def getVarient(self):
        return self.custom_data.get("data/varient",None);
 

 
if __name__ == '__main__':

    def getData():
        data = []
        for ii in range(150):
            size = 6
            R = [()]*size
            for jj in range(size):
                R[jj] = (ii+1,jj+1)
            data.append(R)
        return data
    
    import sys
    
    app = QApplication(sys.argv)

    table = LargeTable()
    
    table.addColumn()
    table.addColumn()
    table.addColumn()
    table.addColumn()
    table.addColumn()
    table.addColumn()

    
    table.setData(getData())

    #t2 = LargeTable()
    #t2.setData(getData())
    
    w = QWidget()
    v = QHBoxLayout(w)
    v.setSpacing(0)
    v.setMargin(0)
    v.addWidget(table.container)
    #v.addWidget(t2.container)
    w.show()
    w.resize(720,320)
    
    sys.exit(app.exec_())
    
    
    #table.column(4).setTextAlign(Qt.AlignHCenter)
    #
    #def custom_paintItem(col,painter,item,x,y,w,h):
    #    """
    #        paint the data at index 'self.index', in row 'row' of
    #        the parent data array
    #        
    #        if needed this function can be overloaded to provide custom
    #        paint events.
    #        for example, overload it to draw shapes instead of text
    #        
    #        a custom paintItem function should not change the clipping regions
    #    """
    #    # for item as tuple
    #
    #    painter.fillRect(x,y,
    #                     int(min(w,col.width*(float(item[0])/100.0))),
    #                     h,
    #                     QColor(0,200,0)
    #                    )
    #    painter.drawText(x+4,y+col.parent.row_height-2,"%d/100"%(item[0]));                
    #                    
    #table.column(4).paintItem = custom_paintItem
