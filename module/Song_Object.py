# #########################################################
# #########################################################
# File: MpGlobalDefines
#
# Description:
#   Defines the base representation of a Song for the Media Player
#   This file no longer depends on any other files in the project.   
#
#   see MpGlobalDefines for MusicContainer, an extension of EnumSong
# #########################################################

import os
import time

from datatype_hex64 import *

class EnumSong(object):
    PATH      =  1;    # Song Path
    EXIF      =  0;    # FullSongData also bad attempt at abrv EXtInF:EXTra INFo Used for all info minus file path
    ARTIST    =  2;    # Song Artist
    TITLE     =  3;    # Song Title
    ALBUM     =  4;    # Song Album
    GENRE     =  5;    # Song Genre
    DATESTAMP =  6;    # Stamp in passive order from the last time this was played. YYYY/MM/DD HH:MM
    COMMENT   =  7;    # user given comment
    DATEADDEDS=  8;    # string form date the song was added to the library
    
    RATING    =  9;    # Song Rating
    LENGTH    = 10;    # total length of the song in -M:SS
    SONGINDEX = 11;    # Album Index
    PLAYCOUNT = 12;    # Total count of the number of times this song has played
    SKIPCOUNT = 13;    # Number of times user has clicked next for this song.
    FILESIZE  = 14;    # File Size in KB
    BITRATE   = 15;    # Kb per s
    FREQUENCY = 16;    # running waited average of play frequency ( a avg value of time between playings
    DATEVALUE = 17;    # DATESTAMP, but as INT value ( determined while loading songs
    DATEADDED = 18
    YEAR      = 19;    # year the song was made.
    # #####
    SPECIAL   = 20; # true when any error makes this file unuseable ever
    SELECTED  = 21; # Boolean, selected or not
    
    # ########################################
    # Other Enumerations
    
    SONGID    = 99  # 64bit hex song id
    # ########################################
    STRINGTERM = RATING; # if a value is less than this, we have a string
    NUMTERM = SELECTED+1;   # if less than this, greater than strterm, we have a numerical value
    SPEC_WEEK  = 101 # searching by week count ( similar to search by .day)
    SPEC_MONTH = 102 # searching by month count ( similar to search by .day)
    SPEC_DATEEU  = 103 # search by formated date DD/MM/YYYY
    SPEC_DATEUS  = 104 # search by formated date MM/DD/YYYY
    SPEC_DATESTD = 105 # search by formated date YYYY/MM/DD

    SONGDATASIZE = SELECTED+1 #NOTE: selected must always be the last element in the array
    
class Song(list):
    __repr_str__ = [ EnumSong.ARTIST,
                     EnumSong.TITLE,
                     EnumSong.ALBUM,
                     EnumSong.GENRE,
                     EnumSong.COMMENT,
                   ];
    __repr_num__ = [ EnumSong.RATING,
                     EnumSong.LENGTH,
                     EnumSong.DATEVALUE,
                     EnumSong.SONGINDEX,
                     EnumSong.PLAYCOUNT,
                     EnumSong.SKIPCOUNT,
                     EnumSong.FREQUENCY,
                     EnumSong.FILESIZE,
                     EnumSong.BITRATE,
                     EnumSong.DATEADDED,
                     EnumSong.YEAR
                   ];        
            
    def __init__(self,varient="",DRIVELIST=[],DATEFMT="%Y/%m/%d %H:%M"):
        """
            Provides 4 different ways to make a new song
            the default, provide only a path and a container will be created with dummy values
            
            pass a repr string and a date format to reconstruct a saved song.
            
            of pass in a Song, and an exact copy will be made.
        """
        super(Song,self).__init__([0]*EnumSong.SONGDATASIZE)
        self.id = hex64(0);
        self.md5 = "";

        if type(varient) == Song:
            # produce a copy of the song.
            self.id = varient.id
            self.md5 = varient.md5
            self[EnumSong.PATH]      = varient[EnumSong.PATH]
            self[EnumSong.ARTIST]    = varient[EnumSong.ARTIST]
            self[EnumSong.TITLE]     = varient[EnumSong.TITLE]
            self[EnumSong.ALBUM]     = varient[EnumSong.ALBUM]
            self[EnumSong.GENRE]     = varient[EnumSong.GENRE]
            self[EnumSong.DATESTAMP] = varient[EnumSong.DATESTAMP]
            self[EnumSong.DATEVALUE] = varient[EnumSong.DATEVALUE]
            self[EnumSong.COMMENT]   = varient[EnumSong.COMMENT]
            self[EnumSong.RATING]    = varient[EnumSong.RATING]
            self[EnumSong.LENGTH]    = varient[EnumSong.LENGTH]
            self[EnumSong.SONGINDEX] = varient[EnumSong.SONGINDEX]
            self[EnumSong.PLAYCOUNT] = varient[EnumSong.PLAYCOUNT]
            self[EnumSong.SKIPCOUNT] = varient[EnumSong.SKIPCOUNT]
            self[EnumSong.FILESIZE]  = varient[EnumSong.FILESIZE]
            self[EnumSong.FREQUENCY] = varient[EnumSong.FREQUENCY]
            self[EnumSong.BITRATE]   = varient[EnumSong.BITRATE]
            self[EnumSong.SPECIAL]   = varient[EnumSong.SPECIAL]
            self[EnumSong.SELECTED]  = varient[EnumSong.SELECTED]
            self[EnumSong.DATEADDEDS]= varient[EnumSong.DATEADDEDS]
            self[EnumSong.DATEADDED] = varient[EnumSong.DATEADDED]
            self[EnumSong.YEAR ]     = varient[EnumSong.YEAR]
            return;
        elif type(varient) == str or type(varient) == unicode: # TODO: of type basestring
            
            if varient.strip().count('\n') > 0:
                self.from_repr(varient,DRIVELIST,DATEFMT);
                return;
        
        self[EnumSong.PATH]      = unicode(varient)
        self[EnumSong.ARTIST]    = u"Unknown Artist"
        self[EnumSong.TITLE]     = u"Unknown Title"
        self[EnumSong.ALBUM]     = u"Unknown Album"
        self[EnumSong.GENRE]     = u"None"
        self[EnumSong.DATESTAMP] = "NEW"
        self[EnumSong.DATEADDEDS]= ""
        self[EnumSong.DATEVALUE] = 0
        self[EnumSong.COMMENT]   = ""
        self[EnumSong.RATING]    = 0
        self[EnumSong.LENGTH]    = 64
        self[EnumSong.SONGINDEX] = 0
        self[EnumSong.PLAYCOUNT] = 0
        self[EnumSong.SKIPCOUNT] = 0
        self[EnumSong.FILESIZE]  = 0
        self[EnumSong.FREQUENCY] = 0
        self[EnumSong.BITRATE]   = 0
        self[EnumSong.SPECIAL]   = False
        self[EnumSong.SELECTED]  = False
        self[EnumSong.DATEADDEDS]= ""
        self[EnumSong.DATEADDED] = 0
        self[EnumSong.YEAR ]     = 0
        

    def __str__(self):
        return "[%s]"%(self.id)
    
    def __unicode__(self):
        return "[%s] %s - %s"%(self.id,self[EnumSong.ARTIST],self[EnumSong.TITLE])

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
        art = self[EnumSong.ARTIST].upper()
        if art[:4] == "THE ":
            art = art[4:]

        a = u"%- 2s"%art[:2]
        b = u"%s"   %self[EnumSong.ALBUM ][:1].upper()
        t = u"%- 2s"%self[EnumSong.TITLE ][:2].upper()
        l = self[EnumSong.LENGTH ]
        _a = (Song.__char_to_6bit__(a[0])<<6)|Song.__char_to_6bit__(a[1])
        _a = (_a<<7)|Song.__str_to_Xbit__(self[EnumSong.ARTIST])
        _b =  Song.__char_to_6bit__(b)
        _b = (_b<<7)|Song.__str_to_Xbit__(self[EnumSong.ALBUM])
        _t = (Song.__char_to_6bit__(t[0])<<6)|Song.__char_to_6bit__(t[1])
        _t = (_t<<8)|Song.__str_to_Xbit__(self[EnumSong.TITLE])
        _l = Song.__int_to_Xbit__(l)

        _x = (_a<<13)|_b
        _y = (_t<<12)|_l

        self.id = hex64(_y,_x)

        self.__format_exif__()
        #print self.id
        #print "[%-2s] [%-2s] [%-2s] [%-d]"%(a,b,t,l)
        #print "[%03X] [%03X] [%03X] [%03X]"%(_a,_b,_t,_l)
        return

    @staticmethod
    def __char_to_6bit__(c):
        o = ord(c.upper())
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
        elif o <= 0x7F:
            return 0x0A;
        elif o <= 0xFF:
            return 0x25;
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
    @staticmethod
    def repr_length():
        return 6; # return the number of lines of text retunred by __repr__.
    
    def __format_exif__(self):
        """
            returns a formatted exif string.
            ExIf stands for EXtra InFo
            this frame contains information from all text frames,
            this makes it possible to search all text fields, at once, in an easier way
        """
        return "%s %s %s %s %s"%( \
            unicode(self[EnumSong.ARTIST]), \
            unicode(self[EnumSong.TITLE]), \
            unicode(self[EnumSong.ALBUM]), \
            unicode(self[EnumSong.GENRE]), \
            unicode(self[EnumSong.COMMENT]) );
            
    def __repr__(self,drivelist=[]):

        """
            repr produces the following 6 lines:
            "3 Doors Down","Kryptonite","The Better Life","Alternative Rock","2011/08/28 06:55",""
            5,233,1,12,0,92,3656,0
            D:\\Music\\discography\\discography - 3 doors down\\the better life\\01 kryptonite.mp3
            md5:
            c1:
            c2:
            
            if drivelist is not empty, as in (song.__repr__([]) is called and not "%r"%song ) 
                then the largest match from drivelist is stripped from the START of PATH

        """

        # ######################################
        # generate string and number values
        q = lambda x: x.replace("\"","\\\"");

        sfmt = ""
        nfmt = ""
        
        for field in Song.__repr_str__:
            sfmt += "\"%s\","%q(self[field])
            
        for field in Song.__repr_num__:
            nfmt += "%d,"%self[field]

        # ######################################
        # determine what to save from the path
        p = self[EnumSong.PATH]
        lp = p.lower().replace("\\",'/');
        lmatch = 0
        
        for part in drivelist:
            part = part.lower().replace("\\",'/');
            if lp.startswith(part):
                lmatch = len(part);
                
        p = p[lmatch:]     
        
        if p[0] == '\\' or p[0] == '/': # unix bug fix for path restoration
            p = p[1:]
            
        # ###################################### 
        # store everything under one multiline string
        # -1 strips final comma
        repr  = u"%s\n"%unicode(sfmt[:-1]).encode('unicode-escape')
        repr += u"%s\n"%unicode(nfmt[:-1])
        repr += u"%s\n"%unicode(p).encode('unicode-escape');
        repr += u"md5:%s\n"%self.md5;
        repr += u"lo:\n";   # lo frequency information
        repr += u"hi:\n";   # hi frequency information
        
        # A NEW LINE MUST BE THE LAST CHARACTER IN REPR
        # BUT IS NOT REQUIRED IN RESTORING FROM A REPR

        return repr

    def from_repr(self,string,DRIVELIST,FMT):
        """
            take the output from __repr__
            and set the values of the current song.
            
            FMT allows the date to be formatted an way a user wants, as only the UNIX time stamp
            is saved, as an integer
            
        """
        string = str(string).strip() # cannot have an unicode object here
        
        R = string.split("\n") # split the 6 or more line string into multiple lines
        R[0] = R[0][1:-1] # strip the beginning and ending quotes from the string field
        
        s = R[0].strip().split('","') # in repr all " are changed to \" therefore any instance
                                      # of "," in a song field will be \",\". this split cannot fail.

        n = R[1].split(',');
        
        # process each string value
        for i in range(len(s)): # fix all escaped quotes
            s[i] = unicode(s[i],'unicode-escape').replace("\\\"","\"");
        
        # s is now an array of unicode strings for all text information stored
        # n is now an array of integers for all text information stored
        
        # by keying off the length of 's' and 'n', i can tack on
        # new save values to the END of the __repr_str__ and __repr__num__
        # lists, then the next time the user saves these values will be saved
        # and automatically loaded later.
        for i in Song.__repr_str__:
            self[i] = ""
            
        for i in range(len(s)):
            self[Song.__repr_str__[i]] = s[i]
            
        for i in range(len(n)):
            self[Song.__repr_num__[i]] = int(n[i])
            
        # ################################################################
        # other infomation
        path = unicode(R[2].strip(),'unicode-escape')
        if len(DRIVELIST) > 0:
            for drive in DRIVELIST:
                p = os.path.join(drive,path)
                if os.path.exists(p):
                    path = p;
                    break;

            
        self[EnumSong.PATH] = path
        
        # use the time library to format the date
        ds = ""
        try:
            if EnumSong.DATEVALUE > 0:
                ds = time.strftime(FMT, time.localtime(self[EnumSong.DATEVALUE])) 
            #TODO -V0.5.0.0 : remove this code.
            if ds == "1969/12/31 19:00":
                ds = ""
                self[EnumSong.DATEVALUE] = 0;
        except:
            pass
        finally:
            #print ds
            self[EnumSong.DATESTAMP] = ds 
        
        # ################################################################
        # special data
        
        R[3] = R[3][4:] # R3 = md5
        R[4] = R[4][3:] # R4 = lo frequency info
        R[5] = R[5][3:] # R5 = hi frequency info

        self[EnumSong.EXIF]      = self.__format_exif__();
        self[EnumSong.SPECIAL]   = False
        self[EnumSong.SELECTED]  = False 
        self[EnumSong.DATEADDEDS]=""
        
        self.update();
     
