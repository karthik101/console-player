
from collections import namedtuple
SearchTerm = namedtuple("SearchTerm",'str typ dir cf rf') #TODO use these instead of just tuples

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
        self.a=0; # the only way to debug match() effectivley
        self.b=0; # is to increment these counters, one each for C O N X
        self.c=0;
        self.d=0;
        
        self.q = StringQuote()
        self.q.quoteable = '"'  # only quote items wrapped in double quotes
        
        self._original = unicode(string) # create a copy of the string

        self._searchC = []
        self._searchO = []
        self._searchN = []
        self._searchX = [[]]
        
        self.termCount = 0;
        
        
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
            for art in Settings.FAVORITE_ARTIST:
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
            key   = dword[1:]       #the dword with the sigil removed
           
            flag_type = MpMusic.EXIF
                
            if key == "sel":
                self._searchC.append( (".sel",MpMusic.SELECTED,0,None,None) )
                continue
            elif key == "spec":
                self._searchC.append( (".alt",MpMusic.SPECIAL,0,None,None) )
                continue
            else: # get key or return the default value
                flag_type = MpMusic.D_StrToDec.get(key,flag_type)
                
            # chop the .word search
            #print flag_type,frame
            if flag_type == MpMusic.EXIF:
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
        
        # check if the song matches all constant terms
        for i in xrange(len(self._searchC)):
            c = self._compareSongElement(song,self._searchC[i])
            if not c:
                return False; # song did not match a AND term, so break out 
            else:
                self.a+=1;
                
        # check that the song matches none of the not terms
        for i in xrange(len(self._searchN)):
            n = self._compareSongElement(song,self._searchN[i])
            if n:
                self.c+=1;
                return False; # song matched so break out 
                
        # ensure that song matches at least one or term        
        if len(self._searchO) > 0:
            for i in xrange(len(self._searchO)):
                o = self._compareSongElement(song,self._searchO[i])
                if o:
                    self.b+=1
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
                        self.d+=1
                        break;  
                if not t: 
                    x = False;
                    break;
        
        return o and x;
        
    def search(self,R):
        """
            given a list of music R
            search through the entire list and return
            a new list of all songs that match the compiled search string
            
            using the timer on my machine this function takes 17ms for 3000 songs (average, 3 terms)
            for referance an entire search takes 22ms, 5ms to compile, 17 to search
        """
        S = [[]]*len(R)

        index = 0
        
        time = datetime.datetime.now()
        
        self.a=0; # the only way to debug match() effectivley
        self.b=0; # is to increment these counters, one each for C O N X
        self.c=0;
        self.d=0;
        
        for i in xrange(len(R)):
        
            song = R[i]
            
            if self.match(song):
                S[index] = song
                index += 1

            if i%Settings.SEARCH_STALL == 0:   # SEARCH_STALL controls how often to pause
                MpGlobal.Application.processEvents() # pause this to update application

        if MpGlobal.DIAG_SONGMATCH:
            print "A: %d"%self.a
            print "B: %d"%self.b
            print "C: %d"%self.c
            print "D: %d\n"%self.d
            
        end = datetime.datetime.now()
        diagMessage( MpGlobal.DIAG_SEARCH, "Search Time: %s\n"%(end-time) )
        return S[:index]

    def _expand_preset(self,string,preset):
        p = ".preset %d"%preset
        if string.find(p) > -1:
            string = string.replace(p,Settings.getPreset(preset))
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
        #if    element[2]&SEARCH.GE==SEARCH.GE: flag_dir = MpMusic.GTEQUAL
        #elif  element[2]&SEARCH.LE==SEARCH.LE: flag_dir = MpMusic.LTEQUAL
        #elif  element[2]&SEARCH.GT           : flag_dir = MpMusic.GREATERTHAN
        #elif  element[2]&SEARCH.LT           : flag_dir = MpMusic.LESSTHAN
        #elif  element[2]&SEARCH.EQ           : flag_dir = MpMusic.EQUAL
        #else                                 : flag_dir = MpMusic.CONTAINS
        #element = (element[0],element[1],flag_dir,element[3],element[4])
        
        # split this function into special cases, 
        # then all string elements
        # then all number elements
        try:
            if flag_type == MpMusic.SELECTED :
                return song[MpMusic.SELECTED]
                
            elif flag_type == MpMusic.SPECIAL :
                return song[MpMusic.SPECIAL]
                
            elif flag_type == MpMusic.PATH :
                if flag_dir&SEARCH.EQ:
                    #return song[MpMusic.PATH].find(element[cf]) == 0
                    return comparePathLength(element[cf],song[MpMusic.PATH])
                else:
                    return comparePartInPath(song[MpMusic.PATH],element[cf])  
                    
            elif flag_type == MpMusic.DATESTAMP:
                # dates less than means time is greater
                # set or MpMusic.CONTAINS as default
                # defaults to >=, ex, not played fro x days or more
                if flag_dir&SEARCH.LT: # more recent
                    return (song[MpMusic.DATEVALUE] >=  element[cf])
                elif flag_dir&SEARCH.EQ==SEARCH.EQ : # equals one specific day
                    return (song[MpMusic.DATEVALUE] >= element[cf] and song[MpMusic.DATEVALUE] <= element[rf])
                else:   # older than date
                    return (song[MpMusic.DATEVALUE] <= element[cf])
                    
            elif flag_type < MpMusic.STRINGTERM :
                # contains, the element must be anywhere
                #  ex: 'st' will match 'stone' and 'rockstar'
                # equals the entered text must equal the equivalent length in the song
                #  ex: 'st' will match 'stone' but not 'rockstar'
                if flag_dir&SEARCH.EQ and flag_type != MpMusic.EXIF:
                    return song[flag_type].lower().find(element[cf]) == 0
                else:
                    return song[flag_type].lower().find(element[cf]) >= 0
     
            elif flag_type >= MpMusic.STRINGTERM and element[st] < MpMusic.NUMTERM :
                if   flag_dir&SEARCH.LE == SEARCH.LE : return song[flag_type] <= element[cf]
                elif flag_dir&SEARCH.LT              : return song[flag_type] <  element[cf]
                elif flag_dir&SEARCH.GE == SEARCH.GE : return song[flag_type] >= element[cf]
                elif flag_dir&SEARCH.GT              : return song[flag_type] >  element[cf]
                elif flag_dir&SEARCH.EQ              : return song[flag_type] == element[cf]
                
        except Exception as e:
            print "Error: [%s] %s"%(MpMusic.exifToString(flag_type),e.args)
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

        if (flag_type == MpMusic.SPEC_DATESTD ) :
            cf = getSecondsFromDateFormat(cf,flag_type)
            rf = cf + 24*60*60
            if cf == 0:
                return None
            ostr = normalizeDateFormat(ostr,flag_type)
            
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
                
            flag_type = MpMusic.DATESTAMP # change type to standard date format
        elif (flag_type == MpMusic.SPEC_DATEEU ) :
            cf = getSecondsFromDateFormat(cf,flag_type)
            rf = cf + 24*60*60
            if cf == 0:
                return None
            ostr = normalizeDateFormat(ostr,flag_type)
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = MpMusic.DATESTAMP # change type to standard date format   
        elif (flag_type == MpMusic.SPEC_DATEUS ) :
            cf = getSecondsFromDateFormat(cf,flag_type)
            rf = cf + 24*60*60
            if cf == 0:
                return None
            ostr = normalizeDateFormat(ostr,flag_type)
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = MpMusic.DATESTAMP # change type to standard date format
        elif (flag_type == MpMusic.SPEC_MONTH ) :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = MpMusic.DATESTAMP
            cf = getCurrentTime()
            try :
                cf -= 30*int(ostr)*24*60*60
                rf = cf + 28*24*60*60
                ostr = "month: %s"%ostr
            except:
                pass
            
        elif (flag_type == MpMusic.SPEC_WEEK ) :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            flag_type = MpMusic.DATESTAMP
            cf = getCurrentTime()
            try :
                cf -= 7*int(ostr)*24*60*60
                rf = cf + 7*24*60*60
                ostr = "week: %s"%ostr
            except:
                pass
                
        elif (flag_type == MpMusic.DATESTAMP) :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.GT
            cf = getCurrentTime()
            try :
                cf -= int(ostr)*24*60*60
                rf = cf + 24*60*60
                ostr = "day: %s"%ostr
            except:
                pass

        elif (flag_type == MpMusic.PATH ) :
            if cf == u"":
                return None
            rf = None
        elif (flag_type == MpMusic.LENGTH ):
            cf = 0;
            try:
                cf = convertStringToTime(ostr)
            except:
                pass
        elif flag_type >= MpMusic.STRINGTERM and flag_type < MpMusic.NUMTERM :
            if flag&SEARCH.DIR == 0:# if no DIR flags set, set EQ flag
                flag = flag|SEARCH.EQ
            try:
                cf = int(cf)
            except:
                cf = 0
                return None
            rf = None
        
        term = (ostr,flag_type,flag,cf,rf)

        flag_mod = term[2]&SEARCH.MOD
        
        if term != None:   
            if   flag_mod == SEARCH.OR : self._searchO.append(term);
            elif flag_mod == SEARCH.NT : self._searchN.append(term);
            elif flag_mod == SEARCH.IO : self._searchX[-1].append(term);
            else                       : self._searchC.append(term);

    def __unicode__(self):
        string = ""
        for term in self._searchC:
            s = term[3] if (term[1] != MpMusic.DATESTAMP) else term[0]
            string += "%s %s %s\n"%(MpMusic.exifToString(term[1]),SEARCH(term[2]),s)
        for term in self._searchO:
            s = term[3] if (term[1] != MpMusic.DATESTAMP) else term[0]
            string += "%s %s %s\n"%(MpMusic.exifToString(term[1]),SEARCH(term[2]),s)
        for term in self._searchN:
            s = term[3] if (term[1] != MpMusic.DATESTAMP) else term[0]
            string += "%s %s %s\n"%(MpMusic.exifToString(term[1]),SEARCH(term[2]),s)
        i=1;    
        for lst in self._searchX:
            
            for term in lst:
                s = term[3] if (term[1] != MpMusic.DATESTAMP) else term[0]
                string += "%s %s %d %s\n"%(MpMusic.exifToString(term[1]),SEARCH(term[2]),i,s)
            i+=1;
        return string
    
    def __str__(self):
        return "<SearchObject>"
    
    def debug(self):
        print self._searchC
        print self._searchO
        print self._searchN
        print self._searchX

        
def searchSetSelection(string,sel=True):
    so = SearchObject(string)
    
    MpGlobal.Player.selCount = 0
    count = 0 # total count of new songs found
    
    for song in MpGlobal.Player.library:
    
        if so.match(song):
            song[MpMusic.SELECTED] = sel
            count += 1
        
        if song[MpMusic.SELECTED] == True:
            MpGlobal.Player.selCount += 1
    
    UpdateStatusWidget(0,MpGlobal.Player.selCount)
    
    return count # return the number of songs that matched the input string.
    
    
    
    
    
from calendar import timegm
import os
import time
import datetime
import random
import re
import subprocess
import ctypes
 
from StringQuoter import *    
from MpGlobalDefines import *
from Song_Object import Song
from datatype_hex64 import *
from MpFileAccess import *
from SystemPathMethods import *
from MpScripting import *
    
    
    
    
    
    
    
    
    
    
    
    