# #########################################################
# #########################################################
# File: MpScripting
# import:  from Song_Search import SearchObject
# Description:
#   Provides a generic way to search through a list of Songs
# Abreviations are given for each field, allowing a user
# to type .art ="Stone Temple Pilots" and return all songs
# with a matching artist.
# the type of abreviations used can be changed, and the Sigil
# character does not matter, as long as it is not alphanumeric.
# Macros are provided, '.favorite' can be used to expand
# to a list of favorite artists and '.preset X' can be 
# ued to expand to a predefined search string.
# #########################################################

from calendar import timegm
import time
import datetime

from datatype_hex64 import *
from Song_Object import Song, EnumSong
from StringQuoter import *    

from SystemPathMethods import *

from collections import namedtuple
SearchTerm = namedtuple("SearchTerm",'str typ dir cf rf') #TODO use these instead of just tuples



class SearchObject_Controller(object):
    """
        Thsi class provides a way for globally setting values needed to extend
        the functionality of the Search Class.
        
        Example use found in the Console Player:
        found during initilization before the main window is created in MpApplication.py
        SearchObject_Controller.getSearchDictionary   = SOC_getSearchDictionary   
        SearchObject_Controller.getFavoriteArtistList = SOC_getFavoriteArtistList                            
        SearchObject_Controller.getPresetStringdef    = SOC_getPresetString
    """
    #TODO: remember to update this dictionary whenever you update the default one in MpGlobalDefines.
    D_StrToDec = {   'alb'           : EnumSong.ALBUM, \
                     'abm'           : EnumSong.ALBUM, \
                     'added'         : EnumSong.DATEADDED, \
                     'album'         : EnumSong.ALBUM, \
                     'art'           : EnumSong.ARTIST, \
                     'artist'        : EnumSong.ARTIST, \
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
    
    @staticmethod
    def getSearchDictionary():
        #return MpMusic.D_StrToDec                # what the function actually does in Console Player
        return SearchObject_Controller.D_StrToDec # what it should do by default
    @staticmethod
    def getFavoriteArtistList():
        #return Settings.FAVORITE_ARTIST    # what the function actually does in Console Player
        return []                           # what it should do by default
    @staticmethod
    def getPresetString(index):
        #return Settings.getPreset(index)   # what the function actually does in Console Player
        return ""                           # what it should do by default

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
              
class SearchObject(object):
    # """
    #     provides an object that contains all methods related to 
    #     searching a list of music
    #     
    #     taking a user input string, and turning it into something that can be used
    #     to itterate over the list of music involves many small intermediate steps.
    #     
    #     create a new searchObject, while supplying a search string
    #     
    #     then use searchObject.match to compare a song to given string.
    #     
    #     use searchObject.search to return a list of songs from a supplied list that match
    #    TODO would a named tuple be better for the string terms
    #    from collections import namedtuple
    #    Point = namedtuple('Point', 'x y')
    #    p = Point(1,5)
    #    then, p.x == p[0]
    # """
    """
        Searching
        
        \\<font size="3" color=#FF0000\\> Suggestions on how to make searching more intuitive are welcome\\</font\\>
        
        Console Player provides the ability to quickly search through your library of music. Results are returned instantly. To make refining your searches easier a series of keywords, called 'Dot Words' for the period prefix, and control characters can be used. A Search is allways case insensitive. This page will go over the basics of searching, for more information check the sub pages.
        
        \\<b\\>The Basics:\\</b\\>
            Typing in any word, part of an arist name, song titles, etc, will return any song that contains that word.
        
        \\<b\\>Modifier Characters:\\</b\\>  
            = < > <= >= 
            Modifier characters control how a word is compared. 
            
                Text Data:
                    When searching for text data, by default a song will be considered 
                    a match if the word appears anywhere in the tag. 
                    The Equals sign '=' can be used to force matching to the beginning 
                    of the word.
                    The other modifiers make no lexical sense, and are ignored
                    
                Numerical Data:
                    By default all numerical data is compared exactly. if you type 
                    '.rte 4' then the songs returned will have a rating of exactly 4.
                    The Modifer characters should be intuitive, '.rte <4' returns a
                    song which contains a rating less than 4, etc.
                    
                Dates:
                    Dates can be a little tricky. By convention '<' Less  Than, means 
                    closer to the present time. and '>' Greater Than means farther away 
                    from present time.
                    
                    By default if no modifier is encountered '>' Greater than is assumed.
                    Therefor '.day 4' means that any song not played for at least 4 days 
                    will be returned.
                    It Follows that '.day <4' means any song played within the last 4 days.

        \\<b\\>Special Characters:\\</b\\>  
            Special character allow change how the the search results are interpreted. see the page on Special Characters.
        \\<b\\>Quotes:\\</b\\>
            Searches are broken up by spaces. 'The Pillows' will become two different searches, one for the word 'THE' and one for 'PILLOWS'. To fix this use double quotes (or single quotes) to group the text into one term. ' "the Pillows" '
        \\<b\\>Examples:\\</b\\>  
            ".art 
        \\<b\\>How it works:\\</b\\>
            A Search is separated by 'Frames' by commas ',' or semicolons ';'. each frame is processed indiviually. First the frame is checked for a dot word. This determines which song tag to compare against. If no dot word is found, the default is used, which includes all text data and the rating of the songs.
            
            Once the search type is determined that data from the frame is parsed. Modifier characters and special characters are read from left to right, as well as each term.
    """
    
    def __init__(self,string=""):
        """
            Special Words:
                At the start of each frame it is possible to change what tag that frame will match by using a dot word. For example '.art' is one way to force that frame to only match the artist tag of a song.
            
            
            blah blah blah mr freeman
        """
        self.q = StringQuote()
        self.q.quoteable = '"'  # only quote items wrapped in double quotes
        
        self._original = unicode(string) # create a copy of the string

        self._searchC = []
        self._searchO = []
        self._searchN = []
        self._searchX = [[]]
        
        self.termCount = 0;
        
        # these are used with Search N
        self.search_iter_index = 0
        self.search_iter_list = None
        self.search_iter_N = 0
        
        if string != "":
            self.compile(string)      
      
    def compile(self,string):
        """
            Dot Words
            
            
            \\<table\\>
            \\<b\\>Dot Word\\</b\\> | \\<b\\>Field\\</b\\> | \\<b\\>Description\\</b\\>
            
            \\<b\\>Text Info\\</b\\>
            .alb .abm .album | Album | Search by album info.
            .art .artist     | Artist | Search by artist info.
            .comm .comment   | Comment | Search by user set comments.
            .gen .genre      | Genre | Search by the songs genre.
            .path            | Path  | Search by the file path.
            .ttl .tit .title | Title | Search by song title.
            
            \\<b\\>Numerical\\</b\\>
            .freq            | Frequency | Search by the average number of days between song plays.
            .pcnt .playcount | Play Count | Search by the playcount 
            .scnt .skipcount | Skip Count | Search by the skipcount 
            .size            | File Size | Search by file size, in KB.
            .rte .rating     | Rating | Search by the song rating, 0-5.
            \\</table\\>
            \\<table\\>
            \\<b\\>Advanced\\</b\\> | \\<b\\>Format\\</b\\> | \\<b\\>Description\\</b\\>
            .day        | number     | By number of days since last playing.
            .week       | number     | By number of weeks since last playing.
            .month      | number     | By number of months since last playing.
            .date       | YYYY/MM/DD | enter a specific date to search by. formatted by year-month-day
            .dateUS     | MM/DD/YYYY | see date. American date format
            .dateEU     | DD/MM/YYYY | see date. Sane people format.
            
            \\<b\\>Special\\</b\\>
            .sel | Selected | Display songs from the selection pool
            .preset # |  | This text is replaced with the text found in the given preset.
            .favorite | | Expands to a OR list of favorite artists. Set your favorite artists by right clicking their name in the Quick Selection tab
            \\</table\\>
            
        """
        # # 
        # #     given a unicode string formatted as a search string, parse, set the 3 tupples for this object
        # #     Parameters:
        # #         str: a user input str
        # # there are three types of searchs to perform
        # # "c" or contains    : target must contain any of these elements 
        # # "o" or boolean or  : target must contain at least one of these elements
        # # "n" or boolean not : target must contain none of these elements
        # # 
        # # format:
        # #   The following will be considered one search 'field':
        # # [.param] [.+!] [dir] term [ [.+!] [dir] term2 ...] [,;] ...
        # # where :
        # #   .param : search type, eg .date, defaults to .exif when not included
        # #   .+!    : AND,OR,NOT include the following term in search results
        # #   dir    : <=,<,=,>,=> can be used to specify comparison direction
        # #   term * : only mandatory string term, this will be compared against each song              
        # #   ,;     : these optionally end a field 
        # #            if multiply fields are wanted, they must be separated by a comma or semicolon
        # # 
        self._original = unicode(string) # create a copy of the string

        self._searchC = []
        self._searchO = []
        self._searchN = []
        self._searchX = [[]]
        
        self.termCount = 0;
        
        #expand preset modifiers into their expressions
        for i in range(10):
            string = self._expand_preset(string,i)
        # expand favorite modifier
        if string[1:].find("favorite") >= 0:
            result = ".art +"
            if string[0] == "*":
                result = ".art *"
            for art in SearchObject_Controller.getFavoriteArtistList():
                if len(art) > 0:
                    result += u" \"%s\""%(art)
            result += ';'
            string = string[1:].replace("favorite",result,1);
        
        # ########################################################
        # Begin Parsing User Input
         # quote first to protect anything the user wants protected.
        string = self.q.quote(string.lower())

        # split the user input string into frames
        R = stringSplit(string,",;")

        # for each field in the string break into terms
        for x in range(len(R)):
            field = R[x]            # the field is the entire string seperated by ;
            temp = field.split()
            if (len(temp) > 0):
                dword = temp[0]    # the dot word will be the first word prepended with a sigil
            else:
                continue;
            frame = field.replace(dword,"",1).strip()   # frame is everything but the dword
            key=""
            sigil = dword[0];
            if not dword[0].isalpha():
                key   = dword[1:]       #the dword with the sigil removed
           
            flag_type = EnumSong.EXIF
                
            if key == "sel":
                self._searchC.append( (".sel",EnumSong.SELECTED,0,None,None) )
                continue
            elif key == "spec":
                self._searchC.append( (".alt",EnumSong.SPECIAL,0,None,None) )
                continue
            elif key[:4] == "freq" and key[4:5] in "<=>" and key[4:5] != "": # a slice never throws an exception, but can return empty
                # allow $freqX , where X is <=>,
                fdict = {
                            '<' : EnumSong.SPEC_FREQ_L,
                            '=' : EnumSong.SPEC_FREQ_E,
                            '>' : EnumSong.SPEC_FREQ_G,
                        }
                fflag = {
                            '<' : SEARCH.LT,
                            '=' : SEARCH.EQ,
                            '>' : SEARCH.GT,
                        }
                ftype = {
                            '.' : 0,
                            '+' : SEARCH.OR,
                            '!' : SEARCH.NT,
                            '*' : SEARCH.IO,
                        }      
                        
                flag = fflag.get(key[4],0)|ftype.get(sigil,0)        
                        
                t = (key,fdict[key[4]],flag,getEpochTime( getNewDate() ),None) # TODO TIME LIB,and USE GET_EPOCH_TIME
                
                if sigil == ".":
                    self._searchC.append( t  ) 
                elif sigil == "+":
                    self._searchO.append( t  ) 
                elif sigil == "!":
                    self._searchN.append( t  ) 
                elif sigil == "*":
                    self._searchX.append( [t,]  ) 
                continue
            else: # get key or return the default value
                flag_type = SearchObject_Controller.getSearchDictionary().get(key,flag_type)
                
            # chop the .word search
            #print flag_type,frame
            if flag_type == EnumSong.EXIF:
                self._parseFrame(flag_type,field)
            else:
                self._parseFrame(flag_type,frame)
            #self._addTerms(flag_type,frame,S)

        self.termCount = len(self._searchC)+len(self._searchO)+len(self._searchN)
        for lst in self._searchX:
            self.termCount += len(lst)
        
    def match(self,song):
        """
            Return whether the given song matches the compiled search expression
            
            the a,b,c,d incrementers are for debug and can be removed later
        """
        c = True    # And
        o = False   # Or
        n = False   # Not
        x = True    # Inclusive or
        
        # check if the song matches all 'constant' terms
        for i in xrange(len(self._searchC)):
            c = self._compareSongElement(song,self._searchC[i])
            if not c:
                return False; # song did not match a AND term, so break out 
                
        # check that the song matches none of the 'not' terms
        for i in xrange(len(self._searchN)):
            n = self._compareSongElement(song,self._searchN[i])
            if n:
                return False; # song matched so break out 
                
        # ensure that song matches at least one 'or' term        
        if len(self._searchO) > 0:
            for i in xrange(len(self._searchO)):
                o = self._compareSongElement(song,self._searchO[i])
                if o:
                    break;     
        else:
            o = True

        #check X
        # searchX is a set of lists
        # a song must match as least one item in each list for each set.
        if len(self._searchX[0]) > 0:
            for i in xrange(len(self._searchX)):
                t = False
                for j in xrange(len(self._searchX[i])):
                    t = self._compareSongElement(song,self._searchX[i][j])
                    if t:
                        break;  
                if not t: 
                    x = False;
                    break;
        
        return o and x;
        
    def search(self,songList):
        """
            given a list of music R
            search through the entire list and return
            a new list of all songs that match the compiled search string
            
            using the timer on my machine this function takes 17ms for 3000 songs (average, 3 terms)
            for referance an entire search takes 22ms, 5ms to compile, 17 to search
        """
        S = [[]]*len(songList)

        index = 0
        
        #time = datetime.datetime.now()
        
        for song in songList:

            if self.match(song):
                S[index] = song
                index += 1
            
        #end = datetime.datetime.now()
        #print "Search Time: %s\n"%(end-time) 
        return S[:index]

    def searchN(self,songList=None,N=100):
        """
            Function: searchN
            call this method with a song list and number N
            the songs that match from thefirst N in the list will be returned
            
            then, call this function with no arguments
            each time the function is called the songs that match in the next set of N
            will be returned.
            
            example
            
            so = SearchObject(".pcnt < 10")
            temp = so.searchN(library,50)
            result = []                         # list of songs that match
            while temp != None:
                result += temp                  # append the matching songs to the end of the resulting song list
                print len(temp)                 # print the number of songs that matched the last time searchN was called.
                temp = so.searchN()             # compare the next 50 songs
            print len(result)                   # print the number of songs that matched the search
                
        """
        if songList != None:
            # initialize the search iteration
            self.search_iter_index = 0
            self.search_iter_list = songList
            self.search_iter_N = N
        
        iter_end = self.search_iter_index + self.search_iter_N

        S = [[]]*self.search_iter_N # init the resulting array to the maximum number of values that could be found
        
        count = 0;
        
        # look through the Next N songs
        while self.search_iter_index < iter_end and self.search_iter_index < len(self.search_iter_list):
            song = self.search_iter_list[self.search_iter_index]
            
            if self.match(song):
                S[count] = song
                count += 1;
                
            self.search_iter_index += 1
        
        # return none when iterating through the list is done
        if self.search_iter_index >= len(self.search_iter_list) and count == 0:
            return None;
        # otherwise return any songs found. this could be zero.
        return S[:count]
        
    def _expand_preset(self,string,preset):
        p = ".preset %d"%preset
        if string.find(p) > -1:
            string = string.replace(p,SearchObject_Controller.getPresetString(preset))
        return string
        
    def _compareSongElement(self,song,element):
        """
            compare a single song to a single compiled term
            the actual comparrison may need to convert the format
            of the song element first.
        """
        # song:
        #   a single song record.
        # element: 
        #   a tupple in form from compileSearchString()
        # return:
        #   True, song matches element, or False
        os = 0 # original string
        st = 1 # search type
        dm = 2 # direction
        cf = 3 # compiled form
        rf = 4 # alternate value for comparing ( of same type to cf )
        
        # RETRANSLATE TO OLD STYLE FORMAT
        # TODO: REMOVE THIS
        flag_dir  = element[dm]
        flag_type = element[st]
        #if    element[2]&SEARCH.GE==SEARCH.GE: flag_dir = EnumSong.GTEQUAL
        #elif  element[2]&SEARCH.LE==SEARCH.LE: flag_dir = EnumSong.LTEQUAL
        #elif  element[2]&SEARCH.GT           : flag_dir = EnumSong.GREATERTHAN
        #elif  element[2]&SEARCH.LT           : flag_dir = EnumSong.LESSTHAN
        #elif  element[2]&SEARCH.EQ           : flag_dir = EnumSong.EQUAL
        #else                                 : flag_dir = EnumSong.CONTAINS
        #element = (element[0],element[1],flag_dir,element[3],element[4])
        
        # split this function into special cases, 
        # then all string elements
        # then all number elements
        try:
            if flag_type == EnumSong.SELECTED :
                return song[EnumSong.SELECTED]
                
            elif flag_type == EnumSong.SPECIAL :
                return song[EnumSong.SPECIAL]
                
            elif flag_type == EnumSong.SPEC_FREQ_G :

                old=song[EnumSong.DATEVALUE]
                if old != 0:
                    d =  max(1, int(float(element[cf] - old)/(60*60*24)) )
                else: 
                    d = 0;
                return d > song[EnumSong.FREQUENCY];
                
            elif flag_type == EnumSong.SPEC_FREQ_L :

                old=song[EnumSong.DATEVALUE]
                if old != 0:
                    d =  max(1, int(float(element[cf] - old)/(60*60*24)) )
                else: 
                    d = 0;
                return d < song[EnumSong.FREQUENCY];
            
            elif flag_type == EnumSong.SPEC_FREQ_E :

                old=song[EnumSong.DATEVALUE]
                if old != 0:
                    d =  max(1, int(float(element[cf] - old)/(60*60*24)) )
                else: 
                    d = 0;
                return d == song[EnumSong.FREQUENCY];
                
            elif flag_type == EnumSong.PATH :
                if flag_dir&SEARCH.EQ:
                    #return song[EnumSong.PATH].find(element[cf]) == 0
                    return comparePathLength(element[cf],song[EnumSong.PATH])
                else:
                    return comparePartInPath(song[EnumSong.PATH],element[cf])  
                    
            elif flag_type == EnumSong.DATESTAMP:
                # dates less than means time is greater
                # set or EnumSong.CONTAINS as default
                # defaults to >=, ex, not played fro x days or more
                if flag_dir&SEARCH.LT: # more recent
                    return (song[EnumSong.DATEVALUE] >=  element[cf])
                elif flag_dir&SEARCH.EQ==SEARCH.EQ : # equals one specific day
                    return (song[EnumSong.DATEVALUE] >= element[cf] and song[EnumSong.DATEVALUE] <= element[rf])
                else:   # older than date
                    return (song[EnumSong.DATEVALUE] <= element[cf])
                    
            elif flag_type == EnumSong.DATEADDED:
                # dates less than means time is greater
                # set or EnumSong.CONTAINS as default
                # defaults to >=, ex, not played fro x days or more
                if flag_dir&SEARCH.LT: # more recent
                    return (song[EnumSong.DATEADDED] >=  element[cf])
                elif flag_dir&SEARCH.EQ==SEARCH.EQ : # equals one specific day
                    return (song[EnumSong.DATEADDED] >= element[cf] and song[EnumSong.DATEADDED] <= element[rf])
                else:   # older than date
                    return (song[EnumSong.DATEADDED] <= element[cf])
                    
            elif flag_type < EnumSong.STRINGTERM :
                # contains, the element must be anywhere
                #  ex: 'st' will match 'stone' and 'rockstar'
                # equals the entered text must equal the equivalent length in the song
                #  ex: 'st' will match 'stone' but not 'rockstar'
                if flag_dir&SEARCH.EQ and flag_type != EnumSong.EXIF:
                    return song[flag_type].lower().find(element[cf]) == 0
                else:
                    return song[flag_type].lower().find(element[cf]) >= 0
     
            elif flag_type >= EnumSong.STRINGTERM and element[st] < EnumSong.NUMTERM :
                if   flag_dir&SEARCH.LE == SEARCH.LE : return song[flag_type] <= element[cf]
                elif flag_dir&SEARCH.LT              : return song[flag_type] <  element[cf]
                elif flag_dir&SEARCH.GE == SEARCH.GE : return song[flag_type] >= element[cf]
                elif flag_dir&SEARCH.GT              : return song[flag_type] >  element[cf]
                elif flag_dir&SEARCH.EQ              : return song[flag_type] == element[cf]
                
        except Exception as e:
            print "Error: [%s] %s"%(EnumSong.exifToString(flag_type),e.args)
            print song
            print element
        return False;    
        
    def _parseFrame(self,type,frame):
        # parse Frame looks for special characters
        # and then sets the appropriate bit flag.
        # the following doc_string is used in auto generating the help file.
        """
            Special Characters: . & + ! *

            \\<b\\>About Special Characters:\\</b\\>
                Special characters are used to decorate the beginning of a word.  Each one raises a different flag, changing how the search interpreter will interpret the next word. By default the 'AND' flag is in effect and can be changed to 'NOT' with a '!' or to an 'OR' flag with '+'. A Flag is in effect until a new special character is found and is reset to 'AND' each time a ',' (comma) or ';' semicolon is found.

            \\<b\\>'.' '&' AND:\\</b\\>
                Words grouped by the 'AND' flag must be found somewhere in the tags for the song to be included in the search results.
                This flag is set by default, and it is not required to ne explicitly set this flag. Both '.' and '&' can be used to change the flag back to 'AND'. 
                Note that this character is also governed by a special case. the '.' is also used to denote dot-words. In the case that a period is found before a word, and that word is the first word in the frame that world will be considered a dot-word, instead of as a flagged search term.
                
            \\<b\\>2. '!' NOT:\\</b\\>    
                This flag is the opposite of 'AND'. Songs that contain any word or value matching the entered word or value will NOT be included in the search results.
             
            \\<b\\>3. '+' OR:\\</b\\>
                Use this flag to create a list of parameters that could be included in the songs tags. If a song does not match any of the OR terms it will not be included in the search results.
              
            \\<b\\>4. '*' SET INCLUSIVE OR:\\</b\\>
                This flag is similar to 'OR' but with 1 major distinction. Individual frames are broken up into exclusive sets. A song will only be included in the search results if it matches at least one term in each set.
                keywords .art .artist, etc
                hook, unhook to keyhook 1/0

            \\<b\\>By Example:\\</b\\>
                Removing a set of results:
                    ".rte !5;"
                    Removes all songs with a rating of 5 from the results
                    
                OR Vs. SET INCLUSIVE OR:
                
                    Consider these two searchs:
                    
                        1. ".alb +core dust; .rte +=2 = 4"
                        2. ".alb *core dust; .rte *=2 = 4"
                        
                    In the first case all songs from both listed albums will be included, 
                    as well as all songs with a rating equal to 2 or 4.
                    In the second case all of the songs from both albums will be included,
                    BUT only if those songs were given a rating of 2 or 4 stars.
                    
                    There are of course other ways to get to the same result, for example:
                    
                        3. ".alb +core dust; .rte >=2 !3 5"
                        
                        same as 1, but includes all ratings equal to or above 2, then
                        removes all ratings equal to 3 and 5
                    
                    The differences between OR and SET INCLUSIVE OR are small, 
                    and can be very confusing. experiment!
        """
        
        # frames as string with search type removed.
        # eg frame = "+>4 1" i.e. rte equals 1 or greater than 4.
        KEYS = ".&!+*<>="
        flag = 0;
        R = frame.split();  # split the frame on whitespace
        ST = ~(SEARCH.MOD) # bit mask that clears OR and NT on '&'
        SD = ~(SEARCH.LT|SEARCH.GT) # bit mask that clears LT and GT on '&'
        for string in R:
            
            while len(string) > 0 and string[0] in KEYS :
                if   string[0] == "+": flag  = (flag&ST)|SEARCH.OR# set OR
                elif string[0] == "!": flag  = (flag&ST)|SEARCH.NT# set NT
                elif string[0] == ".": flag &= ST                 # clr OR, NT, IO
                elif string[0] == "&": flag &= ST                 # clr OR, NT, IO
                elif string[0] == "<": flag  = (flag&SD)|SEARCH.LT# set LT    
                elif string[0] == ">": flag  = (flag&SD)|SEARCH.GT# set GT
                elif string[0] == "=": flag ^= SEARCH.EQ          # set EQ
                elif string[0] == "*": 
                    # set IO and create the new set
                    flag  = (flag&ST)|SEARCH.IO
                    if len(self._searchX[-1]) > 0:
                        self._searchX.append([]) 
                    
                string = string[1:] #shift
            
            if len(string) != 0: 

                # now that the string has been fully processed for control
                # characters return it to the original form if needed
                string = self.q.unquote(string)

                #print "FLAGS: %-10s STRING: %s;"%(SEARCH(flag),string)
                
                self._compileTerm(type,flag,string)
   
                flag &= 0xF0;
                
            #else:
            #    print "FLAGS: %-10s;"%(SEARCH(flag))
        return;
        
    def _compileTerm(self,flag_type,flag,ostr):
        """
            flag_type: either EXIF, ARTIST,PLAYCOUNT ETC
            flag     : numeric as defined in SEARCH class
            ostr     : relevant string term for a search of flag_type
        """
        if ostr == "":
            return None
        ostr = unicode(ostr) 
        cf = ostr[:]
        rf = None;
 
        if (flag_type == EnumSong.SPEC_DATESTD ) :
            cf = getSecondsFromDateFormat(cf,flag_type)
            rf = cf + 24*60*60
            if cf == 0:
                return None
            ostr = normalizeDateFormat(ostr,flag_type)
            
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
                
            flag_type = EnumSong.DATESTAMP # change type to standard date format
        elif (flag_type == EnumSong.SPEC_DATEEU ) :
            cf = getSecondsFromDateFormat(cf,flag_type)
            rf = cf + 24*60*60
            if cf == 0:
                return None
            ostr = normalizeDateFormat(ostr,flag_type)
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = EnumSong.DATESTAMP # change type to standard date format   
        elif (flag_type == EnumSong.SPEC_DATEUS ) :
            cf = getSecondsFromDateFormat(cf,flag_type)
            rf = cf + 24*60*60
            if cf == 0:
                return None
            ostr = normalizeDateFormat(ostr,flag_type)
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = EnumSong.DATESTAMP # change type to standard date format
        elif (flag_type == EnumSong.SPEC_MONTH ) :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = EnumSong.DATESTAMP
            cf = getCurrentTime()
            try :
                cf -= 30*int(ostr)*24*60*60
                rf = cf + 28*24*60*60
                ostr = "month: %s"%ostr
            except:
                pass   
        elif (flag_type == EnumSong.SPEC_WEEK ) :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = EnumSong.DATESTAMP
            cf = getCurrentTime()
            try :
                cf -= 7*int(ostr)*24*60*60
                rf = cf + 7*24*60*60
                ostr = "week: %s"%ostr
            except:
                pass        
        elif (flag_type == EnumSong.DATESTAMP) :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            cf = getCurrentTime()
            try :
                cf -= int(ostr)*24*60*60
                rf = cf + 24*60*60
                ostr = "day: %s"%ostr
            except:
                pass
        elif (flag_type == EnumSong.DATEADDED) :
            cf = getSecondsFromDateFormat(cf,EnumSong.SPEC_DATESTD)
            rf = cf + 24*60*60
            if cf == 0:
                return None
            ostr = normalizeDateFormat(ostr,EnumSong.SPEC_DATESTD)
            
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
                
        elif (flag_type == EnumSong.PATH ) :
            if cf == u"":
                return None
            rf = None
        
        elif (flag_type == EnumSong.LENGTH ):
            cf = 0;
            try:
                cf = convertStringToTime(ostr)
            except:
                pass
        elif flag_type >= EnumSong.STRINGTERM and flag_type < EnumSong.NUMTERM :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.EQ
            try:
                cf = int(cf)
            except:
                cf = 0
                return None
            rf = None
        
        term = (ostr,flag_type,flag,cf,rf)

        flag_mod = flag&SEARCH.MOD

        if   flag_mod == SEARCH.OR : self._searchO.append(term);
        elif flag_mod == SEARCH.NT : self._searchN.append(term);
        elif flag_mod == SEARCH.IO : self._searchX[-1].append(term);
        else                       : self._searchC.append(term);

    def __unicode__(self):
        string = ""
        for term in self._searchC:
            s = term[3] if (term[1] != EnumSong.DATESTAMP) else term[0]
            string += "%s %s %s\n"%(EnumSong.exifToString(term[1]),SEARCH(term[2]),s)
        for term in self._searchO:
            s = term[3] if (term[1] != EnumSong.DATESTAMP) else term[0]
            string += "%s %s %s\n"%(EnumSong.exifToString(term[1]),SEARCH(term[2]),s)
        for term in self._searchN:
            s = term[3] if (term[1] != EnumSong.DATESTAMP) else term[0]
            string += "%s %s %s\n"%(EnumSong.exifToString(term[1]),SEARCH(term[2]),s)
        i=1;    
        for lst in self._searchX:
            
            for term in lst:
                s = term[3] if (term[1] != EnumSong.DATESTAMP) else term[0]
                string += "%s %s %d %s\n"%(EnumSong.exifToString(term[1]),SEARCH(term[2]),i,s)
            i+=1;
        return string
    
    def __str__(self):
        return "<SearchObject>"
    
    def debug(self):
        print self._searchC
        print self._searchO
        print self._searchN
        print self._searchX

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
    
def getCurrentTime():
    """return seconds since epoch"""
    return timegm(time.localtime(time.time()))    
   
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
        
    if format == EnumSong.SPEC_DATESTD:
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
    if format == EnumSong.SPEC_DATEEU:
        dateFormat = "%d/%m/%Y"
    elif format == EnumSong.SPEC_DATEUS:
        dateFormat = "%m/%d/%Y"
        
    datetime = None

    try:
        datetime = time.strptime(date,dateFormat)
        return timegm(datetime)   
    except:
        pass
        
    return 0
   
def getNewDate():
    """return a new formatted time string"""
    datetime = time.localtime(time.time())
    return time.strftime("%Y/%m/%d %H:%M",datetime)
   
def getEpochTime( date ):
    """return epoch time for a date"""
    datetime = None
    try:
        datetime = time.strptime(date,"%Y/%m/%d %H:%M")
        return timegm(datetime)   
    except:
        pass
        
    return 0  

#__all__  = ["SearchObject_Controller","SearchObject"]
  
if __name__ == "__main__":
    print "Debug Search"
    #so = SearchObject(".day 5");
    #so = SearchObject(".len 60");
    so = SearchObject(".dateeu 11/12/12");
    so.debug();
    
    
    