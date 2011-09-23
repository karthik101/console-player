
from StringQuoter import *

class StringParse(object):
    """
        Parse the supplied string on the assumption it follows some loose form
        similar to those found in your standard windows command line / bash
        input is assumed to follow:
        [command] [-switch str] [strval]
        where the first word is always assumed to be a command
        and -<character> followed by a string is assumed to be a parameter
        and anything remaining is a string value index starting at zero
    """
    default = ""   # original string
    command = ""   # first white space seperated word
    string = ""    # input without command
    number = None
    
    hasDecVal = 0 # count of all succesful atoi converstions
    hasHexVal = 0 # count of all succesful atoh converstions
    hasStrVal = 0   
    hasNum    = False

    Switch = {} # dictionary of all command switches
    DecVal = [] # array of all white space separated integers     (X or X,XXX or X_XXX formatted
    HexVal = [] # array of all white space separated hex integers (0xXXXX, #XXXX, XXXX or X_XXX or X,XXX
    StrVal = [] # array of all white space separated strings ( Switches will not appear )

    __MAX_INPUT_LENGTH__ = 10
    
    D_StrToDec = None;  # register a dictionary of key=>value pairs
    D_StrToHex = None;  # where the key corresponds to dec/hex values eg any enumerations you use
                        # for example, i have ARTIST : 1,ALBUM : 2,TITLE : 3 and so on
    def __init__(self,string):
    
        self.default = ""   # original string
        self.command = ""   # first white space seperated word
        self.string = ""    # input without command
        self.number = None
        
        self.hasDecVal = 0 # count of all succesful atoi converstions
        self.hasHexVal = 0 # count of all succesful atoh converstions
        self.hasStrVal = 0   
        self.hasNum    = False

        self.Switch = {} # dictionary of all command switches
        self.DecVal = [] # array of all white space separated integers     (X or X,XXX or X_XXX formatted
        self.HexVal = [] # array of all white space separated hex integers (0xXXXX, #XXXX, XXXX or X_XXX or X,XXX
        self.StrVal = [] # array of all white space separated strings ( Switches will not appear )
    
        self.string = unicode(string)
        
        self.default = self.string[:]
        
        # remove quoted values, split the string into arguments
        # then add those values back in
        if len(self.default) == 0:
            return # skipping all processing
            
        q = StringQuote()   # protect any substrings wrapped in double quotes
        qstring = q.quote(string)
        self.StrVal = qstring.split()
        for i in range(len(self.StrVal)):
            self.StrVal[i] = q.unquote(self.StrVal[i])
        
        self.getCommandSwitches(self.StrVal)
        
        if len(self.StrVal) > 0:
            # remove only one instance of command word from string
            self.command = self.StrVal.pop(0)
            self.string = string.replace(self.command,"",1).strip() 
        
        # create two arrays of equal length to all supplied arguments
        
        self.__MAX_INPUT_LENGTH__ = max(self.__MAX_INPUT_LENGTH__,len(self.StrVal))
        
        self.hasStrVal = len(self.StrVal)
        
        self.getNumericData()

    def getNumericData(self):
        
        self.DecVal = [0]*self.__MAX_INPUT_LENGTH__ 
        self.HexVal = [0]*self.__MAX_INPUT_LENGTH__ 
        
        for x in range(min(self.__MAX_INPUT_LENGTH__,len(self.StrVal))):#range(len(self.StrVal)):
            # get int values
            nstr =self.StrVal[x].strip()
            nstr = nstr.replace("_","")
            nstr = nstr.replace(",","")
            # get dec values
            try:
                self.DecVal[x] = int(nstr)
                self.hasDecVal += 1
            except:
                # if the int cast fails, value may be a string type
                # if a Dictionary is registered to D_StrToDec check if the
                # string is a key, correspnding to a predefined numeric value
                if self.D_StrToDec != None:
                    if nstr in self.D_StrToDec:
                        self.DecVal[x] = self.D_StrToDec[nstr]
                        self.hasDecVal += 1
            # get hex values
            try:
                if nstr[0] == '#':
                        nstr=nstr[1:]   # remove the hash symbol
                self.HexVal[x] = int(nstr,16)
                self.hasHexVal += 1
            except:
                # if the int cast fails, value may be a string type
                # if a Dictionary is registered to D_StrToDec check if the
                # string is a key, correspnding to a predefined numeric value
                if self.D_StrToHex != None:
                    if nstr in self.D_StrToHex:
                        self.HexVal[x] = int(self.StrVal[x],16)
                        self.hasHexVal += 1
                        
        # attempt to determine if the command is a numerical value
        try:
            self.number = int(str(self.command))
            self.hasNum = True
        except:
            self.hasNum = False
    def getCommandSwitches(self,strList):
        index = 0
        while index < len(strList):
            if len(strList[index]) == 2:
                if strList[index][0] == '-':
                    noargs = True # check if the next argument is also a switch
                    if (index+1) < len(strList):
                        if strList[index+1][0] != '-':
                            noargs = False
                            self.Switch[strList[index][1]] = strList[index+1]
                            strList.pop(index)  # remove the switch
                            strList.pop(index)  # remove the argument
                    if noargs:
                        self.Switch[strList[index][1]] = True
                        strList.pop(index)  # remove the switch
                    index = 0 # start scanning list again
            index += 1
       
    def debug(self):
        print "---------------------"
        print "---------------------"
        print "input.default:%s"%self.default   # input string
        print "input.command:%s"%self.command   # will be 'test'
        print "input.string :%s"%self.string    # default - command
        print "input.number :%s"%self.number    # string cast to int
        print "---------------------"
        print "input.hasDecVal:%s"%self.hasDecVal   # count of decimal terms
        print "input.hasStrVal:%s"%self.hasStrVal   # count of string terms ( minus command)
        print "input.hasHexVal:%s"%self.hasHexVal   # count of hex terms
        print "input.hasNum   :%s"%self.hasNum      # if input.number evaluates
        print "---------------------"
        print "input.Switch  :%s"%self.Switch     # command line switches eg -a, -b
        print "input.DecVal  :%s"%self.DecVal     # all decimal arguments
        print "input.StrVal  :%s"%self.StrVal     # all string arguments
        print "input.HexVal  :%s"%self.HexVal     # all hex arguments
        
        
if __name__ == "__main__":
    input = StringParse("test a b \"c d\" ")
    input.debug();
    
    print ""
    
    input = StringParse("test -s \"C:\\File.txt\"")
    input.debug();
    
    print ""
    
    input = StringParse("test 1024 #ABC 0x10_24")
    input.debug();