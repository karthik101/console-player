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
 

# ##############################################
# Create PlayList
# ##############################################
def createPlayList(size,autoLoad = False, autoStart = False, clrsel = True):
    """
        Create anew playlist using the songs selected.
        Playlist is then displayed and playback can begin
    """
    # autoLoad, load the song when finished
    # autoStart, start playing the first song when done
    

    R = getSelection(clrsel)
    S = createPlayListFromSongSet(R,size,MpGlobal.PLAYLIST_ARTIST_HASH_SIZE)
    
    registerNewListAsPlayList(S,autoLoad,autoStart)
    
def registerNewListAsPlayList(songList,autoLoad = False, autoStart = False):
    """
        Given a list of songs, set that as the new playlist
        autoLoad and autoStart specify whether to load or play the zero song immediatly
    """
    MpGlobal.Player.playList = songList
    MpGlobal.Window.dsp_info.text_index = "-/%d"%len(songList)
    MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),MpGlobal.Window.dsp_info.update())    
    MpGlobal.Window.tbl_playlist.UpdateTable(0,MpGlobal.Player.playList)
    
    if autoLoad and not autoStart:
        MpGlobal.Player.loadNoPlayback(MpGlobal.Player.getPlayListIndex(0))
        MpGlobal.Player.CurrentIndex = 0;
    # start playing the song immediatley, or wait for the current song to
    # finish playing then start the new playlist
    if autoStart :
        MpGlobal.Player.playSong(0)
    else:
        MpGlobal.INPUT_PLAY_GOTO_ZERO = True
     
    UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())

    # update the time used when comparing songs played since two weeks.
    setSearchTime() 
    
    playListSave(MpGlobal.FILEPATH_PLAYLIST_CURRENT,MpGlobal.Player.playList,Settings.SAVE_FORMAT)
    if Settings.SAVE_BACKUP:
        musicBackup(MpGlobal.Force_Backup);
    
def createPlayListFromSongSet(songSet,size,hashValue = 0):
    """
        Return a list of songs of length size, suitable for use as a new playlist
        Pool of songs used is taken from songSet, obvously this set will normally be the
        set of selected songs, taken by using getSelection()
        hashValue allows for a limit to be placed on the number of songs per artist, or 0 for no limit
        
    """
    S = [] # resulting list
    
    if len(songSet) == 0:
        return []
    # ###############################
    # add to selection from gui
    ShuffleList(songSet)

    size = min(size,len(songSet)) # length of the playlist to return
    if hashValue > 0:  
        # create a hash table and count the songs per artist
        # limit the max number of somgs per artist to the hash number
        D = {}
        S = []
        for song in songSet:
            a = song[MpMusic.ARTIST]
            
            if a in D:
                D[a] += 1
            else:
                D[a] = 1
                
            if D[a] <= hashValue:
                S.append(song)
                
            if len(S) == size:
                break;
        # shuffle again, because the above searches linearly until
        # end of list, which could group similar artists together
        ShuffleList(S)
    else:
        S = songSet[:size]
        
    return S
    
def createFromPlayList(size,index,shuffle=True, hash=0):
    """
        create a playlist from a playlist open in an editor, then play the first song
        
    """
    
    if index < len(MpGlobal.Window.editorTabs):
    
        R = MpGlobal.Window.editorTabs[index][3].DataSrc
        
        if shuffle :
            ShuffleList(R)
        
        if hash > 0:  
            # create a hash table and count the songs per artist
            # limit the max number of somgs per artist to the hash number
            D = {}
            MpGlobal.Player.playList = []
            for song in R:
                a = song[MpMusic.ARTIST]
                
                if a in D:
                    D[a] += 1
                else:
                    D[a] = 1
                    
                if D[a] <= hash:
                    MpGlobal.Player.playList.append(song)
                    
                if len(MpGlobal.Player.playList) == size:
                    break;
            # shuffle again, because the above searches linearly until
            # end of list, which could group similar artists together
            if shuffle :
                ShuffleList(MpGlobal.Player.playList)
        else:
            MpGlobal.Player.playList = R[:size]
        
        MpGlobal.Window.tbl_playlist.UpdateTable(0,MpGlobal.Player.playList)
        
        MpGlobal.Player.playSong(0)

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
    R = []
    for data in MpGlobal.Player.quickList:
        if data[1]:
            R.append(data[0])
            data[1] = False
    MpGlobal.Window.tbl_quicklist.FillTable(0)
    if len(R) > 0:
        MpGlobal.Player.selCount = 0
        for song in MpGlobal.Player.library:
            if song[MpMusic.ARTIST] in R and song[MpMusic.RATING] >= MpGlobal.PLAYLIST_GUI_MINIMUM_RATING:
                song[MpMusic.SELECTED] = True
                
            if song[MpMusic.SELECTED] == True :
                MpGlobal.Player.selCount += 1
        UpdateStatusWidget(0,MpGlobal.Player.selCount)        

def insertSelectionIntoPlayList(size,pos,random = False):

    R = getSelection(False)
    S = createPlayListFromSongSet(R,size,MpGlobal.PLAYLIST_ARTIST_HASH_SIZE)

    #TODO ALLOW SHUFFLE OF REGION pos to end    
    #if random == True:
    #    ShuffleList(MpGlobal.Player.playList)
    
    insertIntoPlayList(S,pos);
    
def insertIntoPlayList(R,pos):  

    MpGlobal.Player.playList = MpGlobal.Player.playList[:pos] + R + MpGlobal.Player.playList[pos:]

    MpGlobal.Window.tbl_playlist.UpdateTable(MpGlobal.Window.tbl_playlist.getDisplayOffset(),MpGlobal.Player.playList)
    
    UpdateStatusWidget(1,MpGlobal.Player.playListPlayTime())
    
    MpGlobal.Window.emit(SIGNAL("UPDATE_INFODISPLAY"),MpGlobal.Player.CurrentSong)
    

# ##############################################
# Library Operations
# ##############################################   

def buildArtistList(minimum=2):

    """
        Builds a list of each artist in the library
        This list is is displayed in the Quick Select tab
        The list contains information about each artist,
        how often they are played, number of songs
        total time spent listening to them
    """

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
    
    for song in MpGlobal.Player.library:
    
        key = song[MpMusic.ARTIST]
        
        if key not in D:
            D[key] = [0]*records

        D[key][c_cnt] += 1                    
        D[key][c_ply] += song[MpMusic.PLAYCOUNT]   
        D[key][c_len] += song[MpMusic.LENGTH]
        D[key][c_tme] += song[MpMusic.PLAYCOUNT] * song[MpMusic.LENGTH]  
        D[key][c_frq] += song[MpMusic.FREQUENCY]
        D[key][c_rte] += song[MpMusic.RATING]  
        if song[MpMusic.RATING] > 0:
            D[key][c_rct] += 1
    
    R = []
    
    for key in D:
    
        if D[key][c_cnt] >= minimum:
            S = [None]*(records+3)
            
            S[0] = key
            S[1] = False
            S[2] = key in Settings.FAVORITE_ARTIST
            S[3] = D[key][c_cnt]
            S[4] = D[key][c_ply]
            S[5] = D[key][c_len]
            S[6] = D[key][c_tme]
            S[7] = D[key][c_frq] / D[key][c_cnt]
            S[8] = D[key][c_rte]
            S[9] = D[key][c_rct]
            
            R.append(S)

    k = lambda song: sort_parameter_str(song,0)

        
    R.sort(key = k, reverse=False )
    
    MpGlobal.Player.quickList = R
    MpGlobal.Window.tbl_quicklist.UpdateTable(0,MpGlobal.Player.quickList)
    
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
    debug( "Play Time         : %s"%convertTimeToString(c_len))   
    debug( "Play Count        : %d"%c_ply)
    debug( "Play Count (AVG)  : %s"%(c_ply/count))
    debug( "Frequency         : %d"%(c_frq))

# ##############################################
# Music Operations
# ##############################################     

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
    
# ##############################################
# time
# ############################################## 
 
def getEpochTime( date ):
    """return epoch time for a date"""
    datetime = None
    try:
        datetime = time.strptime(date,"%Y/%m/%d %H:%M")
        return timegm(datetime)   
    except:
        pass
        
    return 0

def getFormatDate( unixTime ):
    
    try:
        return time.strftime("%Y/%m/%d %H:%M", time.localtime(int(unixTime))) 
    except:
        pass
        
    return "1970/01/01 00:00"
        
def getCurrentTime():
    """return seconds since epoch"""
    return timegm(time.localtime(time.time()))
    
def getNewDate():
    """return a new formatted time string"""
    datetime = time.localtime(time.time())
    return time.strftime("%Y/%m/%d %H:%M",datetime)

def normalizeDateFormat(date,format):
    """
        provide an autocomplete function for
        predicting the date based off the format expected,
        and what the user has already input
    """
    current_year  = str(datetime.date.today().year) # OK RIGHT HERE, FUCK EVERYTHING ABOUT PYTHON AND THIS MODULE.
                                               # year is an attr of datetime.date but not accessible, and today is not OBVIOUS
    
    date = date.replace("\\","/")
    date = date.replace(" ","")
    
    R = date.split('/')
    
    for i in range(len(R)-1,-1,-1): # remove empty fields
        if R[i] == '':
            R.pop(i)
            
    l = len(R) # for determining how many fields are missing
    
    if l < 1 :
        return ""
        
    if format == MpMusic.SPEC_DATESTD:
        if l == 1:
            R.append("01") # append month
        if l < 3 :  
            R.append("01") # append  day
        if len(R[2]) == 1: R[2] =  "0"+R[2];  
        if len(R[1]) == 1: R[1] =  "0"+R[1];  
        if len(R[0]) == 1: R[0] =  "0"+R[0];
        if len(R[0]) == 2: R[0] = "20"+R[0];
    else:
        if l == 1:
            R.append("01") # append day or month
        if l < 3 :  
            R.append(current_year) # append cyear
            
        if len(R[0]) == 1: R[0] =  "0"+R[0];   
        if len(R[1]) == 1: R[1] =  "0"+R[1];  
        if len(R[2]) == 1: R[2] =  "0"+R[2];
        if len(R[2]) == 2: R[2] = "20"+R[2];
    
    date = R[0]+"/"+R[1]+"/"+R[2] # reconstruct the date format   
    if len(date) != 10 :
        return ""   # if the user put to many numbers in one of the fields
    return date
    
def getSecondsFromDateFormat(date,format):    
    """
        format as: SPEC_DATEEU, SPEC_DATEUS SPEC_DATESTD
        There are three basic formats a user can type the date in
        either ISO standard, US custom, or European custom
        The user needs to tell the program which to expect, and even
        then a wide variety of formats can be given, 
        YY or YYYY 
        d or dd
        m or mm
        knowing which format to expect, we can exptrapolate or plug in default
        values, and then parse the UNIX time code from that,
        return 0 if we cant figure out the input
    """
    # assume as input, 'xxxx/xx/xx' , 'xx/xx/xx' , 'xx/xx/xxxx'
    # use the format to determine how to parse this
    
    # repair xx,xxxx,xx/xx,xxxx/xx,xx/xx/xx to full string parameters
    
    date = normalizeDateFormat(str(date),format)

    if date == '':
        return 0
        
    dateFormat = "%Y/%m/%d"
    if format == MpMusic.SPEC_DATEEU:
        dateFormat = "%d/%m/%Y"
    elif format == MpMusic.SPEC_DATEUS:
        dateFormat = "%m/%d/%Y"
        
    datetime = None

    try:
        datetime = time.strptime(date,dateFormat)
        return timegm(datetime)   
    except:
        pass
        
    return 0
        
def setSearchTime(): 
    MpGlobal.RecentEpochTime = getCurrentTime()
    MpGlobal.LaunchEpochTime = MpGlobal.RecentEpochTime - (14*24*60*60)
    MpGlobal.RecentEpochTime -= (24*60*60)

# ##############################################
# Settings
# ##############################################
def init_Settings_default():
    """
        some values need default values incase they do not exist in the settings file that is laoded
    """
    geometry = QDesktopWidget().screenGeometry()

    Settings.SCREEN_POSITION_X = geometry.width()/4
    Settings.SCREEN_POSITION_Y = geometry.height()/4
    Settings.SCREEN_POSITION_W = geometry.width()/2
    Settings.SCREEN_POSITION_H = geometry.height()/2
    Settings.OS =os.name;
    
def init_Settings(release):
    """
        Create the settings object,
        when created settings are set to dummy values
        if a setting needs to be initialized to some other value
        set that here
        
        it is assumed that loadSettings() was called before this function
    """
    
    Settings.RELEASE = release;
    
    setSearchTime()

    

    if not release:
        #MpGlobal.NAME = "ConsolePlayer - Test"
        Settings.SCREENSAVER_ENABLE_CONTROL = False

    if os.name != Settings.OS:
        debugPreboot("Last Save was on Different OS - %s Now %s"%(Settings.OS,os.name))

    if not release:
        # calculate the new build number
        #(a,b,c,build1) = MpGlobal.VERSION.split('.') # version set internally
        #(p,s,t,build2) = Settings.VERSION.split('.') # the last saved version

        #if (c != t or b != s or a != p): # if higher version numbers change, reset build number
        #   import VersionController
        #   MpGlobal.VERSION = VersionController.ResetBuildNumber() 
        #   del VersionController\
        
        # update the settings and save the new version number, it has changed
        # version number is 1 + the value saved in VersionController
        # version controller has already had the value incremented by one, and saved
        # it must nowbne saved again in the settings for other use.
        Settings.VERSION = MpGlobal.VERSION    
        saveSettings()
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
    Settings.LIB_COL_ID     = MpGlobal.Window.tbl_library.col_id[:]
    Settings.LIB_COL_ACTIVE = MpGlobal.Window.tbl_library.colCount
    # windows seven can dictate screen relestate without Qt realizing it has been resized
    # if the window is snapped to an edge or dragged from a snap, it is considered fullscreen
    # even when not
    Settings.WINDOW_MAXIMIZED = MpGlobal.Window.isMaximized()
    if Settings.SCREEN_POSITION_W < 0.90*geometry.width():
        Settings.WINDOW_MAXIMIZED = False

def update_StrToDec_Dict(): #TODO this function does no belong here
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
    
    saveSettings()
    
    if MpGlobal.UNSAVED_DATA or force == True:
        
        
        musicSave_LIBZ(MpGlobal.FILEPATH_LIBRARY,MpGlobal.Player.library,Settings.SAVE_FORMAT);
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
        MpGlobal.Window.setWindowTitle("*%s - Warning"%MpGlobal.NAME)
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

# ##############################################
# Others
# ##############################################

def load_music_from_dir(dir):
    """
        recursively open directorys and load all valid songs
    """
    D = []
    if os.path.isdir(dir):
        R = os.listdir(dir)
        for file in R:
            path = os.path.join(dir,file)
            if pathMatchExt(path) and pathIsUnicodeFree(path):
                MpGlobal.Player.external.append(path)
            if os.path.isdir(path):
                D.append(path)
    if len(D) > 0:
        MpGlobal.Application.processEvents()    #prevents hanging
        for dir in D:
            load_music_from_dir(dir)

def stringSplit(string,deliminator=" "):
    """
        Custom string split function
        splits  strings/unicode strings at deliminator list
        deliminator is a string containing a list of all characters to ignore
        string will be split into tokens and array of all tokens will be returned
        ex:
            deliminator=",;"
            string = "a,b;c,;"
            return ['a','b','c']
    """
    R = []
    n = ''
    l=0
    i=0
    while i < len(string):
        if string[i] in deliminator:
            n = string[l:i]
            if n != "":
                R.append(n)
            l = i+1
        i += 1
        
    n = string[l:i] # aquire the last term if any
    if n != "":
        R.append(n)
        
    return R

def stringCustomReplace(string,old,new=""):
    """
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
    time = getCurrentTime() - 60*60*24
    for song in MpGlobal.Player.library:
        if song[MpMusic.SELECTED] :
        
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
    
def clearSelection():
    MpGlobal.Player.selCount = 0
    for x in range(len(MpGlobal.Player.library)):
        MpGlobal.Player.library[x][MpMusic.SELECTED] = False
    UpdateStatusWidget(0,MpGlobal.Player.selCount)    
    MpGlobal.Window.emit(SIGNAL("FILL_LIBRARY")) 

def startNewPlaylist(forceStart = False):
    """
        Start playing the playlist (assumed to be recently created)
        from the first song.
        
        Parameters:
        
        forceStart : When true the first song will be played
                     if false, or not specified the player will
                     check against stopNext to see if playback should
                     continue
    """
    clearSelection()
    
    MpGlobal.PLAYLIST_SIZE = Settings.PLAYLIST_SIZE_DEFAULT
    MpGlobal.PLAYLIST_ARTIST_HASH_SIZE = 0
    MpGlobal.Player.stopIndex = -1
    MpGlobal.INPUT_PLAY_GOTO_ZERO = False
    
    if MpGlobal.Player.stopNext == False or forceStart == True:
        MpGlobal.Player.playSong(0)
    else:
        MpGlobal.Player.loadNoPlayback(0)
        MpGlobal.Player.setStopNext(False)
 
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
        obj.setScrolling()
        obj.update()
  
def convertTimeToString( t ):

    day =  t/86400
    our = (t%86400)/3600
    min = (t%3600)/60
    sec = (t%60)

    if (sec< 10):
        sec = ":0%d"%sec
    else:
        sec = ":%d"%sec
    if (min< 10):
        min = "0%d"%min
    else:
        min = "%d"%min  
        
    if our > 0 or day > 0:
        if (our< 10):
            our = "0%d:"%our
        else:
            our = "%d:"%our
    else:
        our = ""
    if day > 0 :
        day = "%d:"%day
    else:   
        day = ""

    return "%s%s%s%s"%(day,our,min,sec)

def convertStringToTime(string):
    string = string.replace(" ","")
    R = string.split(':');
    sec = R[-1];
    min = "0";
    our = "0";
    day = "0";
    
    if len(R) > 1:
        min = R[-2];
    if len(R) > 2:
        our = R[-3];
    if len(R) > 3:
        day = R[-4];
    
    h = int(our) + 24*int(day)
    m = int(min) + 60*h
    s = int(sec) + 60*m
    
    return s
    
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
    
    
def atoi(a):
    """
        converts string to int by taking only the first integer
        in the string.
    """
    i = "";
    R = ('0','1','2','3','4','5','6','7','8','9');
    #a = str(a)
    for j in range(len(a)):
        if a[j] in R:
            i += a[j];
        else:
            break;
    try:
        return int(i);
    except:
        return 0;
 
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
# Session
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
        
    else:
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
    time = getCurrentTime();
    for i in range(30):
        song=Song("C:/Folder%d/Artist%d/Title%d.mp3"%(i,i,i))
        song[MpMusic.ARTIST]    = u"%dArtist The Band"%(i%10) # id will have 10 different A,B,T
        song[MpMusic.TITLE]     = u"%dTitle of The Song"%(i%10)  
        song[MpMusic.ALBUM]     = u"%dMonthly Album"%(i%10) 
        song[MpMusic.GENRE]     = (u"ROCK",u"POP","ALT")[(i%3)]
        song[MpMusic.DATEVALUE] = time - (60*60*24*i)# each song is one day older
        song[MpMusic.DATESTAMP] = getFormatDate(song[MusicContainer.DATEVALUE])
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
        song[MpMusic.EXIF] = createInternalExif(song);
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

from PyQt4.QtCore import * 
from PyQt4.QtGui  import *

#import objgraph

from calendar import timegm
import os
import time
import datetime
import random
import re
import subprocess
import ctypes

from MpGlobalDefines import *
from MpSong import Song
from datatype_hex64 import *
from MpFileAccess import *
from MpID3 import *
from UnicodeTranslate import Translate
from MpEventHook import initHook,disableHook
from dialogSettings import SettingsWindow
from MpScreenSaver import *
from MpFirstTime import verifyInstallation  
from MpSort import *
from MpSearch import *
from MpID3 import *
from MpSocket import *





        