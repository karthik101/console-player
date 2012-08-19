#! python $this
import re

_consonants_ = set(__import__('string').ascii_lowercase) - set("aeiou")

class Translate(object):
    """ Use this object to convert a user input string from plain ascii
        phonetics to hiragana or katakana. if string is from a QLineEdit
        this is as easy as passing the string to this object. setting
        the text of the lineedit to nstring, then calling QLineEdit.cursorBackward
        with the argument Translate.rposition to reset the cursor
    """
    Hiragana = None;
    Katakana = None;
    
    def __init__(self,unistr):
    
        self.ostring = u""       # the original string
        self.nstring = u""       # the resulting string
        self.rstring = ""        # roman string, no kana
        self.position = 0        # index after the last change
                            # where the cursor should be moved to
        self.rposition = 0       # positon from the right edge of the string
        self.success = False     # whether anything changed
    
        self.ostring = unicode(unistr)# force type to unicode
        self.nstring = unicode(unistr)
        self.rstring = unicode(unistr)
        
        # old refers to inserting ascii letters next unicode characters
        # that were already in the string
        mk_old = re.search(ur"[\u30A0-\u30ff][a-z|\-]+",self.ostring)
        mh_old = re.search(ur"[\u3040-\u309f][a-z|\*]+",self.ostring)
        
        # new refers to finding two semicolons or colons, and replaceing
        # that, and the following ascii with kana
        mk_new = re.search(r";;[a-z|\-]+",self.ostring)
        mh_new = re.search(r"::[a-z|\*]+",self.ostring)
        
        if mk_old != None:
            substr = mk_old.group(0)[1:]
            repstr = self.convertToKatakana(substr)
            if repstr:  # if a conversion was possible repstr will not be empty
                # set the new string equal to the oldstring, replaced with the new kana
                self.nstring = self.nstring.replace(mk_old.group(0)[1:],repstr)
                # calculate the end position of the change
                self.position = self.ostring.index(substr) + len(repstr)
                # set that a change was made
                self.success = True
            
        if mh_old != None:
            substr = mh_old.group(0)[1:]
            repstr = self.convertToHiragana(substr)
            if repstr:
                self.nstring = self.nstring.replace(mh_old.group(0)[1:],repstr)
                self.position = self.ostring.index(substr) + len(repstr)
                self.success = True
        
        if mk_new != None:
            substr = mk_new.group(0)[2:]
            repstr = self.convertToKatakana(substr)
            if repstr:
                self.nstring = self.nstring.replace(mk_new.group(0),repstr)
                self.position = self.ostring.index(substr) + len(repstr)
                self.success = True
            
        if mh_new != None:
            substr = mh_new.group(0)[2:]
            repstr = self.convertToHiragana(substr)
            if repstr:
                self.nstring = self.nstring.replace(mh_new.group(0),repstr)
                self.position = self.ostring.index(substr) + len(repstr)
                self.success = True
        # calculate the distance from the end of the str to the last character changed        
        self.rposition = len(self.nstring) - self.position
        
        # ######################################################
        rek = re.compile(ur"[\u30A0-\u30ff]")
        reh = re.compile(ur"[\u3040-\u309f]")
        
        m = rek.search(self.rstring)
        while m != None:
            self.rstring = self.rstring.replace(m.group(0),self.unicharToKatakana(m.group(0)))
            m = rek.search(self.rstring)
            
        m = reh.search(self.rstring)    
        while m != None:
            self.rstring = self.rstring.replace(m.group(0),self.unicharToHiragana(m.group(0)))
            m = reh.search(self.rstring)
    def compile(self,string):
        pass

    def codePoint(self,unichar):
        """ given a single character return the integer
            code point for it. if it is not a unicode char
            that fits the scheme \uXXXXY, which all japanese
            kana can fit in, then return 0
        """
        
        string = unichar.encode('unicode-escape')
        
        try:    # if for some reason the cast fails to find an int
            if len(string) == 6:
                return int(string[2:])
        except:
            pass
            
        return 0
    
    def convertToHiragana(self,string):
        nstr = u""
        match = 0
        kana = u""
        while len(string) > 0 :
            # test portions of the string to see if they
            # can be translated into Japanese. start with a 3 character
            # chunk, work down to a single character. cut away matches
            # or remove a single character then repeat until the string
            # is empty
            match = 0
            kana = u""
            for i in range(3,0,-1):
                kana = self.substringToHiragana(string[0:i])
                if kana != u"":
                    match = i
                    break
            # cut out the matched portion of the string
            # or cut out a single character
            if match > 0 :
                #if there was a match add it to the new str
                nstr += kana
                string = string[match:]
            else:
                string = string[1:]
               
        return nstr
        
    def convertToKatakana(self,string):
        """ convert the given string to katakana characters
            if the letter can not be translated it will be lost
        """
        nstr = u""
        match = 0
        kana = u""
        while len(string) > 0 :
            # test portions of the string to see if they
            # can be translated into Japanese. start with a 3 character
            # chunk, work down to a single character. cut away matches
            # or remove a single character then repeat until the string
            # is empty
            match = 0
            kana = u""
            for i in range(3,0,-1):
                kana = self.substringToKatakana(string[0:i])
                if kana != u"":
                    match = i
                    break
            # cut out the matched portion of the string
            # or cut out a single character
            if match > 0 :
                #if there was a match add it to the new str
                nstr += kana
                string = string[match:]
            else:
                string = string[1:]
               
        return nstr
       
    def substringToHiragana(self,substr): 
        """transliterate the ascii letters to an the equivalent
            character in Hiragana"""
        # substring as ascii
        if substr in Translate.Hiragana:
            return Translate.Hiragana[substr]
        if substr == "n": #TODO this special case must be tested, added 7/29/2012
            return Translate.Katakana['nn']
        if substr in _consonants_: #TODO this special case must be tested, added 7/29/2012 
            return Translate.Katakana['dd']
        return u""
    
    def substringToKatakana(self,substr): 
        """transliterate the ascii letters to an the equivalent
            character in Katakana"""
        # substring as ascii
        if substr in Translate.Katakana:
            return Translate.Katakana[substr]
        if substr == "n": #TODO this special case must be tested, added 7/29/2012 
            return Translate.Katakana['nn']
        if substr in _consonants_: #TODO this special case must be tested, added 7/29/2012 
            return Translate.Katakana['dd']
            
        return u""
        
    def unicharToHiragana(self,unichar):
        """
            given a unicode character return its ascii equivalent
        """
        for key in Translate.Hiragana:
            if Translate.Hiragana[key] == unichar :
                return key
        return u""
        
    def unicharToKatakana(self,unichar):
        """
            given a unicode character return its ascii equivalent
        """
        for key in Translate.Katakana:
            if Translate.Katakana[key] == unichar :
                return key
        return u""
    
def init_KanaTables():    
    """
        dictionary version
    """
    Hiragana = {}
    Katakana = {}
    
    Hiragana["a"   ] = u"\u3042"
    Hiragana["i"   ] = u"\u3044"
    Hiragana["u"   ] = u"\u3046"
    Hiragana["e"   ] = u"\u3048"
    Hiragana["o"   ] = u"\u304a"
    Hiragana["ka"  ] = u"\u304b"
    Hiragana["ki"  ] = u"\u304d"
    Hiragana["ku"  ] = u"\u304f"
    Hiragana["ke"  ] = u"\u3051"
    Hiragana["ko"  ] = u"\u3053"
    Hiragana["kya" ] = u"\u304d\u3083"
    Hiragana["kyu" ] = u"\u304d\u3085"
    Hiragana["kyo" ] = u"\u304d\u3087"
    Hiragana["sa"  ] = u"\u3055"
    Hiragana["shi" ] = u"\u3057"
    Hiragana["su"  ] = u"\u3059"
    Hiragana["se"  ] = u"\u305b"
    Hiragana["so"  ] = u"\u305d"
    Hiragana["sha" ] = u"\u3057\u3083"
    Hiragana["shu" ] = u"\u3057\u3085"
    Hiragana["sho" ] = u"\u3057\u3087"
    Hiragana["ta"  ] = u"\u305f"
    Hiragana["chi" ] = u"\u3061"
    Hiragana["tsu" ] = u"\u3064"
    Hiragana["te"  ] = u"\u3066"
    Hiragana["to"  ] = u"\u3068"
    Hiragana["cha" ] = u"\u3061\u3083"
    Hiragana["chu" ] = u"\u3061\u3085"
    Hiragana["cho" ] = u"\u3061\u3087"
    Hiragana["na"  ] = u"\u306a"
    Hiragana["ni"  ] = u"\u306b"
    Hiragana["nu"  ] = u"\u306c"
    Hiragana["ne"  ] = u"\u306d"
    Hiragana["no"  ] = u"\u306e"
    Hiragana["nya" ] = u"\u306b\u3083"
    Hiragana["nyu" ] = u"\u306b\u3085"
    Hiragana["nyo" ] = u"\u306b\u3087"
    Hiragana["ha"  ] = u"\u306f"
    Hiragana["hi"  ] = u"\u3072"
    Hiragana["fu"  ] = u"\u3075"
    Hiragana["he"  ] = u"\u3078"
    Hiragana["ho"  ] = u"\u307b"
    Hiragana["hya" ] = u"\u3072\u3083"
    Hiragana["hyu" ] = u"\u3072\u3085"
    Hiragana["hyo" ] = u"\u3072\u3087"
    Hiragana["ma"  ] = u"\u307e"
    Hiragana["mi"  ] = u"\u307f"
    Hiragana["mu"  ] = u"\u3080"
    Hiragana["me"  ] = u"\u3081"
    Hiragana["mo"  ] = u"\u3082"
    Hiragana["mya" ] = u"\u307f\u3083"
    Hiragana["myu" ] = u"\u307f\u3085"
    Hiragana["myo" ] = u"\u307f\u3087"
    Hiragana["ya"  ] = u"\u3084"
    Hiragana["yu"  ] = u"\u3086"
    Hiragana["yo"  ] = u"\u3088"
    Hiragana["ra"  ] = u"\u3089"
    Hiragana["ri"  ] = u"\u308a"
    Hiragana["ru"  ] = u"\u308b"
    Hiragana["re"  ] = u"\u308c"
    Hiragana["ro"  ] = u"\u308d"
    Hiragana["rya" ] = u"\u308a\u3083"
    Hiragana["ryu" ] = u"\u308a\u3085"
    Hiragana["ryo" ] = u"\u308a\u3087"
    Hiragana["wa"  ] = u"\u308f"
    Hiragana["wo"  ] = u"\u3092"
    Hiragana["nn"  ] = u"\u3093"
    Hiragana["ga"  ] = u"\u304c"
    Hiragana["gi"  ] = u"\u304e"
    Hiragana["gu"  ] = u"\u3050"
    Hiragana["ge"  ] = u"\u3052"
    Hiragana["go"  ] = u"\u3054"
    Hiragana["gya" ] = u"\u304e\u3083"
    Hiragana["gyu" ] = u"\u304e\u3085"
    Hiragana["gyo" ] = u"\u304e\u3087"
    Hiragana["za"  ] = u"\u3056"
    Hiragana["ji"  ] = u"\u3058"
    Hiragana["zu"  ] = u"\u305a"
    Hiragana["ze"  ] = u"\u305c"
    Hiragana["zo"  ] = u"\u305e"
    Hiragana["ja"  ] = u"\u3058\u3083"
    Hiragana["ju"  ] = u"\u3058\u3085"
    Hiragana["jo"  ] = u"\u3058\u3087"
    Hiragana["da"  ] = u"\u3060"
    Hiragana["ji"  ] = u"\u3062"
    Hiragana["zu"  ] = u"\u3065"
    Hiragana["de"  ] = u"\u3067"
    Hiragana["do"  ] = u"\u3069"
    Hiragana["ba"  ] = u"\u3070"
    Hiragana["bi"  ] = u"\u3073"
    Hiragana["bu"  ] = u"\u3076"
    Hiragana["be"  ] = u"\u3079"
    Hiragana["bo"  ] = u"\u307c"
    Hiragana["bya" ] = u"\u3073\u3083"
    Hiragana["byu" ] = u"\u3073\u3085"
    Hiragana["byo" ] = u"\u3073\u3087"
    Hiragana["pa"  ] = u"\u3071"
    Hiragana["pi"  ] = u"\u3074"
    Hiragana["pu"  ] = u"\u3077"
    Hiragana["pe"  ] = u"\u307a"
    Hiragana["po"  ] = u"\u307d"
    Hiragana["pya" ] = u"\u3074\u3083"
    Hiragana["pyu" ] = u"\u3074\u3085"
    Hiragana["pyo" ] = u"\u3074\u3087"
    Hiragana["*"   ] = u"\u309c"
    
    Katakana["a"   ] = u"\u30a2"
    Katakana["i"   ] = u"\u30a4"
    Katakana["u"   ] = u"\u30a6"
    Katakana["e"   ] = u"\u30a8"
    Katakana["o"   ] = u"\u30aa"
    Katakana["ka"  ] = u"\u30ab"
    Katakana["ki"  ] = u"\u30ad"
    Katakana["ku"  ] = u"\u30af"
    Katakana["ke"  ] = u"\u30b1"
    Katakana["ko"  ] = u"\u30b3"
    Katakana["kya" ] = u"\u30ad\u30e3"
    Katakana["kyu" ] = u"\u30ad\u30e5"
    Katakana["kyo" ] = u"\u30ad\u30e7"
    Katakana["sa"  ] = u"\u30b5"
    Katakana["shi" ] = u"\u30b7"
    Katakana["su"  ] = u"\u30b9"
    Katakana["se"  ] = u"\u30bb"
    Katakana["so"  ] = u"\u30bd"
    Katakana["sha" ] = u"\u30b7\u30e3"
    Katakana["shu" ] = u"\u30b7\u30e5"
    Katakana["sho" ] = u"\u30b7\u30e7"
    Katakana["ta"  ] = u"\u30bf"
    Katakana["chi" ] = u"\u30c1"
    Katakana["tsu" ] = u"\u30c4"
    Katakana["te"  ] = u"\u30c6"
    Katakana["to"  ] = u"\u30c8"
    Katakana["cha" ] = u"\u30c1\u30e3"
    Katakana["chu" ] = u"\u30c1\u30e5"
    Katakana["cho" ] = u"\u30c1\u30e7"
    Katakana["na"  ] = u"\u30ca"
    Katakana["ni"  ] = u"\u30cb"
    Katakana["nu"  ] = u"\u30cc"
    Katakana["ne"  ] = u"\u30cd"
    Katakana["no"  ] = u"\u30ce"
    Katakana["nya" ] = u"\u30cb\u30e3"
    Katakana["nyu" ] = u"\u30cb\u30e5"
    Katakana["nyo" ] = u"\u30cb\u30e7"
    Katakana["ha"  ] = u"\u30cf"
    Katakana["hi"  ] = u"\u30d2"
    Katakana["fu"  ] = u"\u30d5"
    Katakana["he"  ] = u"\u30d8"
    Katakana["ho"  ] = u"\u30db"
    Katakana["hya" ] = u"\u30d2\u30e3"
    Katakana["hyu" ] = u"\u30d2\u30e5"
    Katakana["hyo" ] = u"\u30d2\u30e7"
    Katakana["ma"  ] = u"\u30de"
    Katakana["mi"  ] = u"\u30df"
    Katakana["mu"  ] = u"\u30e0"
    Katakana["me"  ] = u"\u30e1"
    Katakana["mo"  ] = u"\u30e2"
    Katakana["mya" ] = u"\u30df\u30e3"
    Katakana["myu" ] = u"\u30df\u30e5"
    Katakana["myo" ] = u"\u30df\u30e7"
    Katakana["ya"  ] = u"\u30e4"
    Katakana["yu"  ] = u"\u30e6"
    Katakana["yo"  ] = u"\u30e8"
    Katakana["ra"  ] = u"\u30e9"
    Katakana["ri"  ] = u"\u30ea"
    Katakana["ru"  ] = u"\u30eb"
    Katakana["re"  ] = u"\u30ec"
    Katakana["ro"  ] = u"\u30ed"
    Katakana["rya" ] = u"\u30ea\u30e3"
    Katakana["ryu" ] = u"\u30ea\u30e5"
    Katakana["ryo" ] = u"\u30ea\u30e7"
    Katakana["wa"  ] = u"\u30ef"
    Katakana["wi"  ] = u"\u30f0"
    Katakana["we"  ] = u"\u30f1"
    Katakana["wo"  ] = u"\u30f2"
    Katakana["nn"  ] = u"\u30f3"
    Katakana["ga"  ] = u"\u30ac"
    Katakana["gi"  ] = u"\u30ae"
    Katakana["gu"  ] = u"\u30b0"
    Katakana["ge"  ] = u"\u30b2"
    Katakana["go"  ] = u"\u30b4"
    Katakana["gya" ] = u"\u30ae\u30e3"
    Katakana["gyu" ] = u"\u30ae\u30e5"
    Katakana["gyo" ] = u"\u30ae\u30e7"
    Katakana["za"  ] = u"\u30b6"
    Katakana["ji"  ] = u"\u30b8"
    Katakana["zu"  ] = u"\u30ba"
    Katakana["ze"  ] = u"\u30bc"
    Katakana["zo"  ] = u"\u30be"
    Katakana["ja"  ] = u"\u30b8\u30e3"
    Katakana["ju"  ] = u"\u30b8\u30e5"
    Katakana["jo"  ] = u"\u30b8\u30e7"
    Katakana["da"  ] = u"\u30c0"
    Katakana["ji"  ] = u"\u30c2"
    Katakana["zu"  ] = u"\u30c5"
    Katakana["de"  ] = u"\u30c7"
    Katakana["do"  ] = u"\u30c9"
    Katakana["ba"  ] = u"\u30d0"
    Katakana["bi"  ] = u"\u30d3"
    Katakana["bu"  ] = u"\u30d6"
    Katakana["be"  ] = u"\u30d9"
    Katakana["bo"  ] = u"\u30dc"
    Katakana["bya" ] = u"\u30d3\u30e3"
    Katakana["byu" ] = u"\u30d3\u30e5"
    Katakana["byo" ] = u"\u30d3\u30e7"
    Katakana["pa"  ] = u"\u30d1"
    Katakana["pi"  ] = u"\u30d4"
    Katakana["pu"  ] = u"\u30d7"
    Katakana["pe"  ] = u"\u30da"
    Katakana["po"  ] = u"\u30dd"
    Katakana["pya" ] = u"\u30d4\u30e3"
    Katakana["pyu" ] = u"\u30d4\u30e5"
    Katakana["pyo" ] = u"\u30d4\u30e7"
    Katakana["ye"  ] = u"\u30a4\u30a7"
    #Katakana["wi"  ] = u"\u30a6\u30a3"
    #Katakana["we"  ] = u"\u30a6\u30a7"
    #Katakana["wo"  ] = u"\u30a6\u30a9"
    Katakana["va"  ] = u"\u30F7"
    #Katakana["va"  ] = u"\u30f4\u30a1"
    Katakana["vi"  ] = u"\u30F8"
    #Katakana["vi"  ] = u"\u30f4\u30a3"
    Katakana["vu"  ] = u"\u30F4"
    #Katakana["vu"  ] = u"\u30f4"
    Katakana["ve"  ] = u"\u30f4\u30a7"
    #Katakana["ve"  ] = u"\u30F9"
    Katakana["vo"  ] = u"\u30FA"
    #Katakana["vo"  ] = u"\u30f4\u30a9"
    Katakana["she" ] = u"\u30b7\u30a7"
    Katakana["je"  ] = u"\u30b8\u30a7"
    Katakana["che" ] = u"\u30c1\u30a7"
    Katakana["ti"  ] = u"\u30c6\u30a3"
    Katakana["tu"  ] = u"\u30c8\u30a5"
    Katakana["tyu" ] = u"\u30c6\u30e5"
    Katakana["di"  ] = u"\u30c7\u30a3"
    Katakana["du"  ] = u"\u30c9\u30a5"
    Katakana["dyu" ] = u"\u30c7\u30e5"
    Katakana["tsa" ] = u"\u30c4\u30a1"
    Katakana["tsi" ] = u"\u30c4\u30a3"
    Katakana["tse" ] = u"\u30c4\u30a7"
    Katakana["tso" ] = u"\u30c4\u30a9"
    Katakana["fa"  ] = u"\u30d5\u30a1"
    Katakana["fi"  ] = u"\u30d5\u30a3"
    Katakana["fe"  ] = u"\u30d5\u30a7"
    Katakana["fo"  ] = u"\u30d5\u30a9"
    Katakana["-"   ] = u"\u30fc"
    Katakana["."   ] = u"\u30FB"
    Katakana["*"   ] = u"\u309C"
    Katakana["\\"   ] = u"\u30FD"
    Katakana["|"   ] = u"\u30FE"
    Katakana["dd"  ] = u"\u30c3"
    Katakana["pp"  ] = u"\u30fd"
    
    return (Hiragana,Katakana)
    
(Translate.Hiragana,Translate.Katakana) = init_KanaTables()

if __name__ =="__main__":
    #print "the results of this file cannot be fully realized on windows"
    #print "the console does not allow unicode output"
    string = "Check out ;;sutereoponi-, A great J-Rock Band"
    # obj = Translate(string)
    # # print the original string
    # print obj.ostring
    # #unicode-escape prevents errors on printing to the screen
    # # print the converted string
    # print obj.nstring.encode('unicode-escape') 
    # 
    # obj2 = Translate(obj.nstring)
    # # rstring strips all unicode back to english characters
    # print obj.rstring
    
    o = Translate(";;ken")
    print o.ostring
    print o.nstring.encode('unicode-escape') 
    
    o = Translate(";;mettsu")
    print o.ostring
    print o.nstring.encode('unicode-escape') 
    
    o = Translate(";;meddtsu")
    print o.ostring
    print o.nstring.encode('unicode-escape') 
    