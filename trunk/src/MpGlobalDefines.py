
# #########################################################
# #########################################################
# File: MpGlobalDefines
#
# Description:
#       Defines a series of objects, and then a single
#   instance of each object at the end of this file
#   These are the global containers for variables pertaining
#   to the media player.
#   There are three groups of containers:
#    1. Settings are found in the SettingsContainer
#    2. Music, and playback related variables
#           are found in the MusicContainer
#    3. Misc enumerations, and global objects are found
#           in the RecordContainter
# #########################################################

from Song_Object import *  

class SettingsContainer(object):
    def __init__(self):
        self.DEVMODE = False
        self.RELEASE = False
        self.OS      = "" # 'posix', 'nt', 'mac', 'os2', 'ce', 'java', 'riscos'.
        self.SCREENSAVER_ENABLE_CONTROL = False
        self.MEDIAKEYS_ENABLE = False;
        self.SCREEN_POSITION_X = 0
        self.SCREEN_POSITION_Y = 0
        self.SCREEN_POSITION_W = 0
        self.SCREEN_POSITION_H = 0
        self.PLAYER_LAST_INDEX = 0  # index in the playlist to resume from
        self.WINDOW_MAXIMIZED = True
        self.PLAYER_VOLUME = 50     # plaback volume
        self.PLAYLIST_SIZE_DEFAULT = 50 # size to make playlist, by default
        self.SEARCH_PRESET0 = ".day +>14;"    # default quick search options
        self.SEARCH_PRESET1 = ""
        self.SEARCH_PRESET2 = ".pcnt <2;"
        self.SEARCH_PRESET3 = ""
        self.SEARCH_PRESET4 = ".rte >=4;"
        self.SEARCH_PRESET5 = ""
        self.SEARCH_PRESET6 = "+freq>;+freq=;.pcnt >1;" # "below average songs" (where 'below' is greater than average, and lower than average is 'higher'
        self.SEARCH_PRESET7 = ""
        self.SEARCH_PRESET8 = ""
        self.SEARCH_PRESET9 = ""
        self.FAVORITE_ARTIST = []   # array of unicode artist names
        self.FAVORITE_GENRE  = []   # array of unicode genre names
        self.LIB_COL_ID = []
        self.LIB_COL_ACTIVE=-1;

        self.SEARCH_FIELD_ALBUM     = "alb"
        self.SEARCH_FIELD_ARTIST    = "art"
        self.SEARCH_FIELD_COMMENT   = "comm"
        self.SEARCH_FIELD_DAY       = "day"
        self.SEARCH_FIELD_FREQ      = "freq"
        self.SEARCH_FIELD_GENRE     = "gen"
        self.SEARCH_FIELD_LENGTH    = "len"
        self.SEARCH_FIELD_PLAYCOUNT = "pcnt"
        self.SEARCH_FIELD_PATH      = "path"
        self.SEARCH_FIELD_RATING    = "rte"
        self.SEARCH_FIELD_SKIPCOUNT = "scnt"
        self.SEARCH_FIELD_TITLE     = "ttl"
        self.SEARCH_FIELD_DATEEU    = "dateeu"
        self.SEARCH_FIELD_DATEUS    = "dateus"
        self.SEARCH_FIELD_DATESTD   = "date"
        self.SEARCH_FIELD_YEAR      = "year"
        self.SEARCH_FIELD_DATEADDED = "added"

        self.PLAYLIST_SIDE = 1 # 1==right, 0==left
        self.POSIX_VLC_MODULE_PATH='/usr/lib/vlc'
        self.DRIVE_ALTERNATE_LOCATIONS=[] #'/home/nick/windows/D_DRIVE'
        self.FILE_LOCATION_LIBRARY='' #when  empty str, not in use, otherwise path to an alternate library file

        self.THEME = "default"
        self.USE_CUSTOM_THEME_COLORS = False
        self.SAVE_FORMAT=0
        #self.RELATIVE_DRIVE_PATH="%RELATIVE%" # any string or %RELATIVE%
        self.LOG_HISTORY = False
        self.SAVE_BACKUP = False
        self.SEARCH_STALL = 300;  # 175 is once every ms 2.6*175 = f*x
        self.KEYBOARD_PLAYPAUSE   = 179
        self.KEYBOARD_STOP        = 178
        self.KEYBOARD_PREV        = 177
        self.KEYBOARD_NEXT        = 176
        self.KEYBOARD_LAUNCHMEDIA = 181
        #self.KEYBOARD_INSERT      = 45
        self.VERSION = "0.0.0.0" # dummy value set in GlobalContainer
        self.SIGIL = '.'    # single character to act as sigil

    def getPreset(self,index):
        return (self.SEARCH_PRESET0,
                self.SEARCH_PRESET1,
                self.SEARCH_PRESET2,
                self.SEARCH_PRESET3,
                self.SEARCH_PRESET4,
                self.SEARCH_PRESET5,
                self.SEARCH_PRESET6,
                self.SEARCH_PRESET7,
                self.SEARCH_PRESET8,
                self.SEARCH_PRESET9)[index];

class GlobalContainer(object):
    Window = None
    Application = None
    AudioPlayer = None
    Player = None
    EventHandler = None;
    PlayerThread = None
    HookManager = None
    SocketThread = None     # used for session lock and socket communication
    SSService = None # screen saver service object
    #QOUTPUT  = None

    t1=0;
    t2=0;
    PrintFrame = False #: # TODO: Remove, debug of search frame only

    installPath = "";

    debug_preboot_string = "Console Player Initializing..."

    # ###############################################
    # Program Variables
    # ###############################################
    VERSION = "0.0.0.0" # fourth value in version auto updates in init_Settings
    SAVED_VERSION = "0.0.0.0"
    MINIMUM_VERSION = "0.5.3.0" # hardcoded value to compare against,
    NAME = "Console Player"

    SONGDATASIZE  = 22#MusicContainer.NUMTERM; #length of array to use
    FILESAVE_VERSIONID = 4      # deprecated


    PLAYLIST_ARTIST_HASH_SIZE = 0
    PLAYLIST_GUI_MINIMUM_RATING = 0
    PLAYLIST_SKIP_RECENT = False        # on playlist creation skip songs played recently
    PLAYLIST_SIZE = 50
    Hiragana = None # tables of characters
    Katakana = None

    LaunchEpochTime = 0
    RecentEpochTime = 0

    SplitterWidthMax = 400 # max,min size for the playlist widget
    SplitterWidthMin = 200 #

    SEARCH_MINSTRINGLENGTH = 1
    SEARCH_AUTOAPPEND = ""
    # #############################
    # Boolean States
    # #############################
    # when blank input into the text box should mean play song zero
    INPUT_PLAY_GOTO_ZERO = False
    # whether data has been modified since the last save
    UNSAVED_DATA = False
    # whether to create a new playlist automatically when the current one finishes
    PLAYLIST_END_CREATE_NEW = 1
    PLAYLIST_END_STOP       = 2
    PLAYLIST_END_LOOP_SAME  = 4
    PLAYLIST_END_LOOP_ONE   = 8
    PLAYLIST_END_POLICY = PLAYLIST_END_CREATE_NEW
    # when set to true the secondary thread will start loading songs found in the external list
    ENABLE_MUSIC_LOAD = False

    Console_State_Counter = 0;
    # #############################
    # Default Icons
    icon_None    = None
    icon_Folder  = None
    icon_Music   = None
    icon_Clear   = None
    icon_Trash   = None
    icon_AutoPL  = None
    icon_AutoPLO = None
    icon_AutoPLS = None
    icon_AutoPL1 = None
    icon_Check   = None
    icon_volume    = None
    icon_volumeOOF = None
    icon_save = None
    icon_open = None
    icon_file = None
    icon_note = None
    icon_quick = None
    # search prompt
    SEARCH_PROMPT = u"Search Library <Ctrl+L>"

    FILEPATH_LIBRARY_SYNC_NAME = "sync.libz"
    FILEPATH_LIBRARY_NAME      = "music.libz"

    FILEPATH_PLAYLIST_CURRENT  = "" # "playlist/current.playlist"
    FILEPATH_LIBRARY           = "" # "music.library"
    FILEPATH_SETTINGS          = "" # "settings.ini"
    FILEPATH_ICON              = "" # 'icon.png'
    FILEPATH_VOLUMEICON        = "" # app_volume_icon.png
    FILEPATH_HISTORY           = "" # "history.log"
    FOLDERPATH_BACKUP          = ""
    # diag messages, set to true to see diag feedback from the named
    # areas of the application
    DIAG_PLAYBACK  = True
    DIAG_KEYBOARD  = False
    DIAG_SEARCH    = False
    DIAG_SONGMATCH = False

    Force_Backup = False

    last_gui_newplaylist_string = ""

    SAVE_FORMAT_NOCOMP  = 1  # no compression
    SAVE_FORMAT_CWD     = 2  # drive will always be CWD

    getGenreTags = lambda x : [ item.strip()  for item in x.replace(',',';').replace('\\',';').replace('/',';').split(';') ]
    
    def updatePaths(self,newPath=''):
        # example use
        # # # Settings.FILE_LOCATION_LIBRARY = ""
        # # # MpGlobal.updatePaths()

        # it is very important that before calling this function
        # to verify that newPath exists

        # newpath is of format:
        # %APPDATA#\ConsolePlayer\
        # .\user\
        if newPath != '':
            self.installPath = newPath

        pl_dir_1 = os.path.join(Settings.FILE_LOCATION_LIBRARY, "playlist", "")
        #pl_dir_2 = os.path.join(self.installPath, "playlist", "")

        if os.path.exists(pl_dir_1):
            self.FILEPATH_PLAYLIST_CURRENT = os.path.join(Settings.FILE_LOCATION_LIBRARY,"playlist/current.playlist")
        else:
            self.FILEPATH_PLAYLIST_CURRENT = os.path.join(self.installPath,"playlist/current.playlist")

        if Settings.FILE_LOCATION_LIBRARY != '':
            self.FILEPATH_LIBRARY      = os.path.join(Settings.FILE_LOCATION_LIBRARY,self.FILEPATH_LIBRARY_NAME)
        else:
            self.FILEPATH_LIBRARY      = os.path.join(self.installPath,self.FILEPATH_LIBRARY_NAME)

        self.FILEPATH_SETTINGS         = os.path.join(self.installPath,"settings.ini")
        self.FILEPATH_HISTORY          = os.path.join(self.installPath,"history.log")

        self.FILEPATH_ICON = os.path.join(self.installPath,"icon.png")
        
        self.FOLDERPATH_BACKUP = os.path.join(self.installPath,"backup")
     
class MusicContainer(EnumSong):
    """
        This class extends EnumSong to provide more functionality with working with song info.
        
        it also provides some enumaeration for playing songs, searching for songs, etc.
    """

    # #############################
    # Direction Modifiers
    LESSTHAN    = 0x22
    EQUAL       = 0x21
    GREATERTHAN = 0x24
    CONTAINS    = 0x28
    LTEQUAL = EQUAL | LESSTHAN
    GTEQUAL = EQUAL | GREATERTHAN

    # #############################
    # Type Modifiers
    CONST = 0
    NOT = 1
    OR  = 2
    AND = 4

    # Media State enumeration
    NOTHINGSPECIAL = 0
    OPENING = 1
    BUFFERING = 2
    PLAYING = 3
    PAUSED = 4
    STOPPED = 5
    ENDED = 6
    ERROR = 7
    UNKOWN = 8

    #Playback Mode States
    PL_PLAYLIST_CONSECUTIVE = 1
    PL_PLAYLIST_RANDOM = 2
    PL_NO_PLAYLIST = 4
    AUTO_SIGNAL_ISSUED = False; # solves a bug with threads/queueing in phonon

    #define a dictionary for converting str types to integers
    # TODO in the future, allow the user to modify this list
    # this is the official abreviation list
    D_StrToDec = {   'alb'           : EnumSong.ALBUM, \
                     'abm'           : EnumSong.ALBUM, \
                     'added'         : EnumSong.DATEADDED, \
                     'album'         : EnumSong.ALBUM, \
                     'art'           : EnumSong.ARTIST, \
                     'artist'        : EnumSong.ARTIST, \
                     'ban'           : EnumSong.BANISH, \
                     'banish'        : EnumSong.BANISH, \
                     'bitrate'       : EnumSong.BITRATE, \
                     'comm'          : EnumSong.COMMENT, \
                     'comment'       : EnumSong.COMMENT, \
                     'day'           : EnumSong.DATESTAMP, \
                     'dateval'       : EnumSong.DATEVALUE, \
                     'exif'          : EnumSong.EXIF, \
                     'size'          : EnumSong.FILESIZE, \
                     'freq'          : EnumSong.FREQUENCY, \
                     'gen'           : EnumSong.GENRE, \
                     'len'           : EnumSong.LENGTH, \
                     'path'          : EnumSong.PATH, \
                     'pcnt'          : EnumSong.PLAYCOUNT, \
                     'playcount'     : EnumSong.PLAYCOUNT, \
                     'rte'           : EnumSong.RATING, \
                     'rate'          : EnumSong.RATING, \
                     'rating'        : EnumSong.RATING, \
                     'sel'           : EnumSong.SELECTED, \
                     'scnt'          : EnumSong.SKIPCOUNT, \
                     'skipcount'     : EnumSong.SKIPCOUNT, \
                     'id'            : EnumSong.SONGID, \
                     'index'         : EnumSong.SONGINDEX, \
                     'spec'          : EnumSong.SPECIAL, \
                     'dateeu'        : EnumSong.SPEC_DATEEU, \
                     'dateus'        : EnumSong.SPEC_DATEUS, \
                     'date'          : EnumSong.SPEC_DATESTD, \
                     "month"         : EnumSong.SPEC_MONTH, \
                     "week"          : EnumSong.SPEC_WEEK, \
                     'ttl'           : EnumSong.TITLE, \
                     'tit'           : EnumSong.TITLE, \
                     'title'         : EnumSong.TITLE, \
                     'year'          : EnumSong.YEAR
                    }

    def expandExifMacro(self,string,sigil,song):
        """
            Expand a string macro based of a template song,
            eg given a sigil of '$':
            replace all instances of '$art' in str with the artist name of song
        """
        if song == None:
            return string

        s = unicode(string)
        for key,value in self.D_StrToDec.items():
            if value == self.SONGID:
                s = s.replace(sigil+key,str(song.id));
            elif value < self.NUMTERM: # value is an array index
                s = s.replace(sigil+key,str(song[value]));
        return s;

def debugPreboot(str):
    """
        a debug function for printing to the debug text box in the player
        this function stores all messages to a string buffer
        when the program is done initializing, the data is passed to the
        text box
    """
    MpGlobal.debug_preboot_string += "\n" + str

# ###################################################################
# ENUMERATION
# ###################################################################
class COMMAND(object):
    VALID    = "prompt_valid"
    UNKNOWN  = "prompt_warn"
    WARN     = "prompt_error"
    ERROR    = "prompt_unknown"
    SPECIAL  = "prompt_spec"


# ###################################################################
# Instantiate
# ###################################################################



MpGlobal = GlobalContainer()
MpMusic  = MusicContainer()
Settings = SettingsContainer()

# ###################################################################
# Import C DLL
# currently highly experimental - and not included in the project
# ###################################################################

import os
isPosix = os.name == 'posix'

MpTest = None
if os.path.exists("./MpTest.dll") and not isPosix:
    # load test functions from C++ dll.
    # maybe someday i can find a good use for this right now
    MpTest = ctypes.cdll.LoadLibrary('./MpTest.dll')

    MpTest.systest1.argtypes = [ctypes.c_int,ctypes.c_char_p]
    MpTest.systest1.restype  = ctypes.c_byte

    MpTest.systest2.argtypes = [ctypes.c_int,]

    MpTest.fcopy.argtypes   = [ctypes.c_char_p,ctypes.c_char_p]
    MpTest.fcopy.restype  = ctypes.c_byte

    MpTest.fdelete.argtypes = [ctypes.c_char_p,]
    MpTest.fdelete.restype  = ctypes.c_byte


