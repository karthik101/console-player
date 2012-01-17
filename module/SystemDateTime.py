# #########################################################
# #########################################################
# File: SystemDateTime
# Description:
#       Standard Python library requires imports from 3
#   different modules to handle date and time values.
#   each is speciailized and serves a purpase, but the goal
#   of this file is to unify them under one common object.
#
#   DateTime is an object with static methods that can be
#   used to :
#
#   convert date strings to a Unix time integer and back
#   get the current time as an int
#   get the current time as a string
#
#   
#
# import:
#   from SystemDateTime import DateTime
#
# #########################################################

import os
from SystemPathMethods import atoi
from calendar import timegm
import time
import datetime


#todo detect date format, assuming it is complete and one of the 3 builtin formats

class DateTime(object):
    DATETIME_STANDARD = 0
    DATETIME_US = 1
    DATETIME_EU = 2
    
    datetime_format = { 0:"%Y/%m/%d %H:%M",
                        1:"%m/%d/%Y %H:%M",
                        2:"%d/%m/%Y %H:%M"
                      }
    date_format = { 0:"%Y/%m/%d",
                    1:"%m/%d/%Y",
                    2:"%d/%m/%Y"
                  }
    time_format = { 0:"%H:%M",
                    1:"%H:%M",
                    2:"%H:%M"
                  }
    
    def __init__(self,format=0):
        if isinstance(format,basestring):
            self.format = -1;
            self.datetime_format[-1] = format
        else:
            self.format = format
        self.timedelta_start = 0;
        self.timedelta_end = 0;
        self.timedelta = 0;
        self.usdelta = 0;
        
    @staticmethod
    def now():
        """
            Return seconds since Unix Epoch
        """
        # this is an odd format, time.time() returns a float containing the seconds
        # but, i need to convert that number to local time.
        # which requires calender.timegm to convert back to seconds
        return timegm(time.localtime(time.time()))

    def timer_start(self):
        self.timedelta_start = datetime.datetime.now()
        #return self.timedelta_start
        
    def timer_end(self):
        # set timedelta to the number of elapsed milliseconds
        d = (datetime.datetime.now() - self.timedelta_start).total_seconds()
        self.timedelta = int(  d*1000 );    # get time delta in milliseconds
        self.usdelta = int(  d*1000000 );   # get time delta in microseconds (UNIX only)
        return self.timedelta
        
    def getFormat(self):
        return self.format
        
    def getFormatString(self):
        return self.datetime_format[self.format]
        
    def setFormat(self,format):
        self.format = format
        
    def setDateFormat(self,fmtstr):    
        """
            set a custom string format for Dates
            this will update the format for datetime, which is always date first then hour/minutes
        """
        self.format = -1;
        self.date_format[-1] = fmtstr
        self.datetime_format[-1] = self.date_format.get(-1,"")+" "+self.time_format.get(-1,"")
        
    def setTimeFormat(self,fmtstr):    
        """
            set a custom string format for time
            this will update the format for datetime, which is always date first then hour/minutes
        """
        self.format = -1;
        self.time_format[-1] = fmtstr
        self.datetime_format[-1] = self.date_format.get(-1,"")+" "+self.time_format.get(-1,"")    
        
    def currentDateTime(self):
        """
            Return current date-time as a formatted string
            use setFormat to change the date format
        """
        return time.strftime(self.__dt(),time.localtime(time.time()))
        
    def currentDate(self):
        """
            Return current date as a formatted string
            use setFormat to change the date format
        """
        return time.strftime(self.__d(),time.localtime(time.time()))
    
    def currentTime(self):
        """
            Return current date as a formatted string
            use setFormat to change the date format
        """
        return time.strftime(self.__t(),time.localtime(time.time()))
        
    def formatDateTime(self,unixTime):
        """
            Return a formated string using the current DateTime format
            for a given time, in seconds since the Unix Epoch.
            
            returns 
        """
        try:
            return time.strftime(self.datetime_format[self.format], time.gmtime(unixTime)) 
        except:
            pass
            
        return time.strftime(self.datetime_format[self.format], time.gmtime(0))
    
    @staticmethod
    def reformatDateTime(input_fmt,output_fmt,date):
        """
            whereas formatDateTime returns a formatted date from seconds since the Epoch
            this function will reformat the date from one string to another
            
            the 'input' date is the cell item from the index
            of the parent tables' data.
            
            the 'output' can use any of the symbols found in input
            in a different order.
            
            the allowed symbols are:
            %Y - year   %H - hour
            %m - month  %M - minute 
            %d - day   
            %y - 2 digit year
            if %Y is defined, then %y will be autofilled
            
            e.x.:
                input = "%Y/%m/%d" ==> 1990/3/12
                output= "%m/%d/%y" ==> 3/12/90
                
                or even : "%Y/%m/%d - %H:%M" ==> "%H:%M" 
                    but this is not the fastest way to extract this information
                
            symbols need not be defined anywhere previously, as long as they are unique.
            using the transform "%1/%2/%3" ==> "%3-%2-%1" will work for any possible input
            that has three values separated by '/'. -- however %Y is still special in that
            it expects a 4 digit year and sets %y to a 2 digit year aswell
            
            if the input date does not have all of the formats needed in the input_fmt
            or if the characters do not match between the input_fmt and output_fmt
            the resulting behavior is undefined and may throw an exception.
        """
        tokens = "- /\\:"
        
        fmt    = msplit( input_fmt , tokens );
        input  = msplit( date , tokens );
        
        D = {}
        # build a dictionary of single letters to format values
        for i in range(len(fmt)):
            D[ fmt[i][1] ] = input[i] 
            if fmt[i] == "%Y":
                D["y"] = input[i][-2:]
        #print input
        #print D
        output = ""
        index = 0;
        
        while index < len(output_fmt):
            if output_fmt[index] == "%":
                index += 1 # skip the percent
                output += D[output_fmt[index]]
            else:
                output += output_fmt[index]  
            index += 1
    
        return output
    def getEpochTime(self,datestring):
        """
            return seconds since the Unic Epoch by converting a string formatted
            in the current set date format.
            
            note that this function is a little forgiving.
            if it is possible to determine missing parts they will be filled in
            and '/' '\' or '-' are all considered the same.
        """
        datestring = self.repairDateTime(datestring)
        datetime = None
        try:
            datetime = time.strptime(datestring,self.datetime_format.get(self.format,"%Y/%m/%d %H:%M"))
            return timegm(datetime)   
        except:
            pass
            
        return 0;
    
    def repairDateTime(self,datetime):
        """
            Takes a partically completed datetime string, assumed to be
            formatted as the current format, and fills in missing data
            
            example for format==0:
                70/1/1 12  <==> 1970/01/01 12:00
                00         <==> 2000/01/01 00:00
        
            an empty string is returned when not enough information is supplied
            
            TODO:
                would it be worth, reading in a locale file,
                and be able to convert say -  March to 03
            
        """
        # split the input into a list, on / \ - ' ' and :
        # using the current format read left to right
        
        tokens = "- /\\:"
        
        input  = msplit( datetime , tokens );
        
        repaired_string = "" # the string to be returned.
        
        srcfmt = self.datetime_format[self.format]
        
        do_nothing = lambda x: x; # do nothing is used to skip unknown % formats
        
        index = 0; # index for srcfmt character to reference
        ii = 0; # input index
        
        while index < len(srcfmt):
        
            
            if srcfmt[index] == "%":
                index += 1; # skip the % in the datetime format
                
                if ii < len(input): # get the next user input or empty string
                    s = input[ii]
                else:
                    s = ""
                
                # using the srcfmt character, and the user input
                # ensure that the string matches a valid date/time format
                # and fix it if it does not
                repaired_string += repair_formats.get('%'+srcfmt[index],do_nothing)(s);
                
                ii+=1;
            else:
                repaired_string += srcfmt[index];
            index += 1;
        
        return repaired_string;
        
    def daysElapsed(self,date1,date2=""):
        """
            return the umber of days elapsed from between two dates
            
            the default is days since the given date and today
            
            a second date can be supplied to compare the two dates
            
            use repairDateTime to ensure you are passing in two complete date formats
        """
        try:
            old=self.getEpochTime( date1 )
            
            if date2 != "":
                now=self.getEpochTime( date2 )
            else:
                now=DateTime.now();
                
            if old != 0:
                return max(1, int(float(now - old)/(60*60*24)) )
        except:
            pass
        
        return 0;

    def getTimeDelta(self):
        """
            return the current timedelta, as a formatted string:
                DD:HH:MM:SS where D is days
            set the time delta using timer_start and timer_end
            
        """
        pass
        
    @staticmethod
    def formatTimeDelta(seconds):
        """
            return a formated string converting the number of seconds
            to "DD:HH:MM:SS"
        """
        _d =  seconds/86400
        _h = (seconds%86400)/3600
        _m = (seconds%3600)/60
        _s = (seconds%60)

        ms = "%02d:%02d"%(_m,_s)
        h = ""
        d = ""
   
        #conditionally format hours only when needed
        if _h > 0 or _d > 0:
            h = "%02d:"%_h
        #conditionally format days only when needed
        if _d > 0 :
            d = "%d:"%_d
            
        #return "DD:HH:MM:SS"
        return "%s%s%s"%(d,h,ms)
        
    @staticmethod
    def formatTimeDeltams(milliseconds):
        """
            return a formated string converting the number of milliseconds
            to "DD:HH:MM:SS.mmm"
        """
        ms = milliseconds%1000
        s = milliseconds/1000
        return DateTime.formatTimeDelta(s)+(".%03d"%ms)
        
    @staticmethod    
    def formatTimeDeltaus(microseconds):
        """
            return a formated string converting the number of milliseconds
            to "DD:HH:MM:SS.mmm"
        """
        us = microseconds%1000
        ms = microseconds/1000
        return DateTime.formatTimeDeltams(ms)+("%03d"%ms)    
       
    @staticmethod
    def parseTimeDelta(string):
        """
            reverse of formatTimeDelta
        """
        string = string.replace(" ","")
        R = string.split(':');
        _s = R[-1];
        _m = "0";
        _h = "0";
        _d = "0";
        
        l = len(R)
        
        if l > 1:
            _m = R[-2];
        if l > 2:
            _h = R[-3];
        if l > 3:
            _d = R[-4];
        
        h = int(_h) + 24*int(_d) # given time in hours
        m = int(_m) + 60*h      # given time in minutes
        s = int(_s) + 60*m      # given time in seconds
        
        return s
        
    @staticmethod   
    def parseTimeDeltams(string):
        """
            reverse of formatTimeDeltams
        """
        R = string.split('.')
        return DateTime.parseTimeDelta(R[0])*1000 + atoi(R[1])
    
    @staticmethod   
    def parseTimeDeltaus(string):
        """
            reverse of formatTimeDeltaus
        """
        R = string.split('.')
        return DateTime.parseTimeDelta(R[0])*1000000 + atoi(R[1])
        
    # the following just make some of the above code easier to read
    # if i always want to get a date/time format, i must use 'get'
    # and supply the default.
    def __dt(self):
        return self.datetime_format.get(self.format,"%Y/%m/%d %H:%M"); 
    def __d(self):
        return self.date_format.get(self.format,"%Y/%m/%d");
    def __t(self):
        return self.time_format.get(self.format,"%H:%M");   
    
        
def __repair_year__(string):
    """
        Repair a given string to a full year
        e.g. 00 => 2000
             90 => 1990
        should use a +/- 50 rule, of autocomplete the century absed off the closest date
        
        there are 4 operational cases:
                X => can't auto complete return ""
               XX => completes to CCXX
              XXX => can only autocomplete by appeneding 0 if startswith 19 or 20
             XXXX => return XXXX
    """
    current_year  = datetime.date.today().year
    l = len(string);
    if l==4:
        return string;
    elif l==3:
        if string[:2] in ["19",20]: 
            return string+'0'
    elif l==2:
        
        cc = (current_year/100)*100; # the current century base year, e.g. 2000
        pc = cc-100;                 # previous century
        nc = cc+100;                 # next century
        
        # possible bug: what about nc, next century
        value = atoi(string)
        # test whether, for the entered 2 digit year, 
        # if it exists in the previous century
        # or in the current century

        hi = value + cc - current_year
        lo = current_year - (value + pc)
        if lo < hi:
            return str(pc+value)
        return str(cc+value)
    return str(current_year);

def __repair_month__(string):
    """
        repair a given string to a "full" month
        e.g. 9 => 09
            12 => 12
        if any error is encountered '01' is returned
        months are 1 or 2 characters and always return a 2 digit month
        
        months must be less than or equal to 12
    """
    value = atoi(string)
    l = len(string)
    if l==1 and value < 10:
        return "0"+string;
    if l==2 and value <= 12:
        return string
    return "01"    
    
def __repair_day__(string):
    """
        repair a given string to a "full" day
        e.g. 9 => 09
            30 => 30
           401 => '' 
        days are 1 or 2 characters and always return a 2 digit day
        
        days must be less than or equal to 31
    """
    value = atoi(string)
    l = len(string)
    if l==1 and value < 10:
        return "0"+string;
    if l==2 and value <= 31:
        return string
    return "01"
   
def __repair_hour__(string):
    value = atoi(string)
    l = len(string)
    if l==1 and value < 10:
        return "0"+string;
    if l==2 and value <= 60:
        return string
    return "00"
    
def __repair_minute__(string):
    value = atoi(string)
    l = len(string)
    if l==1 and value < 10:
        return "0"+string;
    if l==2 and value <= 60:
        return string
    return "00"
   
# gather all repair methods into a dictionary
# this will make calling them easier   
repair_formats = {
                  '%Y':__repair_year__,
                  '%m':__repair_month__,
                  '%d':__repair_day__,
                  '%H':__repair_hour__,
                  '%M':__repair_minute__,
                 };
  
def msplit(s, seps):
    """
        define a split that can work on multiple seperator tokens.
    """
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res
  
if __name__ == "__main__":
    dt = DateTime(DateTime.DATETIME_STANDARD)
    
    # the old getSecondsFromDateFormat
    # can be recreated by instantiating an object with a date format, then calling getEpochTime
    
    print dt.getFormat();
    print dt.getFormatString();
    #print dt.setDateFormat("%Y-%m-%d");
    #print dt.setTimeFormat("%M/%H");
    print "Unix Time: %d"%DateTime.now();        # Was: getCurrentTime
    print "Date-Time: %s"%dt.currentDateTime();  # Was: getNewDate
    print "Date     : %s"%dt.currentDate();      
    print "     Time: %s"%dt.currentTime();      
    print "EPOCH-to-DT : %s"%dt.formatDateTime(DateTime.now())      # Was: getFormatDate
    print "DT-to-Epoch : %d"%dt.getEpochTime(dt.currentDateTime())  # Was: getEpochTime
    print "Days Elapsed: %d"%dt.daysElapsed("2011/01/01 00:00")     # Was: get_DaysPassed
    
    print "-------------"
    # in this section, the first i should include seconds
    # then the value of i at every other line should be the same
    # with the seconds component rounded down
    i = DateTime.now()
    print i, dt.currentDateTime()
    
    d = dt.formatDateTime( i ) 
    i = dt.getEpochTime( d )
    print i, d

    d = dt.formatDateTime( i ) 
    i = dt.getEpochTime( d )
    print i, d
    print "-------------"
    
    print dt.timer_start()
    print dt.timer_end()
    
    print "hey"
    print DateTime.reformatDateTime("%Y/%1/%2","%y:%2:%1","1990/03/12")
    # #################################
    # print dt.formatDateTime(0)
    # print dt.getEpochTime("1970/01/01 00:00")
    # print dt.getEpochTime(dt.formatDateTime(0))
    # print dt.formatDateTime(dt.getEpochTime("1970/01/01 00:00"))
    
    # #################################
    # print "test date repair methods"
    # print "repair year 0: <%s>"%__repair_year__("")
    # print "repair year 1: <%s>"%__repair_year__("0")
    # print "repair year 2: <%s>"%__repair_year__("90")
    # print "repair year 3: <%s>"%__repair_year__("199")
    # print "repair year 4: <%s>"%__repair_year__("1990")
    # print "repair year 5: <%s>"%__repair_year__("1990y")
    # 
    # print "repair month 0: <%s>"%__repair_month__("")
    # print "repair month 1: <%s>"%__repair_month__("5")
    # print "repair month 2: <%s>"%__repair_month__("12")
    # print "repair month 3: <%s>"%__repair_month__("120")
    # 
    # print "repair day 0: <%s>"%__repair_day__("")
    # print "repair day 1: <%s>"%__repair_day__("5")
    # print "repair day 2: <%s>"%__repair_day__("25")
    # print "repair day 3: <%s>"%__repair_day__("901")
    print DateTime.parseTimeDelta("2:50") # should print 170
    print dt.getEpochTime("89/3/12")
    

    # print "test timer"
    # d1 = DateTime()
    # d2 = DateTime()
    # count = 999999
    # d1.timer_start()
    # for i in range(count):
    #     d2.timer_start()
    #     d2.timer_end()
    # d1.timer_end();
    # print d1.timedelta
    # print d1.timedelta/float(count)
 
