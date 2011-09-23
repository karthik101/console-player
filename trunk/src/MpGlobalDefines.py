
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
#    1. Settings are found in the RecordContainer
#    2. Music, and playback related variables 
#           are found in the MusicContainer
#    3. Misc enumerations, and global objects are found
#           in the RecordContainter
# #########################################################

class RecordContainer(object):
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
        self.SEARCH_PRESET6 = ""
        self.SEARCH_PRESET7 = ""
        self.SEARCH_PRESET8 = ""
        self.SEARCH_PRESET9 = ""
        self.FAVORITE_ARTIST = []   # array of unicode artist names
        
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
        
        self.POSIX_VLC_MODULE_PATH='/usr/lib/vlc'
        self.DRIVE_ALTERNATE_LOCATIONS=[] #'/home/nick/windows/D_DRIVE'
        self.FILE_LOCATION_LIBRARY='' #when  empty str, not in use, otherwise path to an alternate library file
        
        self.THEME = "default"
        self.USE_CUSTOM_THEME_COLORS = False
        self.SAVE_FORMAT=0
        #self.RELATIVE_DRIVE_PATH="%RELATIVE%" # any string or %RELATIVE%
        self.LOG_HISTORY = False
        self.SAVE_BACKUP = True
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
    PlayerThread = None
    LoadThread = None
    HookManager = None
    SSService = None # screen saver service object
    #QOUTPUT  = None

    PrintFrame = False #: # TODO: Remove, debug of search frame only

    installPath = "";
    
    debug_preboot_string = "Console Player Initializing..."

    # ###############################################
    # Program Variables
    # ###############################################
    VERSION = "0.0.0.0" # fourth value in version auto updates in init_Settings
    NAME = "Console Player - v%s"%VERSION
    SONGDATASIZEV1=10; 
    SONGDATASIZEV2=16; # length of the song array for version two
    SONGDATASIZEV3=19; # length of the song array for version three
    SONGDATASIZE  = SONGDATASIZEV3; #length of array to use
    FILESAVE_VERSIONID = 4


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

    FILEPATH_LIBRARY_SYNC_NAME = "sync.library"
    FILEPATH_LIBRARY_NAME      = "music.library"
    
    FILEPATH_PLAYLIST_CURRENT  = "" # "playlist/current.playlist"
    FILEPATH_LIBRARY           = "" # "music.library"
    FILEPATH_SETTINGS          = "" # "settings.ini"
    FILEPATH_ICON              = "" # 'icon.png'
    FILEPATH_VOLUMEICON        = "" # app_volume_icon.png
    FILEPATH_HISTORY           = "" # "history.log"
    
    # diag messages, set to true to see diag feedback from the named
    # areas of the application
    DIAG_PLAYBACK  = True
    DIAG_KEYBOARD  = False
    DIAG_SEARCH    = False
    DIAG_SONGMATCH = False

    Force_Backup = False
    
    last_gui_newplaylist_string = ""
    
    SAVE_FORMAT_NORMAL  = 0 # drive will always be the same
    SAVE_FORMAT_CWD     = 1 # drive will always be CWD
    SAVE_FORMAT_UNKNOWN = 2 # drive will be unkown at start
    
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

class MusicContainer(object):
# ########################################
    PATH      =  1;    # Song Path
    EXIF      =  0;    # FullSongData also bad attempt at abrv EXtInF:EXTra INFo Used for all info minus file path
    ARTIST    =  2;    # Song Artist
    TITLE     =  3;    # Song Title
    ALBUM     =  4;    # Song Album
    GENRE     =  5;    # Song Genre
    DATESTAMP =  6;    # Stamp in passive order from the last time this was played. YYYY/MM/DD HH:MM
    COMMENT   =  7;
    RATING    =  8;    # Song Rating
    LENGTH    =  9;    # total length of the song in -M:SS
    SONGINDEX = 10;    # Album Index

    PLAYCOUNT = 11;    # Total count of the number of times this song has played
    SKIPCOUNT = 12;    # Number of times user has clicked next for this song.
    FILESIZE  = 13;    # File Size in KB
    BITRATE   = 14; # Kb per s
    FREQUENCY = 15; # running waited average of play frequency ( a avg value of time between playings
    DATEVALUE = 16  # DATESTAMP, but as INT value ( determined while loading songs
    SONGID    = 99  # 64bit hex song id
    # #####
    SPECIAL   = 17; # true when any error makes this file unuseable ever
    SELECTED  = 18; # Boolean, selected or not
    # ########################################
    STRINGTERM = 8; # if a value is less than this, we have a string
    NUMTERM = 19;   # if less than this, greater than strterm, we have a numerical value
    SPEC_WEEK  = 101 # searching by week count ( similar to search by .day)
    SPEC_MONTH = 102 # searching by month count ( similar to search by .day)
    SPEC_DATEEU  = 103 # search by formated date DD/MM/YYYY
    SPEC_DATEUS  = 104 # search by formated date MM/DD/YYYY
    SPEC_DATESTD = 105 # search by formated date YYYY/MM/DD

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
    # this will be the official abreviation list
    D_StrToDec = {   'alb'           : ALBUM, \
                     'abm'           : ALBUM, \
                     'album'         : ALBUM, \
                     'art'           : ARTIST, \
                     'artist'        : ARTIST, \
                     'bitrate'       : BITRATE, \
                     'comm'          : COMMENT, \
                     'comment'       : COMMENT, \
                     'day'           : DATESTAMP, \
                     'dateval'       : DATEVALUE, \
                     'exif'          : EXIF, \
                     'size'          : FILESIZE, \
                     'freq'          : FREQUENCY, \
                     'gen'           : GENRE, \
                     'len'           : LENGTH, \
                     'path'          : PATH, \
                     'pcnt'          : PLAYCOUNT, \
                     'playcount'     : PLAYCOUNT, \
                     'rte'           : RATING, \
                     'rate'          : RATING, \
                     'rating'        : RATING, \
                     'sel'           : SELECTED, \
                     'scnt'          : SKIPCOUNT, \
                     'skipcount'     : SKIPCOUNT, \
                     'id'            : SONGID, \
                     'index'         : SONGINDEX, \
                     'spec'          : SPECIAL, \
                     'dateeu'        : SPEC_DATEEU, \
                     'dateus'        : SPEC_DATEUS, \
                     'date'          : SPEC_DATESTD, \
                     "month"         : SPEC_MONTH, \
                     "week"          : SPEC_WEEK, \
                     'ttl'           : TITLE, \
                     'tit'           : TITLE, \
                     'title'         : TITLE
                    } 
    
    def exifToString(self,exif):
    
        if   exif == MusicContainer.PATH      : return "PATH"; 
        elif exif == MusicContainer.EXIF      : return "EXIF"; 
        elif exif == MusicContainer.ARTIST    : return "ARTIST"; 
        elif exif == MusicContainer.TITLE     : return "TITLE"; 
        elif exif == MusicContainer.ALBUM     : return "ALBUM"; 
        elif exif == MusicContainer.GENRE     : return "GENRE"; 
        elif exif == MusicContainer.DATESTAMP : return "DATESTAMP"; 
        elif exif == MusicContainer.COMMENT   : return "COMMENT"; 
        elif exif == MusicContainer.RATING    : return "RATING"; 
        elif exif == MusicContainer.LENGTH    : return "LENGTH"; 
        elif exif == MusicContainer.SONGINDEX : return "SONGINDEX";  
        elif exif == MusicContainer.PLAYCOUNT : return "PLAYCOUNT"; 
        elif exif == MusicContainer.SKIPCOUNT : return "SKIPCOUNT"; 
        elif exif == MusicContainer.FILESIZE  : return "FILESIZE"; 
        elif exif == MusicContainer.BITRATE   : return "BITRATE"; 
        elif exif == MusicContainer.FREQUENCY : return "FREQUENCY"; 
        elif exif == MusicContainer.DATEVALUE : return "DATEVALUE";  
        elif exif == MusicContainer.SPECIAL   : return "SPECIAL"; 
        elif exif == MusicContainer.SELECTED  : return "SELECTED";  
        elif exif == MusicContainer.SONGID    : return "ID#";  
        return "UNKOWN TAG:%d"%exif
        
    def stringToExif(self,exif):
    
        if   exif == "PATH"      : return MusicContainer.PATH     
        elif exif == "EXIF"      : return MusicContainer.EXIF     
        elif exif == "ARTIST"    : return MusicContainer.ARTIST   
        elif exif == "TITLE"     : return MusicContainer.TITLE    
        elif exif == "ALBUM"     : return MusicContainer.ALBUM    
        elif exif == "GENRE"     : return MusicContainer.GENRE    
        elif exif == "DATESTAMP" : return MusicContainer.DATESTAMP
        elif exif == "COMMENT"   : return MusicContainer.COMMENT  
        elif exif == "RATING"    : return MusicContainer.RATING   
        elif exif == "LENGTH"    : return MusicContainer.LENGTH   
        elif exif == "SONGINDEX" : return MusicContainer.SONGINDEX
        elif exif == "PLAYCOUNT" : return MusicContainer.PLAYCOUNT 
        elif exif == "SKIPCOUNT" : return MusicContainer.SKIPCOUNT 
        elif exif == "FILESIZE"  : return MusicContainer.FILESIZE 
        elif exif == "BITRATE"   : return MusicContainer.BITRATE  
        elif exif == "FREQUENCY" : return MusicContainer.FREQUENCY 
        elif exif == "DATEVALUE" : return MusicContainer.DATEVALUE  
        elif exif == "SPECIAL"   : return MusicContainer.SPECIAL  
        elif exif == "SELECTED"  : return MusicContainer.SELECTED  
        elif exif == "ID#"       : return MusicContainer.SONGID         
        return 0
    
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

class SEARCH(object):
    OR = 0x10  # OR
    NT = 0x20  # NOT     
    IO = 0x40  # IOR       
    EQ = 0x01  # EQuals       
    GT = 0x02  # Greater Than       
    LT = 0x04  # Less Than
    GE = EQ|GT      # 0x03
    LE = EQ|LT      # 0x05
    MOD  = OR|NT|IO # 0x70
    DIR  = EQ|LT|GT # 0x07
    MASK = DIR|MOD  # 0x77
    def __init__(self,value):
        self.value = value 
        
    def __repr__(self):
        return "SEARCH(0x%02X)"%self.value
        
    def __str__(self):
        # EXAMPLE:
        # print "ENUM SEARCH = %S"%SEARCH(value)
        s = ""
        if   self.value&SEARCH.OR: s+="_OR"
        elif self.value&SEARCH.NT: s+="_NOT"
        elif self.value&SEARCH.IO: s+="_IO"
        else: s+="_AND"
        
        if   self.value&SEARCH.GE==SEARCH.GE: s+="_GE"
        elif self.value&SEARCH.LE==SEARCH.LE: s+="_LE"
        elif self.value&SEARCH.GT: s+="_GT"
        elif self.value&SEARCH.LT: s+="_LT"
        elif self.value&SEARCH.EQ: s+="_EQ"
        else                     : s+="_INC"
        
        return "_%s__"%s
    def __unicode__(self):
        return unicode(self.__str__())
# ###################################################################
# 
# ###################################################################

# ###################################################################
# Custom Data Types
# ###################################################################
class hex(int):
    """
        Sublcass pythons integer object
        to print as a hexadecimal number
        the function len() returns a hex
        number that is count characters long
        # use:
        # hex(-4).len(4) # prints 0xFFFC
    """
    def len(self,value):
        if value > 8: value = 8;
        if value < 1: value = 8;
        return "0x"+("%08X"%(self&0xFFFFFFFF))[-value:]
    def __repr__(self):
        return "hex(0x%08X)"%self
    def __str__(self):
        return "0x%X"%(self&0xFFFFFFFF)
    def __unicode__(self):
        return u"0x%X"%(self&0xFFFFFFFF)
        
import ctypes         

class hex64(ctypes.c_ulonglong):

    def __init__(self,lower,upper=0):
        """
            USE:
            hex64(2)       # returns 00000000_00000002
            hex64(2,4)     # returns 00000004_00000002
            hex64( hex64 ) # returns a copy of hex64
            lower can take any integer data type, byte, int, long, long long
            if upper is non zero, its value is logical-ORed into the upper
            32 bit position of the unsigned 64 bit long long
        """
        if type(lower) == hex64:
            lower = lower.value
        if (type(lower) == str):
            lower = lower[2:]
            lower = lower.replace('_','')
            upper = long(lower[:-8],16)
            lower = long(lower[-8:],16)
            
        super(hex64,self).__init__(lower);
        
        self.value = lower | (upper<<32)
    
    def __repr__(self):
        s1 = "0x%08X"%ctypes.c_ulong(self.value>>32).value
        s2 = "0x%08X"%ctypes.c_ulong(self.value    ).value
        return "hex64(%s,%s)"%(s2,s1)
    def __str__(self):
        s1 = "%08X"%ctypes.c_ulong(self.value>>32).value
        s2 = "%08X"%ctypes.c_ulong(self.value    ).value
        return "0x%s_%s"%(s1,s2)
    def __unicode__(self):
        s1 = u"%08X"%ctypes.c_ulong(self.value>>32).value
        s2 = u"%08X"%ctypes.c_ulong(self.value    ).value
        return u"0x%s_%s"%(s1,s2)
    def __int__(self):
        return int(self.value&0x00000000FFFFFFFFL)
    def __long__(self):
        return long(self.value)
        
    def __eq__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __EQ__ HEX64. FOUND %s"%(type(b))
        
        return self.value == b.value
    def __ne__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __NE__ HEX64. FOUND %s"%(type(b))
        
        return self.value != b.value
    def __lt__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __LT__ HEX64. FOUND %s"%(type(b))
        
        return self.value < b.value
    def __le__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __LE__ HEX64. FOUND %s"%(type(b))
        
        return self.value <= b.value    
    def __gt__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __GT__ HEX64. FOUND %s"%(type(b))
        
        return self.value > b.value
    def __ge__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __GE__ HEX64. FOUND %s"%(type(b))
        
        return self.value >= b.value
    
    def truth(self):
        return self.value > 0

    def __add__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value+b)
    def __iadd__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value += b
        return self
    def __sub__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value-b)
    def __isub__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value -= b
        return self
    def __mul__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value*b)
    def __imul__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value *= b
        return self
    def __div__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value/b)
    def __idiv__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value /= b
        return self
    def __mod__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value%b)
    def __imod__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value %= b
        return self
    def __pow__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value**b)
    def __ipow__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value **= b
        return self
        
    def __rshift__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value>>b)
    def __irshift__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value >>= b
        return self
    def __lshift__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value<<b)
    def __ilshift__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value <<= b
        return self
    def __or__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value|b)
    def __ior__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value |= b
        return self
    def __and__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value&b)
    def __iand__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value &= b
        return self
    def __xor__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value^b)
    def __ixor__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value ^= b
        return self
    def __inv__(self):
        return hex64(~self.value)
    __invert__ = __inv__


import os

class Song(list):    

    def __init__(self,varient=""):
        super(Song,self).__init__([0]*GlobalContainer.SONGDATASIZE)
        
        
        if type(varient) == Song:
            self.id = varient.id
            self.md5 = ""
            self[MusicContainer.PATH]      = varient[MusicContainer.PATH]     
            self[MusicContainer.ARTIST]    = varient[MusicContainer.ARTIST]   
            self[MusicContainer.TITLE]     = varient[MusicContainer.TITLE]    
            self[MusicContainer.ALBUM]     = varient[MusicContainer.ALBUM]    
            self[MusicContainer.GENRE]     = varient[MusicContainer.GENRE]    
            self[MusicContainer.DATESTAMP] = varient[MusicContainer.DATESTAMP]
            self[MusicContainer.DATEVALUE] = varient[MusicContainer.DATEVALUE]
            self[MusicContainer.COMMENT]   = varient[MusicContainer.COMMENT]  
            self[MusicContainer.RATING]    = varient[MusicContainer.RATING]   
            self[MusicContainer.LENGTH]    = varient[MusicContainer.LENGTH]   
            self[MusicContainer.SONGINDEX] = varient[MusicContainer.SONGINDEX]
            self[MusicContainer.PLAYCOUNT] = varient[MusicContainer.PLAYCOUNT]
            self[MusicContainer.SKIPCOUNT] = varient[MusicContainer.SKIPCOUNT]
            self[MusicContainer.FILESIZE]  = varient[MusicContainer.FILESIZE] 
            self[MusicContainer.FREQUENCY] = varient[MusicContainer.FREQUENCY]
            self[MusicContainer.BITRATE]   = varient[MusicContainer.BITRATE]  
            self[MusicContainer.SPECIAL]   = varient[MusicContainer.SPECIAL]  
            self[MusicContainer.SELECTED]  = varient[MusicContainer.SELECTED] 
        else:
            self.id = hex64(0)
            self.md5 = ""
            self[MusicContainer.PATH]      = unicode(varient)
            self[MusicContainer.ARTIST]    = u"Unknown Artist" 
            self[MusicContainer.TITLE]        = u"Unknown Title" 
            self[MusicContainer.ALBUM]        = u"Unknown Album" 
            self[MusicContainer.GENRE]     = u"None" 
            self[MusicContainer.DATESTAMP] = "NEW"
            self[MusicContainer.DATEVALUE] = 0
            self[MusicContainer.COMMENT]   = ""
            self[MusicContainer.RATING]    = 0
            self[MusicContainer.LENGTH]    = 64
            self[MusicContainer.SONGINDEX] = 0
            self[MusicContainer.PLAYCOUNT] = 0
            self[MusicContainer.SKIPCOUNT] = 0
            self[MusicContainer.FILESIZE]  = 0
            self[MusicContainer.FREQUENCY] = 0
            self[MusicContainer.BITRATE]   = 0
            self[MusicContainer.SPECIAL]   = False
            self[MusicContainer.SELECTED]  = False
        
        
    def __str__(self):
        return "[%s] %s - %s"%(self.id,self[MusicContainer.ARTIST],self[MusicContainer.TITLE])    
    
    def update(self):
        """
            set id to a 64 bit unsigned integer with format:
            upper 32 = [A1-6,A2-6,LA-7|B1-6,LB-7]
            lower 32 = [T1-6,T2-6,LT-8| LEN-12  ]
            Where A = Artist, B = Album, T = Title, Len is SONG LENGTH
            and A1 indicates the first character of ARTIST
            and -6 indicates to format that charcter into 6 bits (resp. 7,8,12)
            
            This is ingeneral a very weak way of encoding a song into the minimum number of bits
            This will only work for US-ASCII and even then will only work well
            with ALPHA-NUMERIC data. I will assume that 90% of songs fit in that pattern
            
            This number should be mostly unique. ASSUME that it is ALWAYS unique
            
            If one sorts by this number songs will appear in order of Artist,
            and internally sorted by album then title, then song length
            
            Only the first 2 charactes are considered (1 for album)
            if two text entries contain the same first charactereds
            then the comparison uses the length of the word taking the shorter first
            This will take care of edge cases such as "ITEM - I", "ITEM - IV" etc (for small sets)
            
            slots 0x26 - 0x3E can be defined to anything to help extend uniqueness
            
            special case to whatch: Tsubasa
            4 albums all hash to the same 32 bit hi values TS and TS
            lower 32 bits are always different, so this is success
        """
        art = self[MusicContainer.ARTIST].upper()
        if art[:4] == "THE ":
            art = art[4:]
        
        a = u"%- 2s"%art[:2]
        b = u"%s"   %self[MusicContainer.ALBUM ][:1].upper()
        t = u"%- 2s"%self[MusicContainer.TITLE ][:2].upper()
        l = self[MusicContainer.LENGTH ]
        _a = (Song.__char_to_6bit__(a[0])<<6)|Song.__char_to_6bit__(a[1])
        _a = (_a<<7)|Song.__str_to_Xbit__(self[MusicContainer.ARTIST])
        _b =  Song.__char_to_6bit__(b)
        _b = (_b<<7)|Song.__str_to_Xbit__(self[MusicContainer.ALBUM])
        _t = (Song.__char_to_6bit__(t[0])<<6)|Song.__char_to_6bit__(t[1])
        _t = (_t<<8)|Song.__str_to_Xbit__(self[MusicContainer.TITLE])
        _l = Song.__int_to_Xbit__(l)
        
        _x = (_a<<13)|_b
        _y = (_t<<12)|_l
        
        self.id = hex64(_y,_x)

        #print self.id
        #print "[%-2s] [%-2s] [%-2s] [%-d]"%(a,b,t,l)
        #print "[%03X] [%03X] [%03X] [%03X]"%(_a,_b,_t,_l)
        return
        
    @staticmethod
    def __char_to_6bit__(c):
        o = ord(c)
        # 00 - 09 := 0-9    
        # 0A      := ASCII 0 - 127, not ALPHANUMERIC   
        # 0B - 24 := A-Z    
        # 25      := ASCII 127 - 256  
        # 26      :=        
        # 27      :=        
        # 28      :=        
        # 29      :=        
        # 2A      :=        
        # 2B      :=        
        # 2C      :=        
        # 2D      :=        
        # 2E      :=        
        # 2F      :=        
        # 30      :=        
        # 31      :=        
        # 32      :=        
        # 33      :=        
        # 34      :=        
        # 35      :=        
        # 36      :=        
        # 37      :=        
        # 38      :=        
        # 39      := Hiragana lower half      
        # 3A      := Hiragana upper half       
        # 3B      := Katakana lower half
        # 3C      := Katakana upper half
        # 3D      := kanjii lower half 4E00 - 76DF mostly useless
        # 3E      := Kanjii upper half 76F0 - 9FBF
        # 3F      := else        
        if ord(u'0') <= o <= ord(u'9'):
            return o - ord(u'0')
        elif ord(u'A') <= o <= ord(u'Z'): 
            return o - ord(u'A') + 11
        elif o <= 127:
            return 0x0A;
        elif 0x0000 <= o <= 0x0000:
            return 0x025;
        elif 0x3040 <= o <= 0x306F:
            return 0x39
        elif 0x3070 <= o <= 0x309F:
            return 0x3A
        elif 0x30A0 <= o <= 0x30CF:
            return 0x3B
        elif 0x30D0 <= o <= 0x30FF:
            return 0x3C
        elif 0x4E00 <= o <= 0x76DF:
            return 0x3D
        elif 0x76F0 <= o <= 0x9FBF:
            return 0x3E

        
        return 0x3F
    @staticmethod
    def __str_to_Xbit__(s,b=7):
        l = len(s)
        m = (1<<b) - 1; # max int
        return l if l<=m else m
    @staticmethod
    def __int_to_Xbit__(s,b=12):  
        m = (1<<b) - 1; # max int
        return s if s<=m else m
    
    
        

    
# ###################################################################
# Instantiate
# ###################################################################

MpGlobal = GlobalContainer()
MpMusic  = MusicContainer()
Settings = RecordContainer()

# ###################################################################
# Import C DLL
# currently highly experimental
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


