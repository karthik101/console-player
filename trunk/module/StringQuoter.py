# #########################################################
# #########################################################
#       String Quoter Module
# File:
#       StringQuoter.py
# File Description:
#       Instantiate an instance of StringQuote. use the
#   Member function quote() to tokenize parts of the
#   string wrapped up in a string. Use unquote() to restore
#   the tokenized strings.
# #########################################################
# #########################################################


class StringQuote(object):
    
    """
        given a string that contains quoted words,
        builds a dictionary reference and replaces the quoted
        words with tokens
        use unquote to replace the tokens with the original strings
        tokens are of form ~Q%d, starting at 0
    """
    quoteable = "\"'" # token list of things to consider as "quotes"
    marker    = "~Q"  # what to replace quoted items with
    QuoteDict = {}
    
    def quote(self,string):
        """
            custom quote string function for removing quoted words from 
        """
        s = string[:]
        l = len(s)
        self.QuoteDict = {} # was QuoteVal
        qstart = -1
        qcount = 0
        index = 0
        type = '"'
        
        while index < len(s):# x in range(len(s)):
            #print s[index],
            if s[index] in self.quoteable:
                 # type of current quote system to lookout for
                if qstart == -1:
                    type = s[index]
                    qstart = index
                elif s[index] == type: #otherwise ignore the quote, its the wrong format
                    # append the string enclosed in quotes to the 
                    # list of quoted values
                    # then remove it, along with the quotes from the string
                    # TODO ENABLE escaping back spaces
                    #   IS this s[index-1:index+1] == "\\\\"
                    # TODO AT ZERO this is wrong, returns empty string
                    if s[index-1] == "\\" and index > 0:
                        # if the quote is escaped remove the escape character
                        s = s[:index-1]+s[index:]
                        index -= 1
                    else:
                        key = "%s%d"%(self.marker,qcount)
                        self.QuoteDict[key] = s[qstart+1:index] 
                        s =  s[:qstart]+key+s[index+1:]
                        
                        qcount += 1
                        index = qstart # start scanning again from before the change
                        qstart = -1
                        
            index += 1
        # when no matching quote is found remove the starting quote
        # and everything after it
        if qstart != -1:
            s = s[:qstart]
        #print "\n", s ,":", QuoteVal       
        return s
    
    def unquote(self,string):
        """
            given a string and the look up table to compare to
            replace all instances of key with the dict value
        """
        if len(self.QuoteDict) > 0:
            # error: when using key,value "too many values to unpack"
            for key in self.QuoteDict:
                string = string.replace(key,self.QuoteDict[key])
                
        return string

if __name__ == "__main__":
    test1 = 'abc"1\'2\'3"def'
    test2 = "123'a\"b\"c'def"
    
    q1 = StringQuote()
    q2 = StringQuote()
    
    r1 = q1.quote(test1)
    r2 = q2.quote(test2)
    
    s1 = q1.unquote(r1)
    s2 = q2.unquote(r2)
        
        
    print "t1: %s"%test1    
    print "r1: %s - %s"%(r1,q1.QuoteDict)    
    print "s1: %s"%s1
    
    print "---"
    
    print "t2: %s"%test2   
    print "r2: %s - %s"%(r1,q1.QuoteDict)       
    print "s2: %s"%s2   
    #-----------------------
    test1 = "word*word*word"
    q1.quoteable = "*"
    q1.marker = "!"
    r1 = q1.quote(test1)
    print "--- Change the Quote Symbol, and the replacement token"
    print "t3: %s"%test1
    print "r3: %s - %s"%(r1,q1.QuoteDict)    
    
    #-----------------------
    # -_- toothpick hell should be reserved for perl only.
    test1 = 'word"word\\\"word\\\"word"word'
    q1 = StringQuote()
    r1 = q1.quote(test1)
    print "--- Escape Quotes"
    print "t4: %s"%test1
    print "r4: %s - %s"%(r1,q1.QuoteDict)  
    
    
    
    
    
    