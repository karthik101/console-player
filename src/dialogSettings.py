
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from MpGlobalDefines import *
from MpSong import Song
from datatype_hex64 import *
from MpFileAccess import fileGetPath,load_css,css_save_dict
from Qt_CustomStyle import *

#from widgetDialog import *

class SettingsWindow(QDialog):
    
    def __init__(self,parent):
    #Qt.WindowModal
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.tabbar = QTabWidget(self)
        self.tab_app    = VPage(self)
        self.tab_search = VPage(self)
        self.tab_style  = VPage(self)
        
        self.container = QVBoxLayout(self)
        
        self.container.setSpacing(0)
        self.setFixedHeight(400)
        
        self.init_tab_app()
        self.init_tab_search()
        self.init_tab_style()
        
        # add widgets to scroll areas after initializing them

        self.tabbar.addTab(self.tab_app, "Application")
        self.tabbar.addTab(self.tab_search, "Search Preset")
        self.tabbar.addTab(self.tab_style, "Theme")
        
        self.hbox_dia = QHBoxLayout()
        self.btn_accept = QPushButton("Save & Close")
        self.btn_cancel = QPushButton("Cancel")
        self.hbox_dia = QHBoxLayout()
        self.hbox_dia.addWidget(self.btn_accept)
        self.hbox_dia.addWidget(self.btn_cancel)
        self.btn_accept.setFixedWidth(128)
        self.btn_cancel.setFixedWidth(128)
        
        self.container.addWidget(self.tabbar)
        self.container.addLayout(self.hbox_dia)
        
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_accept.clicked.connect(self.accept)
        
        self.setData_app()
        self.setData_search()
        self.setData_style()
    
    def init_tab_app(self):
    
        self.grid_app = QGridLayout()
        self.grid_app.setRowMinimumHeight(0,20)
        self.grid_app.setRowMinimumHeight(1,20)
        self.grid_app.setColumnStretch (0,10)
        
        
        self.chk_SScontrol = QCheckBox("Disable Screen Saver during playback",self)
        self.chk_Mediakeys = QCheckBox("Enable Media Keys",self)
        
        self.box_save = QGroupBox('Save Format',self)
        self.vbox_save = QVBoxLayout(self.box_save)
        self.box_save.setLayout(self.vbox_save)  
        self.chk_normal  = QRadioButton("Normal Mode",self.box_save)
        self.chk_multiOS  = QRadioButton("Multi OS Mode",self.box_save)
        self.chk_multiOS.setToolTip("Drives will be deteremined at run time, and OS specific checks will be made to find the music")
        lbl_OSPrompt = QLabel("Use When Running on a flashdrive, or\nwhen the library file could be accessed by a\nseparate Windows/Linux installation.")
        self.vbox_save.addWidget(self.chk_normal);
        self.vbox_save.addWidget(self.chk_multiOS);
        self.vbox_save.addWidget(lbl_OSPrompt);
        
        
        
        self.chk_liblocal = QCheckBox("Use Alternate library file location:",self)
        self.hbox_liblocal = QHBoxLayout();
        self.edit_liblocal = QLineEdit(self);
        self.edit_liblocal.setDisabled(True);
        
        self.btn_liblocal = QPushButton('...',self);
        self.btn_libload  = QPushButton('Load',self);
        self.btn_liblocal.clicked.connect(self.get_liblocal_path)
        self.btn_libload.clicked.connect(self.get_liblocal_load)
        
        self.hbox_liblocal.addSpacing(24)
        self.hbox_liblocal.addWidget(self.edit_liblocal)
        self.hbox_liblocal.addWidget(self.btn_liblocal)
        self.hbox_liblocal.addWidget(self.btn_libload)
        #self.chk_relDrive  = QRadioButton("Flash Drive Mode",self)
        #self.chk_relDrive.setToolTip("Player will assume all media is contained on a flashdrive and on the same drive as the Executable")
        self.chk_history  = QCheckBox("Log History",self)
        
        
        
        self.grid_app.addWidget(self.chk_SScontrol,0,0,1,3,Qt.AlignLeft|Qt.AlignTop)
        self.grid_app.addWidget(self.chk_Mediakeys,1,0,1,3,Qt.AlignLeft|Qt.AlignTop)
        self.grid_app.addWidget(self.box_save     ,2,0,1,3,Qt.AlignLeft|Qt.AlignTop)

        #self.grid_app.addWidget(self.chk_relDrive ,4,0,Qt.AlignLeft|Qt.AlignTop)
        #self.grid_app.addWidget(QLabel("Use this setting only if your music collection \nexists on the same drive as the application."),4,1,Qt.AlignLeft|Qt.AlignTop)
        self.grid_app.addWidget(self.chk_liblocal ,4,0,    Qt.AlignLeft|Qt.AlignTop)
        self.grid_app.addLayout(self.hbox_liblocal,5,0,1,3,Qt.AlignLeft|Qt.AlignTop)
        self.grid_app.addWidget(self.chk_history  ,6,0,1,2,Qt.AlignLeft|Qt.AlignTop)

        
        info = QLabel("Application wide settings...")
        info.setWordWrap(True)
        info.setFixedHeight(20)
        self.tab_app.addWidget(info)
        
        if not Settings.DEVMODE:
            self.chk_history.setDisabled(True)
            self.chk_history.hide()
        
        self.tab_app.addLayout(self.grid_app)
        
    def init_tab_search(self):
        self.editSearch=[]
        
        self.grid_search = QGridLayout()
        self.grid_search.setColumnMinimumWidth(0,70)
    
        for i in range(10):
            self.editSearch.append(QLineEdit())
            self.editSearch[i].setFixedWidth(300)
            self.grid_search.addWidget(QLabel("Preset %d:"%i),i,0,Qt.AlignLeft)
            self.grid_search.addWidget(self.editSearch[i],i,1,Qt.AlignRight)

            #self.tab_search.addLayout(t.layout)  
        info = QLabel("Presets allow you to quickly build a new playlist out of matching songs.\nAny search parameter can be used.\nTo use, type the number of a preset into the console,\nthen press enter to make a new playlist")
        info.setWordWrap(True)
        self.tab_search.addWidget(info)
        self.tab_search.addLayout(self.grid_search)

    def init_tab_style(self):

        
        self.cbox_theme = QComboBox(self)
        self.cbox_theme.addItem("default")

        for item in loadStyleDir():
            self.cbox_theme.addItem(item)
        
        self.btn_theme = QPushButton("Apply Custom Colors",self)
        self.btn_theme_reset = QPushButton("Default Colors",self)
        
        self.scroll_tstyle = QScrollArea(self)
        
        self.style_page = VPage()

        
        
        # ----------------------------------------------------------
        self.gbox_style1 = QGroupBox("Theme Colors",self)
        
        self.grid_themecolor = QGridLayout();
        self.grid_themecolor.setColumnMinimumWidth(0,300)
 
        self.themeColors = []
        self.themeColors.append(ColorEdit(self))
        self.themeColors.append(ColorEdit(self))
        self.themeColors.append(ColorEdit(self))
        
        self.themeColors.append(ColorEdit(self))
        self.themeColors.append(ColorEdit(self))
        self.themeColors.append(ColorEdit(self))

        self.grid_themecolor.addWidget(QLabel("Primary Color"),0,0,Qt.AlignLeft)
        self.grid_themecolor.addWidget(self.themeColors[0].edit,0,1,Qt.AlignRight)
        
        self.grid_themecolor.addWidget(QLabel("Secondary Color"),1,0,Qt.AlignLeft)
        self.grid_themecolor.addWidget(self.themeColors[1].edit,1,1,Qt.AlignRight)
        
        self.grid_themecolor.addWidget(QLabel("Background Color"),2,0,Qt.AlignLeft)
        self.grid_themecolor.addWidget(self.themeColors[2].edit,2,1,Qt.AlignRight)
        
        self.grid_themecolor.addWidget(QLabel("Light Color"),3,0,Qt.AlignLeft)
        self.grid_themecolor.addWidget(self.themeColors[3].edit,3,1,Qt.AlignRight)
        
        self.grid_themecolor.addWidget(QLabel("Nuetral Color"),4,0,Qt.AlignLeft)
        self.grid_themecolor.addWidget(self.themeColors[4].edit,4,1,Qt.AlignRight)
        
        self.grid_themecolor.addWidget(QLabel("Dark Color"),5,0,Qt.AlignLeft)
        self.grid_themecolor.addWidget(self.themeColors[5].edit,5,1,Qt.AlignRight)
        
        self.gbox_style1.setLayout(self.grid_themecolor)
        
        self.gbox_style2 = QGroupBox("Text and Highlight",self)
        self.gbox_style2.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
        self.grid_textcolor = QGridLayout();
 
        self.textColors = []
        self.textColors.append(ColorEdit(self))
        self.textColors.append(ColorEdit(self))
        self.textColors.append(ColorEdit(self))
        
        self.textColors.append(ColorEdit(self))
        self.textColors.append(ColorEdit(self))
        
        self.textColors.append(ColorEdit(self))
        self.textColors.append(ColorEdit(self))
        
        self.textColors.append(ColorEdit(self))
        self.textColors.append(ColorEdit(self))

        self.spin_font = QSpinBox(self)
        self.spin_font.setMaximum(16)
        self.spin_font.setMinimum(8)
        self.spin_font.setValue(12)
        self.spin_font.setFixedWidth(55)
        
        self.cbox_font = QFontComboBox()
        self.cbox_font.setEditable(False)
        filter = QFontComboBox.ScalableFonts|QFontComboBox.MonospacedFonts|QFontComboBox.ProportionalFonts
        self.cbox_font.setFontFilters(filter)
        
        
        self.grid_textcolor.addWidget(QLabel("Font Size",self)     ,0,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.cbox_font               ,0,1,Qt.AlignRight)
        self.grid_textcolor.addWidget(self.spin_font               ,0,2,Qt.AlignRight)
                                                                   
        self.grid_textcolor.addWidget(QLabel("Text Color")         ,1,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[0].edit      ,1,2,Qt.AlignRight)
                                                                   
        self.grid_textcolor.addWidget(QLabel("Text Color - Light") ,2,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[1].edit      ,2,2,Qt.AlignRight)
                                                                   
        self.grid_textcolor.addWidget(QLabel("Text Color - Dark")  ,3,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[2].edit      ,3,2,Qt.AlignRight)
                                                                   
        self.grid_textcolor.addWidget(QLabel("Important Text 1")   ,4,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[3].edit      ,4,2,Qt.AlignRight)
                                                                   
        self.grid_textcolor.addWidget(QLabel("Important Text 2")   ,5,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[4].edit      ,5,2,Qt.AlignRight)
                                                                  
        self.grid_textcolor.addWidget(QLabel("Highlight Color")    ,6,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[5].edit      ,6,2,Qt.AlignRight)
                                                                   
        self.grid_textcolor.addWidget(QLabel("Highlight Invalid")  ,7,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[6].edit      ,7,2,Qt.AlignRight)
        
        self.grid_textcolor.addWidget(QLabel("Highlight Special 1"),8,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[7].edit      ,8,2,Qt.AlignRight)
        
        self.grid_textcolor.addWidget(QLabel("Highlight Special 2"),9,0,Qt.AlignLeft)
        self.grid_textcolor.addWidget(self.textColors[8].edit      ,9,2,Qt.AlignRight)
        
        self.gbox_style2.setLayout(self.grid_textcolor)
        
        self.style_page.addWidget(self.gbox_style1) 
        self.style_page.addWidget(self.gbox_style2) 
        
        self.scroll_tstyle.setWidget(self.style_page)
        self.scroll_tstyle.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
        
        
        #--------------------------------
        #self.test = []
        #self.test.append(ColorEdit(self))
        #self.test.append(ColorEdit(self))
        #self.test.append(ColorEdit(self))
        #self.test.append(ColorEdit(self))
        #h = QHBoxLayout()
        #h.addWidget(self.test[0].edit)
        #h.addWidget(self.test[1].edit)
        #h.addWidget(self.test[2].edit)
        #h.addWidget(self.test[3].edit)
        #self.tab_style.addLayout(h) 
        #--------------------------------
        
        
        self.tab_style.addWidget(self.cbox_theme) 
        h = QHBoxLayout()
        h.addWidget(self.btn_theme_reset)
        h.addWidget(self.btn_theme)
        
        self.tab_style.addLayout(h) 
        self.tab_style.addWidget(self.scroll_tstyle) 
        
        self.btn_theme.clicked.connect(self.getData_style)
        self.btn_theme_reset.clicked.connect(self.button_theme_setDefault)
        self.cbox_theme.currentIndexChanged.connect(self.themeChanged)
    
    def setData_app(self):

        if (Settings.SCREENSAVER_ENABLE_CONTROL):
            self.chk_SScontrol.setCheckState(Qt.Checked)
        if (Settings.MEDIAKEYS_ENABLE):    
            self.chk_Mediakeys.setCheckState(Qt.Checked)
            
        if (Settings.SAVE_FORMAT&MpGlobal.SAVE_FORMAT_CWD):
            self.chk_multiOS.setChecked(True)
        else:
            self.chk_normal.setChecked(True)   
            
        if (Settings.FILE_LOCATION_LIBRARY != ''):    
            self.chk_liblocal.setChecked(True)
            self.edit_liblocal.setText(Settings.FILE_LOCATION_LIBRARY);
           
            
        if (Settings.LOG_HISTORY):
            self.chk_history.setCheckState(Qt.Checked)   
        #if (Settings.RELATIVE_DRIVE_PATH!="%RELATIVE%")
        
    def setData_search(self):
        self.editSearch[0].setText(Settings.SEARCH_PRESET0)
        self.editSearch[1].setText(Settings.SEARCH_PRESET1)
        self.editSearch[2].setText(Settings.SEARCH_PRESET2)
        self.editSearch[3].setText(Settings.SEARCH_PRESET3)
        self.editSearch[4].setText(Settings.SEARCH_PRESET4)
        self.editSearch[5].setText(Settings.SEARCH_PRESET5)
        self.editSearch[6].setText(Settings.SEARCH_PRESET6)
        self.editSearch[7].setText(Settings.SEARCH_PRESET7)
        self.editSearch[8].setText(Settings.SEARCH_PRESET8)
        self.editSearch[9].setText(Settings.SEARCH_PRESET9)
        self.editSearch[0].setCursorPosition(0)
        self.editSearch[1].setCursorPosition(0)
        self.editSearch[2].setCursorPosition(0)
        self.editSearch[3].setCursorPosition(0)
        self.editSearch[4].setCursorPosition(0)
        self.editSearch[5].setCursorPosition(0)
        self.editSearch[6].setCursorPosition(0)
        self.editSearch[7].setCursorPosition(0)
        self.editSearch[8].setCursorPosition(0)
        self.editSearch[9].setCursorPosition(0)
    
    def setData_style(self,dict=None):
        if MpGlobal.Window != None:
        
            if dict == None:
                dict = MpGlobal.Window.style_dict
            
            for i in range(self.cbox_theme.count()):
                if self.cbox_theme.itemText(i) == Settings.THEME:
                    self.cbox_theme.setCurrentIndex(i)
            
            self.themeColors[0].setColor(dict["theme_p_mid"].name())
            self.themeColors[1].setColor(dict["theme_s_mid"].name())
            self.themeColors[2].setColor(dict["theme_bg_color"].name())
            self.themeColors[3].setColor(dict["theme_very_light"].name())
            self.themeColors[4].setColor(dict["theme_neutral"].name())
            self.themeColors[5].setColor(dict["theme_very_dark"].name())
    
            self.spin_font.setValue( int(dict["font_size"])  )
            self.cbox_font.setCurrentFont(QFont(dict["font_family"]))
            
            self.textColors[0].setColor(dict["text_color"].name())
            self.textColors[1].setColor(dict["text_light"].name())
            self.textColors[2].setColor(dict["text_dark"].name())
            self.textColors[3].setColor(dict["text_important1"].name())
            self.textColors[4].setColor(dict["text_important2"].name())
            self.textColors[5].setColor(dict["color_highlight"].name())
            self.textColors[6].setColor(dict["color_invalid"].name())
            self.textColors[7].setColor(dict["color_special1"].name())
            self.textColors[8].setColor(dict["color_special2"].name())
      
    def getData_app(self):
       
        Settings.SCREENSAVER_ENABLE_CONTROL = self.chk_SScontrol.checkState() == Qt.Checked
 
        Settings.MEDIAKEYS_ENABLE = self.chk_Mediakeys.checkState() == Qt.Checked
 
        #if self.chk_relDrive.isChecked():

        if  self.chk_multiOS.isChecked():
            Settings.SAVE_FORMAT = bitSet(Settings.SAVE_FORMAT,MpGlobal.SAVE_FORMAT_CWD)          
        else:
            Settings.SAVE_FORMAT = bitClear(Settings.SAVE_FORMAT,MpGlobal.SAVE_FORMAT_CWD)        
        
        if self.chk_liblocal.checkState() == Qt.Checked:    
            Settings.FILE_LOCATION_LIBRARY = self.edit_liblocal.displayText()
        else:
            Settings.FILE_LOCATION_LIBRARY = ''
        Settings.LOG_HISTORY = self.chk_history.checkState() == Qt.Checked
        
        if Settings.SCREENSAVER_ENABLE_CONTROL == True and MpGlobal.SSService == None:
        
            msgBox = QMessageBox(MpGlobal.Window)
            msgBox.setIcon(QMessageBox.Warning)
            message = "Screen Saver Failed to Initialize.\nTry Reopening the Application"
            msgBox.setText(message)
            #    "Delete Song Confirmation", message,
             #   QMessageBox.NoButton, self)
            msgBox.addButton("Ok", QMessageBox.AcceptRole)
            
            msgBox.exec_()
            MpGlobal.SSService = None
            
            Settings.SCREENSAVER_ENABLE_CONTROL = False

        if Settings.MEDIAKEYS_ENABLE:
            initHook()
        else:
            disableHook()
            
        

    def getData_search(self):
        Settings.SEARCH_PRESET0 = self.editSearch[0].text()
        Settings.SEARCH_PRESET1 = self.editSearch[1].text()
        Settings.SEARCH_PRESET2 = self.editSearch[2].text()
        Settings.SEARCH_PRESET3 = self.editSearch[3].text()
        Settings.SEARCH_PRESET4 = self.editSearch[4].text()
        Settings.SEARCH_PRESET5 = self.editSearch[5].text()
        Settings.SEARCH_PRESET6 = self.editSearch[6].text()
        Settings.SEARCH_PRESET7 = self.editSearch[7].text()
        Settings.SEARCH_PRESET8 = self.editSearch[8].text()
        Settings.SEARCH_PRESET9 = self.editSearch[9].text()
        
    def getData_style(self):  

        D = {}
        #4,and 2-tuples of colors
        cp = self.get_4Color(self.themeColors[0].color)
        cs = self.get_4Color(self.themeColors[1].color)
        cb = self.get_2Color(self.themeColors[2].color)
        
        D["theme_p_light"]    = cp[0]
        D["theme_p_mid"]      = cp[1]
        D["theme_p_dark"]     = cp[2]
        D["theme_p_vdark"]    = cp[3]
        D["theme_s_light"]    = cs[0]
        D["theme_s_mid"]      = cs[1]
        D["theme_s_dark"]     = cs[2]
        D["theme_s_vdark"]    = cs[3]
        
        D["theme_bg_color"]     = cb[0]
        D["theme_bg_color_alt"] = cb[1]
        
        D["theme_very_light"] = self.themeColors[3].color
        D["theme_neutral"]    = self.themeColors[4].color
        D["theme_very_dark"]  = self.themeColors[5].color

        D["font_size"]    = str( self.spin_font.value() )
        D["font_family"]  = self.cbox_font.currentText()
        
        D["text_color"] = self.get_Color(self.textColors[0].color)
        D["text_light"] = self.get_Color(self.textColors[1].color)
        D["text_dark"] = self.get_Color(self.textColors[2].color)
        D["text_important1"] = self.get_Color(self.textColors[3].color)
        D["text_important2"] = self.get_Color(self.textColors[4].color)
        
        
        # HL, HLOOF
        D["color_highlight"]    = self.get_ColorA(self.textColors[5].color,175)
        D["color_highlightOOF"] = self.get_ColorA(self.textColors[5].color, 75)
        
        # invalid
        D["color_invalid"] = self.get_ColorA(self.textColors[6].color,127)
        
        #special 1,2
        D["color_special1"] = self.get_ColorA(self.textColors[7].color,127)
        D["color_special2"] = self.get_ColorA(self.textColors[8].color,50)
        
        
        
        if MpGlobal.Application != None:
            # when we change fonts the play/cont button needs to be resized
            # the size of the play/cont button determines the layout management
            # of the info display to its right
           
            size = max( self.spin_font.value(), 10 )
            MpGlobal.Window.btn_playstate.setFixedHeight(size*4)
            MpGlobal.Window.btn_playstate.setFixedWidth(size*4)
            MpGlobal.Window.txt_main.setMinimumHeight(size+8)
            Settings.USE_CUSTOM_THEME_COLORS = True
            Settings.THEME = self.cbox_theme.currentText()
            css_save_dict(Settings.THEME,"user",D)
            D = load_css(Settings.THEME,MpGlobal.Application,D,True)
            MpGlobal.Window.set_colorFromCssDict(D)
                 
    def accept(self):       
        self.getData_app()
        self.getData_search()
        MpGlobal.updatePaths()  # update file save paths 
        super(SettingsWindow,self).accept()
        # a save will be performed on return to the main script
        
    def reject(self):
        super(SettingsWindow,self).reject()
        
    def button_theme_setDefault(self):
        Settings.USE_CUSTOM_THEME_COLORS = False
        Settings.THEME = self.cbox_theme.currentText()
        D = load_css(Settings.THEME,MpGlobal.Application)
        MpGlobal.Window.set_colorFromCssDict(D)
        self.setData_style()
     
    def themeChanged(self,index):
        
        newTheme = self.cbox_theme.itemText(index)
        if newTheme != Settings.THEME:
            Settings.THEME = newTheme
            
            D = {}
            
            D = load_css(Settings.THEME,MpGlobal.Application,D,Settings.USE_CUSTOM_THEME_COLORS)
        
            MpGlobal.Window.set_colorFromCssDict(D)
        
    def get_4Color(self,cstring):
        """
            returns a tupple of 4 colors, given an initial
            color formatted as #RRGGBB
            
        """
        c = hex_to_QColor(cstring)# conver the color to a QColor
        
        # pull out its color values in the HSV space
        h =  c.hue()
        s =  c.saturation()
        v =  c.value()
       
        #Adjust the brightness to create new colors
        
        c.setHsv(h,s,min(255,int(v*1.5)))
        c1 =  c.name()
        
        c.setHsv(h,s,int(v*.75))
        c3 = c.name()
        
        c.setHsv(h,s,int(v*.375))
        c4 = c.name()
        
        # return color, light, mid, dark and vdark
        return (c1,cstring,c3,c4)
    
    def get_2Color(self,cstring):
        """
            returns a tupple of 2 colors, given an initial
            color formatted as #RRGGBB
            the new color is slightly brighter than the original
            
        """
        c = hex_to_QColor(cstring)# conver the color to a QColor
        
        # pull out its color values in the HSV space
        h =  c.hue()
        s =  c.saturation()
        v =  c.value()
       
        #Adjust the brightness to create new colors
        
        c.setHsv(h,s,min(255,v+10))
        c1 = c.name()
 
        # return color, light, mid, dark and vdark
        return (cstring,c1)
        
    def get_Color(self,cstring):
        """
            given a color, and an alpha value
            creates a new color in the rgba space
            of the string format:
            rgba(r,g,b,a), a as a float 0 to 1
        """
        c = hex_to_QColor(cstring)# conver the color to a QColor
        r = c.red()
        g = c.green()
        b = c.blue()
        return "rgb(%3d,%3d,%3d)"%(r,g,b)
        
    def get_ColorA(self,cstring,alpha=255):
        """
            given a color, and an alpha value
            creates a new color in the rgba space
            of the string format:
            rgba(r,g,b,a), a as a float 0 to 1
        """
        c = hex_to_QColor(cstring)# conver the color to a QColor
        r = c.red()
        g = c.green()
        b = c.blue()
        a = str(alpha/255.0)[:5]
        return "rgba(%3d,%3d,%3d,%s)"%(r,g,b,a)
    
    def get_liblocal_path(self,event=None):
    
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "Select a Save Location",
                self.edit_liblocal.displayText(), 
                options)
        if directory:
            self.edit_liblocal.setText(directory)
            self.chk_liblocal.setChecked(True)
            
    def get_liblocal_load(self,event=None):
        print "Reloading..."
        MpGlobal.updatePaths()  # update file save paths 
        processTextInput('libload') # yay lazy
        
class ColorEdit(object):

    color = "#FF0000"
    
    def __init__(self,parent):
        #self.layout  = QHBoxLayout()
        #self.label  = QLabel(field,parent)
        
        self.edit  = QLabel(parent)
        
        
        #self.label.setFixedWidth(70)
        self.edit.setFixedWidth(55)
        self.edit.setFixedHeight(20)
        self.edit.setObjectName("ColorEditor")

        
        #self.layout.addWidget(self.label,0,Qt.AlignLeft)

        #if useAlpha :
        #    self.spin  = QSpinBox(parent)
        #    self.spin.setRange(0,255)
        #    self.spin.setValue(255)
        #    self.label2 = QLabel("Alpha: ",parent)
        #    self.layout.addWidget(self.label2  ,0,Qt.AlignRight)
        #    self.layout.addWidget(self.spin  ,0,Qt.AlignRight)
        #else:
        #    self.spin = None
        #self.layout.addWidget(self.edit  ,0,Qt.AlignRight)

        self.setColor("#ee0000")
        
        self.edit.mouseReleaseEvent = self.btnClicked
    
    def btnClicked(self,event=None):
    
        default = hex_to_QColor(self.color)
        cstring = show_ColorChooser(default)
        
        if cstring != "":
            self.setColor(cstring)
            self.color = cstring
    
    def setColor(self,cstring):
        """
            Set the background color of a widget
            using .setStyleSheet, given a color
            formatted as a string ( in legal css form )
        """
        
        # invert the text color so it is readable
        #cinvert = hex_InvertColor(cstring)
        self.edit.setStyleSheet("background: "+cstring+";")
        self.color = cstring
        #widget.setText(cstring)

def loadStyleDir():
    dir = os.path.join( MpGlobal.installPath,"style","");
    D = os.listdir(dir)
    R = []
    for file in D:
        path = os.path.join(dir,file)
        fl = file.lower()
        if os.path.isdir(path) and fl != 'default':
            R.append(file)
            
    return R
        
def show_ColorChooser(default):

    color = QColorDialog.getColor(default, None)
    if color.isValid(): 
        return color.name()
    return ""
    
def hex_to_QColor(string):
        hex = {'0':0, '1':1, '2':2, '3':3, '4':4,
           '5':5, '6':6, '7':7, '8':8, '9':9,   
           'A':10, 'B':11,'C':12, 'D':13, 'E':14, 'F':15,
           'a':10, 'b':11,'c':12, 'd':13, 'e':14, 'f':15 }
        r = hex[string[1]]*16 + hex[string[2]]
        g = hex[string[3]]*16 + hex[string[4]]
        b = hex[string[5]]*16 + hex[string[6]] 
        
        return QColor(r,g,b);
        
def hex_InvertColor(string):
    hex = {'0':0, '1':1, '2':2, '3':3, '4':4,
       '5':5, '6':6, '7':7, '8':8, '9':9,   
       'A':10, 'B':11,'C':12, 'D':13, 'E':14, 'F':15,
       'a':10, 'b':11,'c':12, 'd':13, 'e':14, 'f':15 }
    inv = {
            0:'0', 1:'1', 2:'2', 3:'3', 4:'4',
            5:'5', 6:'6', 7:'7', 8:'8', 9:'9',
            10:'A', 11:'B', 12:'C', 13:'D', 14:'E', 15:'F'
          }
    r = 255 - hex[string[1]]*16 + hex[string[2]]
    g = 255 - hex[string[3]]*16 + hex[string[4]]
    b = 255 - hex[string[5]]*16 + hex[string[6]] 
    
    if r == g == b:
        if r > 127:
            return "#000000"
        else:
            return "#FFFFFF"
    r = inv[r/16] + inv[r%16]
    g = inv[g/16] + inv[g%16]
    b = inv[b/16] + inv[b%16]
    print "#"+r+g+b
    return "#"+r+g+b    
      
      
      
from MpCommands import *  
from widgetPage import VPage
import os
from MpEventHook import *    