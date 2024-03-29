# #########################################################
# #########################################################
# File: MpScripting
# Description:
#       Functions related to the inner workings of the player
#   but not specifically for updating the gui, eg Work Functions
#   like search, and sort.
#   Specific functions pertaining to the gui, or the application
#   itself can be found in MpApplication
# -All imports are at the bottom of this doc-
# #########################################################
from PyQt4.QtCore import * 
from PyQt4.QtGui  import *

#import objgraph

import os
import random
import re
import subprocess
import ctypes
import traceback


from SystemDateTime import DateTime

def trace():
    report = ""
    
    trace = traceback.format_stack()
    trace = ''.join(trace[:-1]) # and remove the call that made the trace from the returned list

    report += str(trace).replace(', line', "\nLINE:").replace(', in', '\nMETHOD:').replace('  File', "\nFILE:")
    
    return report
    
    
def debug(string):
    """
        convenience function
        display a message to the user
    """
    MpGlobal.Window.debugMsg("\n%s"%string)    

def debugRetail(string):
    """
        convenience function
        display a message to the user
        open the debug box if it is hidden
    """
    MpGlobal.Window.debugMsg("\n%s"%string,True)   
    
def diagMessage(display,Message):
    # diagMessage(MpGlobal.DIAG_PLAYBACK,);
    if display:
        MpGlobal.Window.emit(SIGNAL("DIAG_MESSAGE"),Message)

def RetailMessage(string):
    point = MpGlobal.Window.txt_main.pos()
    point.setY( point.y() + MpGlobal.Window.txt_main.height() + 4 )
    
    #tip = QToolTip();
    
    #tip.showText(point,string)
    return;
 
def WarningMessage(message,btn1="Ok",btn2="",icon=QMessageBox.Warning):
    """
        icon can be of value:
        QMessageBox.Warning
    """
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(message)
    #    "Delete Song Confirmation", message,
     #   QMessageBox.NoButton, self)
    msgBox.addButton(btn1, QMessageBox.AcceptRole)
    if btn2 !="":
        msgBox.addButton(btn2, QMessageBox.RejectRole)

    return msgBox.exec_() == QMessageBox.AcceptRole
# ##############################################
# Create PlayList
# ##############################################

def selectByNumber(num):
    
    if num >= 0 and num <= 9:
        # build an array of all search strings
        # then select the string at the index given by the number
        s =[Settings.SEARCH_PRESET0, \
            Settings.SEARCH_PRESET1, \
            Settings.SEARCH_PRESET2, \
            Settings.SEARCH_PRESET3, \
            Settings.SEARCH_PRESET4, \
            Settings.SEARCH_PRESET5, \
            Settings.SEARCH_PRESET6, \
            Settings.SEARCH_PRESET7, \
            Settings.SEARCH_PRESET8, \
            Settings.SEARCH_PRESET9][num]
        searchSetSelection(s)

def fromGuiSetSelection():
    # get the list of selected artists
    

    MpGlobal.Window.tab_quickselect
    
    format = MpGlobal.Window.tab_quickselect.getFormat()
    qlist  = MpGlobal.Window.tab_quickselect.getQuickList()
    
    sel_list = [ data[0].lower() for data in qlist if data[1]]

    h = lambda x : [ item.strip()  for item in x.replace(',',';').replace('\\',';').replace('/',';').lower().split(';') ]
    
    if format == MpMusic.ARTIST:
        g = lambda x: x in sel_list
    else:
        g = lambda x: any( item in h(x) for item in sel_list )
    
    if len(sel_list) > 0:
        MpGlobal.Player.selCount = 0
        
        for song in MpGlobal.Player.library:
        
            if g(song[format].lower()) and song[MpMusic.RATING] >= MpGlobal.PLAYLIST_GUI_MINIMUM_RATING:
                song[MpMusic.SELECTED] = True
                
            if song[MpMusic.SELECTED] == True :
                MpGlobal.Player.selCount += 1
        UpdateStatusWidget(0,MpGlobal.Player.selCount)        
    print MpGlobal.Player.selCount
    
def insertIntoPlayList(R,pos):  

    MpGlobal.Player.playlist_insertSongList(pos,R)

    MpGlobal.Window.tbl_playlist.updateTable(-1,MpGlobal.Player.playList)
    
    UpdateStatusWidget(1,MpGlobal.Player.playlist_PlayTime())
    
    MpGlobal.Window.emit(SIGNAL("UPDATE_INFODISPLAY"),MpGlobal.Player.CurrentSong)
    

# ##############################################
# Library Operations
# ##############################################   

def buildArtistList(minimum=2,search=""):

    """
        Builds a list of each artist in the library
        This list is is displayed in the Quick Select tab
        The list contains information about each artist,
        how often they are played, number of songs
        total time spent listening to them
    """

    
    
    library = MpGlobal.Player.library
    if search != "":
        so = SearchObject(search);
        library = so.search(library)
 
    g = lambda x : [x,]
    h = lambda x : [ item.strip()  for item in x.replace(',',';').replace('\\',';').replace('/',';').split(';') ]
 
    MpGlobal.Player.quickList = buildQuickList(library,minimum,MpMusic.ARTIST,g)
    MpGlobal.Player.quickList_Genre = buildQuickList(library,0,MpMusic.GENRE,h)
    # sort the resulting list and update the quick selection tab
    MpGlobal.Window.tab_quickselect.sortData()

def buildQuickList(library,minimum,index,text_transform):

    D = {}
    #reset counters
    c_cnt=0 # song count
    c_ply=1 # total play count
    c_len=2 # total play time
    c_tme=3 # total listen time
    c_frq=4 # average frequency
    c_rte=5 # combined rating
    c_rct=6 # count of songs rated
    records = 7 # total count of records to keep
    
    for song in library:
    
        svalue = song[index] # the string value
        
        key_list = text_transform(svalue)
        
        for key in key_list :
        
            test_key = key.lower()    
            if test_key not in D  :
                D[test_key] = [0]*(records+1)
                D[test_key][records] = key # this way a case sensitive version is saved

            D[test_key][c_cnt] += 1                    
            D[test_key][c_ply] += song[MpMusic.PLAYCOUNT]   
            D[test_key][c_len] += song[MpMusic.LENGTH]
            D[test_key][c_tme] += song[MpMusic.PLAYCOUNT] * song[MpMusic.LENGTH]  
            D[test_key][c_frq] += song[MpMusic.FREQUENCY]
            D[test_key][c_rte] += song[MpMusic.RATING]  
            if song[MpMusic.RATING] > 0:
                D[test_key][c_rct] += 1
    
    R = []
    
    fav_list = Settings.FAVORITE_ARTIST 
    if index == MpMusic.GENRE:
        fav_list = Settings.FAVORITE_GENRE
        
    for i in range(len(fav_list)):
        fav_list[i] = fav_list[i].lower();
        
    for key in D:
    
        if D[key][c_cnt] >= minimum:
            S = [None]*(records+3)
            
            S[0] = D[key][records] 
            S[1] = False
            S[2] = key in fav_list
            S[3] = D[key][c_cnt]
            S[4] = D[key][c_ply]
            S[5] = D[key][c_len]
            S[6] = D[key][c_tme]
            S[7] = D[key][c_frq] / D[key][c_cnt]
            S[8] = D[key][c_rte]
            S[9] = D[key][c_rct]
            
            R.append(S)
    
    return R
    
    
def getStatistics():
    c_ply=0 # total play count
    c_len=0 # total play time
    c_frq=0
    count = len(MpGlobal.Player.library);
    
    for song in MpGlobal.Player.library:    
        c_ply += song[MpMusic.PLAYCOUNT]
        c_len += song[MpMusic.LENGTH]*song[MpMusic.PLAYCOUNT]
        c_frq += song[MpMusic.FREQUENCY]
    c_frq /= count; 
    debug( "Song Count        : %d"%count)
    debug( "Play Time         : %s"%DateTime.formatTimeDelta(c_len))   
    debug( "Play Count        : %d"%c_ply)
    debug( "Play Count (AVG)  : %s"%(c_ply/count))
    debug( "Frequency         : %d"%(c_frq))

# ##############################################
# Music Operations
# ##############################################     

def music_library_save():
    """
        save the currently loaded library
        this file is intended to cover the most usual case of loading the library
        for this reason it takes no arguments
    """
    lib=MpGlobal.Player.library
    if Settings.LIB_USE_MULTI:
        basepath = fileGetPath(MpGlobal.FILEPATH_LIBRARY)
        musicMergeSave_LIBZ(basepath,lib,Settings.SAVE_FORMAT|1);
    else:
        musicSave_LIBZ(MpGlobal.FILEPATH_LIBRARY,lib,Settings.SAVE_FORMAT|1);
        
def music_library_load():
    """
        return a library of music
        this file is intended to cover the most usual case of loading the library
        for this reason it takes no arguments
    """
    print "libload"
    print Settings.FILE_LOCATION_LIBRARY
    if Settings.LIB_USE_MULTI:
        basepath = fileGetPath(MpGlobal.FILEPATH_LIBRARY)
        return musicMergeLoad_LIBZ(basepath,Settings.LIB_MULTI)
    else:
        return musicLoad_LIBZ(MpGlobal.FILEPATH_LIBRARY)
    
def songGetAlbumIndex(song):
    """
        aggregate function to determine the album index for a song.
        this is used as part of the autoupdater for a push to version 0.4.2
    """
    
    # first try to make a new song and steal the index from that
    filepath = song[MpMusic.PATH]
    
    #print filepath
    
    # we can't do anything if the song does not exist
    if not os.path.exists(filepath):
        print "File Does Not Exist"
        return 0;
        
    # if we already have it why get it again?    
    if song[MpMusic.SONGINDEX] != 0:
        return song[MpMusic.SONGINDEX]
    
    temp = id3_createSongFromPath(filepath)
    
    i = temp[MpMusic.SONGINDEX]
    
    if i==0:
        # attempt to grab the index as the index in the sorted array
        # we will assume the file is in it's album folder for this part
        #print "PATH:"
        #print filepath
        R = os.listdir(fileGetPath(filepath));
        filename = fileGetFileName(filepath).lower();
        
        S=[];
        for item in R:
            if pathMatchExt(item):
                S.append(item);
        
        for j in range(len(S)):
            item = S[j].lower()
            if item == filename:
                i = j+1;
                break;
                
    #print "%s -> %d"%(song,i);        
    
    return i
    
def searchSetSelection(string,sel=True):
    so = SearchObject(string)
    
    MpGlobal.Player.selCount = 0
    count = 0 # total count of new songs found
    
    for song in MpGlobal.Player.library:
    
        if so.match(song):
            song[EnumSong.SELECTED] = sel
            count += 1
        
        if song[EnumSong.SELECTED] == True:
            MpGlobal.Player.selCount += 1
    
    UpdateStatusWidget(0,MpGlobal.Player.selCount)
    
    return count # return the number of songs that matched the input string.    
    
def calcScoreHistogram():
    # builds 2 histograms based of of basescore and playcount
    # then builds an accumilator array for calculating the final score of the song
    # a songs score is float(MpGlobal.Histogram[song.basescore])/MpGlobal.Histogram[-1]
    s=10000
    t=255
    if Settings.USE_HISTOGRAM == False: # histogram is disabled.
        MpGlobal.Histscre  = None
        MpGlobal.Histpcnt  = None
        MpGlobal.Histogram = None
        return
        
    MpGlobal.Histscre = [0]*(s+1)
    MpGlobal.Histpcnt = [0]*(t+1)

    for song in MpGlobal.Player.library:
        song.calcBaseScore();

        MpGlobal.Histscre[ min(s,song[ EnumSong.SPECIAL   ]  )] += 1
        MpGlobal.Histpcnt[ min(t,song[ EnumSong.PLAYCOUNT ] )] += 1

    l = len(MpGlobal.Player.library)

    accum = 0
    MpGlobal.Histogram = [0]*(s+1)
    for i in range(len(MpGlobal.Histscre)):
        accum += MpGlobal.Histscre[i]
        MpGlobal.Histogram[i] = accum
    
    for song in MpGlobal.Player.library:
        #m = min(s,song[ EnumSong.SPECIAL   ] );
        #n = min(t,song[ EnumSong.PLAYCOUNT ] );

        #_m = float(sum(MpGlobal.Histscre[:m]));
        #_n = float(sum(MpGlobal.Histpcnt[:n]));
     
        #_d = int( 1000*(_m/l) )  # percentile by score
        #_p = int( 1000*(_n/l) ) # percentile by playcount
        
        #song[ EnumSong.SCORE ] = _d
        song.calcScore(MpGlobal.Histogram)
    
    print "histogram updated"
    
@staticmethod
def SOC_getSearchDictionary():        # These methods are used in the Search Object Controller Class
    return MpMusic.D_StrToDec         # 
@staticmethod                         #  Found in ./module/Song_Search.py
def SOC_getFavoriteArtistList():      # 
    return Settings.FAVORITE_ARTIST   # They are used to extend the basic functionality of searching.
@staticmethod                         # 
def SOC_getPresetString(index):       # They must be defined as a static method
    return Settings.getPreset(index)  # 

    
# ##############################################
# time
# ############################################## 
    
def setSearchTime(): 
    dt = DateTime()
    date = dt.currentDate();
    
    MpGlobal.RecentEpochTime = dt.getEpochTime(date+" 00:00") # return seconds at start of this day
    MpGlobal.LaunchEpochTime = MpGlobal.RecentEpochTime - (14*24*60*60) # date of two weeks ago

    #MpGlobal.RecentEpochTime -= (24*60*60)
    
# ##############################################
# Initialize settings values
# ##############################################
def init_Settings_default(settingsObject):
    """
        this is called before calling ReadableDict_Load
        this way the dimensions (or other values) are preset
        to meaningful value for the user, other than hardcoded values
    """
    geometry = QDesktopWidget().screenGeometry()

    settingsObject.SCREEN_POSITION_X = geometry.width()/4
    settingsObject.SCREEN_POSITION_Y = geometry.height()/4
    settingsObject.SCREEN_POSITION_W = geometry.width()/2
    settingsObject.SCREEN_POSITION_H = geometry.height()/2
    settingsObject.OS=os.name;
  
def init_Settings(release):
    """
        Create the settings object,
        when created settings are set to dummy values
        if a setting needs to be initialized to some other value
        set that here
        
        it is assumed that ReadableDict_Load() was called before this function
    """
    
    Settings.RELEASE = release;
    
    setSearchTime()

    if not release:
        #MpGlobal.NAME = "ConsolePlayer - Test"
        Settings.SCREENSAVER_ENABLE_CONTROL = False

    if os.name != Settings.OS:
        debugPreboot("Last Save was on Different OS - %s Now %s"%(Settings.OS,os.name))

    if not release:
        Settings.VERSION = MpGlobal.VERSION    
        ReadableDict_Save(MpGlobal.FILEPATH_SETTINGS,Settings)
        pass
    else:
        MpGlobal.DIAG_PLAYBACK = False
        
    MpGlobal.NAME = "ConsolePlayer - v%s"%MpGlobal.VERSION
    print MpGlobal.NAME
    
    Settings.VERSION = MpGlobal.VERSION
    
    MpGlobal.updatePaths()
     
    import sip
    MpGlobal.debug_preboot_string = "   Version %s Platform %s PyQt: %s Sip: %s \n%s" % \
        (Settings.VERSION,Settings.OS.upper(),PYQT_VERSION_STR,sip.SIP_VERSION_STR,MpGlobal.debug_preboot_string) 
    del sip
    
# ##############################################
# Settings Update
# ##############################################

def settings_get_Update():
    """
        certain values in the settings object may not be updated
        as they change, these values will need to be retreived 
        before a settings dictionary can be saved.
        In Addition, these settings may only exist after everything
        has been loaded, so these values may not be able to set to true default
        values until loading is done
    """
    # ----------------------------------------------------------------
    Settings.PLAYER_VOLUME = MpGlobal.Player.getVolume();
    
    Settings.PLAYER_LAST_INDEX = MpGlobal.Player.CurrentIndex
    
    Settings.SCREEN_POSITION_W = MpGlobal.Window.width()
    Settings.SCREEN_POSITION_H = MpGlobal.Window.height()
    Settings.SCREEN_POSITION_X = MpGlobal.Window.x()
    Settings.SCREEN_POSITION_Y = MpGlobal.Window.y()
    
    # set constraints on settings which would be saved
    geometry = QDesktopWidget().screenGeometry()
    w = geometry.width()
    h = geometry.height()
    
    if Settings.SCREEN_POSITION_W > w:
        Settings.SCREEN_POSITION_W = geometry.width()/2
    if Settings.SCREEN_POSITION_H > h:   
        Settings.SCREEN_POSITION_H = geometry.height()/2

    xw = w - Settings.SCREEN_POSITION_W
    xh = h - Settings.SCREEN_POSITION_H
 
    if Settings.SCREEN_POSITION_X > xw:
        Settings.SCREEN_POSITION_X = xw
    if Settings.SCREEN_POSITION_X < 0:
        Settings.SCREEN_POSITION_X = 0
        
    if Settings.SCREEN_POSITION_Y > xh:
        Settings.SCREEN_POSITION_Y = xh
    if Settings.SCREEN_POSITION_Y < 0:
        Settings.SCREEN_POSITION_Y = 0
    # ----------------------------------------------------------------
    Settings.LIB_COL_ID     = MpGlobal.Window.tab_library.table.columns_getOrder()
    #Settings.LIB_COL_ACTIVE = MpGlobal.Window.tab_library.table.colCount  #TODO-LIB
    # windows seven can dictate screen relestate without Qt realizing it has been resized
    # if the window is snapped to an edge or dragged from a snap, it is considered fullscreen
    # even when not
    Settings.WINDOW_MAXIMIZED = MpGlobal.Window.isMaximized()
    if Settings.SCREEN_POSITION_W < 0.90*geometry.width():
        Settings.WINDOW_MAXIMIZED = False
 
def update_StrToDec_Dict():
    """
        This is called after loading the settings
        this allows the user to reset the .words for searching.
    """
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_ALBUM     ] = MpMusic.ALBUM;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_ARTIST    ] = MpMusic.ARTIST;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_COMMENT   ] = MpMusic.COMMENT;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_DAY       ] = MpMusic.DATESTAMP;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_FREQ      ] = MpMusic.FREQUENCY;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_GENRE     ] = MpMusic.GENRE;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_LENGTH    ] = MpMusic.LENGTH;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_PLAYCOUNT ] = MpMusic.PLAYCOUNT;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_PATH      ] = MpMusic.PATH;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_RATING    ] = MpMusic.RATING;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_SKIPCOUNT ] = MpMusic.SKIPCOUNT;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_TITLE     ] = MpMusic.TITLE;

    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_DATEEU ] = MpMusic.SPEC_DATEEU;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_DATEUS ] = MpMusic.SPEC_DATEUS;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_DATESTD] = MpMusic.SPEC_DATESTD;
    
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_YEAR]      = MpMusic.YEAR;
    MpMusic.D_StrToDec[Settings.SEARCH_FIELD_DATEADDED] = MpMusic.DATEADDED;        
      
# ##############################################
# 
# ##############################################
    
def UpdateStatusWidget(index,varient):
    """ update the widget on the status bar at index
        value may not be text
    """
    if index == 0:
        MpGlobal.Window.statusWidgets[0].setText("%d Songs Selected"%varient)
    if index == 1:
        MpGlobal.Window.statusWidgets[1].setText("Play Time: %s"%varient)
    if index == 2:
        MpGlobal.Window.statusWidgets[2].setText("Search Terms: %d"%varient)
    if index == 3:# file paths
        #MpGlobal.Window.statusbar
        varient = varient.replace("Discography","D~")
        varient = varient.replace("discography","D~")
        varient = varient.replace("Japanese","J~")
        MpGlobal.Window.statusWidgets[3].setText(varient)

def On_Close_Save_Data(force = False):
    settings_get_Update()   # any last minute changes to the settings
    
    ReadableDict_Save(MpGlobal.FILEPATH_SETTINGS,Settings)
    
    if MpGlobal.UNSAVED_DATA or force == True:
        
        
        #musicSave_LIBZ(MpGlobal.FILEPATH_LIBRARY,MpGlobal.Player.library,Settings.SAVE_FORMAT|1);
        music_library_save()
        
        playListSave(MpGlobal.FILEPATH_PLAYLIST_CURRENT,MpGlobal.Player.playList,Settings.SAVE_FORMAT,MpGlobal.Player.CurrentIndex);
        
        MpGlobal.UNSAVED_DATA = False
        
        MpGlobal.Window.setWindowTitle(MpGlobal.NAME)
        
        print "saved music" 

def safeClose():
    On_Close_Save_Data(True)
    MpGlobal.Application.quit()
        
def Player_set_unsaved():
    """
        set the varible indiciating that the player contains unsaved information
        indicate this to the user by updating the title bar
    """
    MpGlobal.UNSAVED_DATA = True
    l = len(MpGlobal.Player.libDelete)
    if l > 0:
        MpGlobal.Window.setWindowTitle("***%s"%MpGlobal.NAME)
    else:
        MpGlobal.Window.setWindowTitle("*%s"%MpGlobal.NAME)
 
def registerSSService():
    """
        creates a new screen saver object, if the user has separetly set screen saver enabled,
        this object will enable/disable the screensaver when playing music
        this service is platform dependent
        upon failure service is disabled entirely
        
    """
   
    if MpGlobal.SSService == None :
        try:
            if (Settings.OS == 'nt'):
                MpGlobal.SSService = ScreenSaverService()
            else:
                MpGlobal.SSService = None
                SCREENSAVER_ENABLE_CONTROL = False
                debugPreboot("***Screen Saver initialization error - 1")
        except Exception as e:
            
            MpGlobal.SSService = None
            SCREENSAVER_ENABLE_CONTROL = False
            debugPreboot("***Screen Saver initialization error - 0");
            debugPreboot("VLC instance Error: %s"%(e.args));
            
    return  MpGlobal.SSService != None

def getApplicationIcons():

    MpGlobal.pixmap_Song      = QPixmap(getStyleImagePath("app_drag.png"))
    MpGlobal.icon_None        = QIcon(getStyleImagePath("blank.png")) 
    MpGlobal.icon_Folder      = QIcon(getStyleImagePath("app_folder.png"))
    MpGlobal.icon_Music       = QIcon(getStyleImagePath("app_blank.png"))
    MpGlobal.icon_Clear       = QIcon(getStyleImagePath("app_blank.png"))
    MpGlobal.icon_Trash       = QIcon(getStyleImagePath("app_trash.png"))
    MpGlobal.icon_AutoPL      = QIcon(getStyleImagePath("app_btn_autoON.png"))
    MpGlobal.icon_AutoPLO     = QIcon(getStyleImagePath("app_btn_autoOFF.png"))  
    MpGlobal.icon_AutoPLS     = QIcon(getStyleImagePath("app_btn_autoSAME.png"))  
    MpGlobal.icon_AutoPL1     = QIcon(getStyleImagePath("app_btn_autoONE.png"))  
    MpGlobal.icon_Check       = QIcon(getStyleImagePath("app_check.png"))  
    MpGlobal.icon_volume      = QIcon(getStyleImagePath("app_volume.png"))  
    MpGlobal.icon_volumeOOF   = QIcon(getStyleImagePath("app_volume_OOF.png"))  
    MpGlobal.icon_save        = QIcon(getStyleImagePath("app_save.png"))  
    MpGlobal.icon_open        = QIcon(getStyleImagePath("app_open.png"))  
    MpGlobal.icon_file        = QIcon(getStyleImagePath("app_file.png"))  
    MpGlobal.icon_quick       = QIcon(getStyleImagePath("app_quick.png"))  
    MpGlobal.icon_note        = QIcon(getStyleImagePath("app_note.png"))  
    MpGlobal.icon_favpage     = QIcon(getStyleImagePath("app_favpage.png"))  

def get_md5(filepath):
        block_size=(1<<12);
        if os.path.exists( filepath ):
            md5 = hashlib.md5()
            rf = open(filepath ,"rb")
            while True:
                data = rf.read(block_size)
                if not data:
                    break
                md5.update(data)
            rf.close();
            return "%s"%md5.hexdigest()
        else:
            return ""     
     
def getInstallPath(forcehome=False):
    """
        Return the path that the application is installed in
        Assume first that it is installed localled
        Then assume it is installed to the appdata folder
        
        application is installed if a settings.ini file exists
        if that file does not exist then return no path
    """
    
    _localname_ = "user"   
    _appdataname_ = "ConsolePlayer"
    
    arg0path = fileGetPath(sys.argv[0])
    
    #path = os.path.join(os.getcwd(),_localname_,"");
    path = os.path.join(arg0path,_localname_,"");
    file = os.path.join(path,"settings.ini");
    if os.path.exists(file):
        debugPreboot("Install Path: %s"%path)
        return path
    
    # getenv('USERPROFILE') returns C:/Users/Nick/ or /home/nick/
    if isPosix: # get a global directory to save to
        home = os.getenv("HOME")
    else:
        home = os.getenv("APPDATA")
    
    
    if home != None and ((not "-devmode" in sys.argv) or "--install=home" in sys.argv): #only use global install path when not developing
        path = os.path.join(home,_appdataname_,"");
        file = os.path.join(path,"settings.ini");
        if os.path.exists(file):
            debugPreboot("Install Path: %s"%path)
            return path
        
    return "";

def getStyleImagePath(filename):
    """
        returns the path to the named image
        if it is not found in the current style
        then use the default image icon from /images instead
    """
    path = os.path.join(MpGlobal.installPath,"style",Settings.THEME,"images",filename);
    if not os.path.exists(path):
        newpath = os.path.join(MpGlobal.installPath,"images",filename);
        if not os.path.exists(newpath):
            return os.path.join(MpGlobal.installPath,"images","blank.png");
        else:
            return newpath
    return path
     
    
# ##############################################
# Others
# ##############################################

def stringCustomReplace(string,old,new=""):
    """
        TODO: delete me - this is from the days of no python experience
        Quick and dirty custom replace function that repeatedly calls
        replace until no instance of old exists
    """
    # used in Search Object, when we have text:
    #   +    XXXXX
    #  and  i want to remove all spaces without regex
    while old in string:
        string = string.replace(old,new)
    return string
 
def setAlt():
    import os
    for x in MpGlobal.Player.library:
        if not os.path.exists(x[MpMusic.PATH]):
            x[MpMusic.SPECIAL] = True

def RunTime_List_Operation_Int(R,index):

    if type(R[0][index]) == int:
        value = 0   # total count
        var = 0     # standard deviation
        
        for x in R:
            value += x[index]
            var += float(x[index]*x[index]);
        normal = value/len(R)
        
        var = ((var/float(len(R)-1)) - (normal*normal))**0.5
        # find standard deviation
        #for x in R:
        #    var += (x[index] - normal)**2
        #var /= (len(R)-1)
        #var = var**.5
        var = int(var)
        debug("N, Value, Normal, STDDEV = %d, %d,%d,%d | >=%d <=%d"%(len(R),value,normal,var,normal-var,normal+var))
        return (len(R),value,normal,var)
    return (0,0,0,0)
            
def listRemoveElements(data,sel):
        """ Warning this removes the given elements from the data array
            It is up to the user to update the table
        """
        for element in sel:
            for i in range(len(data)):
                if element == data[i]:
                    data.pop(i)
                    break;
                    
def getSelection(unselect = True):
    # return an array of all selected elements, and unselect by default
    # these elements
    if MpGlobal.Player.selCount == 0 :
        return []
    R = [[]]*MpGlobal.Player.selCount
    i = 0;
    time = DateTime.now() - 60*60*24
    for song in MpGlobal.Player.library:
        if song[MpMusic.SELECTED] and not song.banish :
        
            if MpGlobal.PLAYLIST_SKIP_RECENT and song[MpMusic.DATEVALUE] >= time:
                # if skip recent is enabled remove them from the selection.
                    song[MpMusic.SELECTED] = False
                    MpGlobal.Player.selCount -= 1
            else:    
                R[i] = song
                i += 1

                if unselect :
                    song[MpMusic.SELECTED] = False
                    MpGlobal.Player.selCount -= 1
                
    MpGlobal.Window.emit(SIGNAL("UPDATE_STATUSBAR"),0,MpGlobal.Player.selCount)
    
    MpGlobal.PLAYLIST_SKIP_RECENT = False
    
    return R[:i]
 
def info_UpdateCurrent():
    info_UpdateDisplay(MpGlobal.Player.CurrentSong);
    
def info_UpdateDisplay(song):
    obj = MpGlobal.Window.dsp_info
    if song == None:
        obj.text_time = ""
        obj.text_playcount = ""
        obj.text_artist = ""
        obj.text_title = "Select a Song to Play"
        obj.text_album = "Drag and Drop music to Load"
        obj.text_index = "-/-"
        obj.text_date = ""
        obj.int_rating = 0
        obj.int_freq = 0
        obj.stopScrolling()
        obj.update()
    else:
        obj.text_playcount = str(song[MpMusic.PLAYCOUNT])
        obj.text_artist = song[MpMusic.ARTIST]
        obj.text_title = song[MpMusic.TITLE]
        obj.text_album = song[MpMusic.ALBUM]
        obj.int_rating = song[MpMusic.RATING]
        obj.int_freq = song[MpMusic.FREQUENCY]
        obj.text_date = song[MpMusic.DATESTAMP]
        obj.text_index = "%d/%d"%(MpGlobal.Player.CurrentIndex+1,len(MpGlobal.Player.playList))
        obj.setScrolling()
        obj.update()
        
        d = DateTime().daysElapsed(song[MpMusic.DATESTAMP])
        if (d > 0) :
            obj.text_date += " {%d}"%( d )
  
def setConsoleColor(hex_color="",counter=0):
    """
        hex_color as #RRGGBB
        sets the bg color of the main console
    """
    if len(hex_color) != 7:
        hex_color = MpGlobal.Window.style_dict["theme_very_dark"].name()
    
    MpGlobal.Window.txt_main.setStyleSheet("background: "+hex_color+";")

    if counter > 0:
        MpGlobal.Console_State_Counter = counter;

def ReadableDocs(fptr):
    """
        this function treats the white space infront of the
        first word as tabbing and removes equavalent white space
        from each line in the string.
        e.g. the two tabs before each line in this docstring
            would be removed, the additional tabing on this line
            will be preserved.
        fptr        Function PoinTeR, function to extract __doc__ 
                    information from
    """
    newline=""
    for c in fptr.__doc__:
        if c in ' \n':
            newline+=c
        else: break
    if newline != "":
        return fptr.__doc__.strip().replace(newline,"\n");
    return fptr.__doc__;        

def stringToHTMLString(string):
    # look for a table to format
    # i am lazy. i want tables to have a new row for each line,
    # and to have | separate each section
    
    table_start = "<table>"
    table_end   = "</table>"
    
    # in the comment string, html symbols must be escaped.
    # this way i dont have to escape the html symbols for normal printing
    string = string.replace("<","&lt;").replace(">","&gt;")
    string = string.replace("\\&lt;","<").replace("\\&gt;",">")
    string = string.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    
    while (string.find(table_start) >= 0 and string.find(table_end  ) > 0 ):
        #
        #    lazy implement the following string into an html table
        #    
        #    one  | two  | tre
        #    four | five | six
        #
        s = string.find(table_start)
        e = string.find(table_end  )

        if ( s >= 0 and s < len(string) and e >= 0 and e < len(string)) :
            table = string[s+len(table_start):e].strip()
            
            table = "<tr><td>" + table.replace("\n","</td></tr><tr><td>") + "</td></tr>"
            table = table.replace("|","</td><td>")
            
            # the html tags here CANNOT match table_start or table_end
            table = "<table border=\"1\">"+table+"< /table >"
            
            string = string[:s] + table + string[e+len(table_end):]
        
    return string.replace("\n","<br>")
    
def HTMLString_StyleHeader(html):
    """
        set the first line in the string to a header format for display
        in a rich text Format.
        input should be an html-formated "Rich Text" string
        new lines should already be converted to <br> tags
    """
    
    html = html.replace("<br>","</font><br>",1);
    return "<font size=\"5\">"+html

def versionCompare(ver,const):
    """
        Return negative if ver  < const
        return  0       if ver == const
        return positive if ver  > const
    """
    if not 3 == ver.count('.') == const.count('.'): # if an invalid version format
        return -10000;
        
    a,b,c,d = ver.split('.')
    w,x,y,z = const.split('.')
    
    m = 1000 * cmp(int(a)-int(w),0) 
    n = 100  * cmp(int(b)-int(x),0) 
    o = 10   * cmp(int(c)-int(y),0) 
    p = 1    * cmp(int(d)-int(z),0)
    
    return m+n+o+p
    
def bitSet(value,bit):
    """
        returns the value with bit or'd in
       
    """
    return value|bit;
    
def bitClear(value,bit):
    """
        returns the value with bit cleared
       
    """
    return value&(~bit);    

# ##############################################
# Session Arguments
# ##############################################        
def session_send_arguments(port):    
# create copy two
    print "Creating Secondary Socket"
    sock = LocalSocket_send(port);
    msg = ""
    
    if len(sys.argv) == 2:
        # send just a file path
        sock.send(sys.argv[1])
    elif len(sys.argv) > 2:
        # send all command line options
        R= sys.argv[1:]
        msg = ""
        for string in R:
            msg += string+" "    
        if msg != "":    
            sock.send(msg) 

def session_receive_argument(message):
    # so formats.
    # support passing a file path
    # support passing a 
    
    message = message.strip();
    
    if message[:2] == '-c':
        cmd = message[2:].strip();
        print "COMMAND: %s"%message
        processTextInput(cmd)
        
    elif message[0] != '-': # should be a file path not a command option
        print "PLAY: %s"%message
        if os.path.isfile(message) and pathMatchExt(message):
            song = id3_createSongFromPath(message)
            MpGlobal.Player.playState = MpMusic.PL_NO_PLAYLIST
            if MpGlobal.Player.load(song) :
                MpGlobal.Player.play()  
        

# ##############################################
# testbench
# ##############################################        
        
def testbench_build_library():
    library = []
    time = DateTime.now()
    for i in range(30):
        song=Song("C:/Folder%d/Artist%d/Title%d.mp3"%(i,i,i))
        song[MpMusic.ARTIST]    = u"%dArtist The Band"%(i%10) # id will have 10 different A,B,T
        song[MpMusic.TITLE]     = u"%dTitle of The Song"%(i%10)  
        song[MpMusic.ALBUM]     = u"%dMonthly Album"%(i%10) 
        song[MpMusic.GENRE]     = (u"ROCK",u"POP","ALT")[(i%3)]
        song[MpMusic.DATEVALUE] = time - (60*60*24*i)# each song is one day older
        song[MpMusic.DATESTAMP] = DateTime.formatDateTime(song[MusicContainer.DATEVALUE])
        song[MpMusic.COMMENT]   = ""
        song[MpMusic.RATING]    = i%6   # in 30 songs, 5 of each rating value
        song[MpMusic.LENGTH]    = 15*i
        song[MpMusic.SONGINDEX] = 0
        song[MpMusic.PLAYCOUNT] = i
        song[MpMusic.SKIPCOUNT] = i
        song[MpMusic.FILESIZE]  = 0
        song[MpMusic.FREQUENCY] = 2*i
        song[MpMusic.BITRATE]   = 0
        song[MpMusic.SPECIAL]   = False
        song[MpMusic.SELECTED]  = False
        
        song.update()

        library.append(song)
    return library;
    
def testbench_Run_Test(testnum,lib,search,t_exp,l_exp):
    strf_term = u"\n%s:\n%s\n *** Expected %d Terms, instead found %d."
    strf_list = u"\n%s:\n%s\n *** Expected %d songs, instead found %d."
    
    so = SearchObject();
    error=0
    so.compile(search)                                # 1 term,  5 songs, rte = 3
    
    print "TEST: %d - '%s'"%(testnum,so._original);
    
    if so.termCount != t_exp: 
        print strf_term%(so._original,so,t_exp,so.termCount)
        error += 1
    lst = so.search(lib)
    
    if len(lst) != l_exp: 
        print strf_list%(so._original,so,l_exp,len(lst))
        error += 2;
      
    #if error == 0:
        
    return lst;
    
def testbench_search(testLib):
    so = SearchObject();
    tindex = 1;
    
    

    testbench_Run_Test(tindex,testLib,".rte  =3",  1,  5); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".rte < 3",  1, 15); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".rte > 3",  1, 10); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".rte <=3",  1, 20); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".rte >=3",  1, 15); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".len  =60",  1, 1); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".len <=60",  1, 5); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".art artist",  1, 30); tindex+=1;
    testbench_Run_Test(tindex,testLib,".art =1art" ,  1,  3); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,"Artist \"of the\" Month",  3, 30); tindex+=1;
    
    testbench_Run_Test(tindex,testLib,".art artist,; .alb album; .ttl title",  3, 30); tindex+=1;
    
    # date = testLib[4][MpMusic.DATESTAMP]
    # dt1 = ".date %s;"%date[:7]
    # dt2 = ".date <%s;"%date[:7]
    # 
    # testbench_Run_Test(tindex,testLib,dt1,  1, 15); tindex+=1;
    # testbench_Run_Test(tindex,testLib,dt2,  1, 15); tindex+=1;
    # 
    #  dt1 = ".date %s;"%date[:10]
    #  dt2 = ".date <%s;"%date[:10]
    #  
    #  testbench_Run_Test(tindex,testLib,dt1,  1, 25); tindex+=1;
    #  testbench_Run_Test(tindex,testLib,dt2,  1, 5);  tindex+=1;
    #      
    print "All Search Test Completed"
# ###################################################################
# ###################################################################
#
# Imports
#
# ###################################################################
# ###################################################################


from MpGlobalDefines import *

from Song_Object import Song
from Song_LibraryFormat import *
from Song_PlaylistFormat import *
from datatype_hex64 import *


from ReadableDictionary_FileFormat import *
from SystemPathMethods import *
from Song_MutagenWrapper import *
from UnicodeTranslate import Translate
from MpEventHook import initHook,disableHook
from dialogSettings import SettingsWindow
from MpScreenSaver import *
from MpStartUp import verifyInstallation  
from MpSort import *
from Song_Search import *
from Song_MutagenWrapper import *
from MpSocket_Thread import *





        