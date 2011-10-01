# #########################################################
# #########################################################
# File: MpFileAccess
# Description:
#       Functions the deal with the OS and file paths go here
#   hopefully all os specific code can be grouped here.
# #########################################################
import os
import sys

isPosix = os.name == 'posix'
__devmode = "-devmode" in sys.argv;

def getInstallPath():
    """
        Return the path that the application is installed in
        Assume first that it is installed localled
        Then assume it is installed to the appdata folder
        
        application is installed if a settings.ini file exists
        if that file does not exist then return no path
    """
    
    _localname_ = "user"   
    _appdataname_ = "ConsolePlayer"
    
    path = os.path.join(os.getcwd(),_localname_,"");
    file = os.path.join(path,"settings.ini");
    if os.path.exists(file):
        debugPreboot("Install Path: %s"%path)
        return path
    
    # getenv('USERPROFILE') returns C:/Users/Nick/ or /home/nick/
    if isPosix: # get a global directory to save to
        home = os.getenv("HOME")
    else:
        home = os.getenv("APPDATA")
    
    
    if home != None and not __devmode: #only use global install path when not developing
        path = os.path.join(home,_appdataname_,"");
        file = os.path.join(path,"settings.ini");
        if os.path.exists(file):
            debugPreboot("Install Path: %s"%path)
            return path
        
    return "";

def getStyleImagePath(filename):
    """
        returns the path to the named image
        if it is not found in the current style
        then use the default image icon from /images instead
    """
    path = os.path.join(MpGlobal.installPath,"style",Settings.THEME,"images",filename);
    if not os.path.exists(path):
        newpath = os.path.join(MpGlobal.installPath,"images",filename);
        if not os.path.exists(newpath):
            return os.path.join(MpGlobal.installPath,"images","blank.png");
        else:
            return newpath
    return path
    
def musicLoad(filepath):

    if not os.path.exists(filepath):
        return [] # return empty array, then check status from that
    rf = open(filepath,"r")
    line1 = not None # this actually kind of hurts
    line2 = not None 
    song = None
    
    count = 0
    _create_Song_ = createSongV2
    
    line1 = rf.readline()
    
    if line1:   # not None
        line1 = line1.strip()
        if line1 == "#VERSION: 2":
            print "found v2"
            # count is stored on the next line
            count = int(rf.readline())
        elif line1 == "#VERSION: 3":
            #print "found v3"
            _create_Song_ = createSongV3
            # count is stored on the next line
            count = int(rf.readline())
        elif line1 == "#VERSION: 4":
            #print "found v3"
            _create_Song_ = createSongV4
            # count is stored on the next line
            count = int(rf.readline()[1:])
        else:   # no version id number ( v1 or older )
            print "no version"
            count = int(line1)
    
    
    array = [[]]*count # number of songs to read
    index = 0;
    # read in song data
    rpath = ""
    useRelDrive = False;
    # these variables enable not knowing the location of music at boot
    lookForDrive = False;
    drivelist = systemDriveList();
    #Settings.SAVE_FORMAT = False
    print drivelist
    while line1:
    

        line1 = rf.readline().strip()
        if line1 == "": break;  # error checking
        
        # look for setting decorators
        if line1[:4] == r'#~D:':
            s = line1[4:]
            if s == "%CWD%":
                #TODO WINDOWS ONLY
                rpath = os.getcwd()[0]+":\\"
                debugPreboot("Music Found on %s:\\ Drive."%rpath)
                Settings.SAVE_FORMAT = MpGlobal.SAVE_FORMAT_CWD
            elif s == "%UNKNOWN%":
                Settings.SAVE_FORMAT = MpGlobal.SAVE_FORMAT_UNKNOWN
                lookForDrive = True;
            else:
                rpath = s
                debugPreboot("Music Found on %s:\\ Drive."%rpath)
            useRelDrive = True
            
            continue;
        
        # line loaded was a song line
        
        line2 = rf.readline().strip()
        line2 = unicode(line2,'unicode-escape')
        if line2 == "": break;  # error checking
        
        if isPosix: # perform a slash path correct fix for the current OS
            line2 = line2.replace('\\','/')     
        else:
            line2 = line2.replace('/','\\')
            
        if lookForDrive:
            # determine which drive the song exists.
            # THEN ASSUME THE ALL SONGS EXIST ON THAT DRIVE
            for drive in drivelist:
                try:

                    path =  os.path.join(drive , line2);
                    if isPosix: # attempt to fix the path on UNIX if it was saved incorrectly
                        path = UnixPathCorrect(path)
                    debugPreboot("LIB Testing: %s"%path)
                    if os.path.exists( path ) and path != '':
                        useRelDrive = True
                        rpath = drive
                        break
                except:
                    pass #debugPreboot("Music Not Found on Any Drive.")
                  
            else:
                print "Error Loading Music. Assuming: %s:\\"%rpath
                
            lookForDrive = False;
            
        if useRelDrive:
            line2 = os.path.join(drive , line2)
        
            
        array[index] = Song()#[[]]*MpGlobal.SONGDATASIZE
        
        array[index][MpMusic.EXIF] = unicode(line1,'unicode-escape')
                        
        array[index][MpMusic.PATH] = line2

        _create_Song_(array[index]);
        
        index += 1
        
    rf.close()    

    if count != index:
        print "READ %d != %d"%(count,index)
        print "encoding error"
        return array[:index]
    #assert count == index, "Count Does note match index %d != %d"(count,index)
    
    return array
    
def musicSave(filepath,data,type=0):
    """save the given array of songs to the destination file path
        Final version of this function, 
        now saves a version id string to the first line of the file
    """
    if len(data) == 0:
        print "No Data to Save: %s"%filepath
        return;
    wf = open(filepath,"w")
    
    wf.write( "#VERSION: %d\n"%MpGlobal.FILESAVE_VERSIONID )
    
    if MpGlobal.FILESAVE_VERSIONID == 4:
        wf.write( "#%d\n"%len(data) )
    else:
        wf.write( "%d\n"%len(data) )
    # version control
    _create_exif_ = createExifV2
    if MpGlobal.FILESAVE_VERSIONID == 3:
        _create_exif_ = createExifV3
    elif MpGlobal.FILESAVE_VERSIONID == 4:
        _create_exif_ = createExifV4
    #self.SAVE_FORMAT=False
    #self.RELATIVE_DRIVE_PATH="%RELATIVE%" # any string or %RELATIVE%

    if type==1:
        wf.write( "#~D:%CWD%\n")
    elif type==2:
        wf.write( "#~D:%UNKNOWN%\n")

    driveList = systemDriveList()
    
    for song in data:
        #try:
        exif = _create_exif_(song)
        string1 = unicode( exif ).encode('unicode-escape')
        string2 = unicode( song[MpMusic.PATH] )
        
        if type > 0:#alternate save formats remove the drive
            string2 = stripDriveFromPath(driveList,string2)
            
        string2 = string2.encode('unicode-escape')
        
        wf.write( "%s\n"%string1 )

        wf.write( "%s\n"%string2 )
        #except Exception as e:
        #    print "Error: %s"%(e.args)
        #    break
        #    print str(data[x][PATH])
        
    wf.close() 
   
def musicBackup(force = False):
    """
        save a copy of the current library to ./backup/
        only save if one has not been made today,
        delete old backups
        
        adding new music, deleting music, are good reasons to force backup
    """
    path = os.path.join(MpGlobal.installPath,'backup')
    if not os.path.exists(path):
        os.mkdir(path)
        print "backup directory created"
        
    date,time = getNewDate().split(' ')
    date = date.replace('/','-').replace('\\','-')
    
    name = 'music_backup-'
    fullname = name+date+'.library'
    h,m = time.split(':')
        
    if (atoi(h) > 12) or force:  # save backups in the afternoon only
    
        R = []
        dir = os.listdir(path)
        for file in dir:
            if file.startswith(name):
                R.append(file);
                
        newestbu = ""

        R.sort(reverse=True)
        
        if len(R) > 0:

            #remove old backups
            # while there are more than 6, 
            # and one has not been saved today
            while len(R) > 6 and R[0] != fullname: 
                delfile = R.pop()
                print "Deleting %s"%delfile
                os.remove(os.path.join(path,delfile))
                
            # record name of most recent backup, one backup per day unless forced    
            newestbu = R[0]
            
        # save a new backup 
        if force or newestbu != fullname:
            print "Saving %s"%fullname
            newbu = os.path.join(path,fullname)  
            musicSave(newbu,MpGlobal.Player.library,Settings.SAVE_FORMAT);
            
            
    
   
def playListSave(filepath,data,relDrive=0,index=0):
    # index = MpGlobal.Player.CurrentIndex
    driveList = systemDriveList()
    wf = open(filepath,"w")
    wf.write("#index=%d\n"%index);
    for x in range(len(data)):
        path = data[x][MpMusic.PATH]
        if type > 0:#alternate save formats remove the drive
            path = stripDriveFromPath(driveList,path)
        wf.write( "%s %s\n"%(data[x].id, unicode(path).encode('unicode-escape') ) )
    wf.close()
    
def playListLoad(filepath,source):
    
    if not os.path.exists(filepath):
        return [] # return empty array, then check status from that
    rf = open(filepath,"r")

    array = []
    
    rpath = ''
    lookForDrive = False
    
    if Settings.SAVE_FORMAT == MpGlobal.SAVE_FORMAT_CWD:
        rpath = os.getcwd()[0]
    elif Settings.SAVE_FORMAT == MpGlobal.SAVE_FORMAT_UNKNOWN:
        lookForDrive = True

    
    drivelist = systemDriveList();

    line = rf.readline().strip()
    count = 0;
    while line:
    
        if line[0] == '#':
            R = line.split('=');
            Settings.PLAYER_LAST_INDEX = atoi(R[1]);
            line = rf.readline().strip()
            continue;
        elif line[:2] == '0x':
            id,path = line.split(' ',1)
            id = hex64(id)
        else:
            id = hex64(0)
            path = line
        
        path = unicode(path.strip(),'unicode-escape')
        
        if lookForDrive:
             # determine which drive the song exists.
            # THEN ASSUME THAT ALL SONG EXIST ON THAT DRIVE
            for drive in drivelist:
                try:
                    p = os.path.join(drive , path)
                    debugPreboot("PL Testing: %s"%p)
                    
                    if os.path.exists( p ):
                        useRelDrive = True
                        rpath = drive
                        break
                except:
                    pass#debugPreboot("Music Not Found on Any Drive.")
            else:
                debugPreboot("Error Loading Music. Assuming: %s"%rpath)
                
            lookForDrive = False;
        
        
        if rpath != '':
            path = os.path.join(rpath,path);
        
        # Search for the song in the source library
        # first compare the hex id. if this fails compare paths
        # comparing paths is much slower than comparing ids
        for x in range(len(source)):
            if source[x].id == id:
                array.append(source[x])
                break
        else:
            for x in range(len(source)):
                if comparePath( source[x][MpMusic.PATH] ,path ):
                    array.append(source[x])
                    break
                
        line = rf.readline().strip()
        count += 1;
        
        if count%25 == 0: # was Settings.SEARCH_STALL, but even 100 was way to much (25 still is)
            MpGlobal.Application.processEvents();
    rf.close()
    return array

def saveSettings( ):
    """
        using the data found in D, a dictionary
        store that data in a file in the format:
        key:value
        sort the keys for readability
        the format intent of a Settings dictionary is as follows:
        keys are in the form of 'type_Attribute'
        values are of type 'type'
        example 
            int_Width:600
            str_Title:MP3Player
        This way parseing and forming of the dictionary can be automatic  
    """
    #k = lambda x: x[0]
    #R = sorted(D.items(), key = k)
    #
    wf = open(MpGlobal.FILEPATH_SETTINGS,"w")
    #for key,value in R :
    #    wf.write( "%s:%s\n"%(key,value) )
    #for k,v in D.items():
    #    print k,"=>",v    
    typeDict = {str(int):'int',
            str(long):'int',
            str(str):'str',
            str(unicode):'str',
            str(bool):'bin',
            str(list):'csv'}

    # from the settings dictionary build a typed dictionary for a human readable save format.
    D = {}
    for key,value in Settings.__dict__.items():
        #TODO: create a list of banned key names
        # for example, PLAYER_LAST_INDEX is saved as the first line of a playlist file
        # instead of in the settings file, despite being a setting key name.
        
        if key != 'PLAYER_LAST_INDEX':
            newKey = "%s_%s"%(typeDict.get(str(type(value)),'???'),key)
            if (type(value) == list):
                D[newKey] = unicode(','.join(value)).encode('unicode-escape')
            else:
                D[newKey] = value
                
    k = lambda x: x[0]
    R = sorted(D.items(), key = k)

    for key,value in R:
        wf.write( "%s:%s\n"%(key,value) )
    wf.close()

def loadSettings():
    """
        read in and set the data from the settings file
        D is the dictionary of values to set
        the intent is to create a default dictionary
        then check if the settings file exists
        if it does override the entry in the dictionary
        with the value in the dictionary
    """
    # dictionary of values to returns
    file = MpGlobal.FILEPATH_SETTINGS
    if os.path.exists(file):
        rf = open(file,"r")
        
        line = True 

        while line:
            line = rf.readline().strip()
            if line != "":
            
                i = line.index(":") # first index of a colon
                
                key,value = ( line[:i], line[i+1:])
                
                dim = key[:3]
                key = key[4:]
               
                # check if the key exists in the Settings
                # therefore deprecaed values are not loaded, and user fat finger values are not laoded
                if key in Settings.__dict__:
                    # load the setting only if it passes basic type checking, only load ints into ints
                    # this way a user cannot attempt to change the basic data type
                    # bad values will still make it crash (string in int) and should be fixed.
                    if dim == u"int" and (type(Settings.__dict__[key]) == int or type(Settings.__dict__[key]) == long):
                        temp = 0;
                        try:
                            temp = int(value)
                        except:
                            print "Not Integral Value: %s_%s = %s"%(dim,key,value)
                        else:
                            Settings.__dict__[key] = temp
                    elif dim == u"bin" and type(Settings.__dict__[key]) == bool:
                        Settings.__dict__[key] = (value.strip() == "True")
                        
                    elif dim == u"csv" and type(Settings.__dict__[key]) == list:
                        #TODO strip whitespace from resulting strings.
                        Settings.__dict__[key] = unicode(value,'unicode-escape').split(',')
                        i=0;
                        while i < len(Settings.__dict__[key]):
                            if len(Settings.__dict__[key][i]) == 0:
                                Settings.__dict__[key].pop(i);
                            else:
                                i += 1;
                        
                    elif dim == u"str" and type(Settings.__dict__[key]) == str or type(Settings.__dict__[key]) == unicode:
                        Settings.__dict__[key] = value
                    else:
                        print "Error Loading Setting: %s_%s = %s"%(dim,key,value)
                else:
                    print "No Setting Named: %s_%s = %s"%(dim,key,value)
            
        rf.close()

        update_StrToDec_Dict();
        #for k,v in D.items():
        #    print k,"=>",v
    return;
  
def getSettingsVersion(dir):    
    """
        this function reads the settings file and extracts the version string only
    """
    settings_path = os.path.join(dir,"settings.ini")
    print "---------------------------"
    print settings_path
    if os.path.exists(settings_path):
        rf = open(settings_path,"r")
        
        line = rf.readline()
        version = ""
        while (line):
            key,value = line.strip().split(':')
            if key == 'str_VERSION':
                version = value
            line = rf.readline()
        rf.close();
    print version
    print MpGlobal.VERSION
    print "---------------------------"
    return version
  
def history_log(filepath,song,type): 

    #exec for song in MpGlobal.Window.tbl_library.data: print "%s %d %s\n"%(song.id,MpMusic.DATESTAMP,song[MpMusic.DATESTAMP])

    if not os.path.exists(filepath):
        wf = open(filepath,"w")
        wf.write("#History\n")
        wf.close()
    #try:
    wf = open(filepath,"a")
    
    datetime = time.localtime(time.time())
    
    data = "None"
    
    if (type == MpMusic.RATING):
        data = "%d"%song[MpMusic.RATING]
        path = createMiniPath(song)
    else: #if (type == MpMusic.DATESTAMP)
        data = time.strftime("%Y/%m/%d %H:%M",datetime)
        type = MpMusic.DATESTAMP

    art = song[MpMusic.ARTIST].encode('unicode-escape') 
    tit = song[MpMusic.TITLE].encode('unicode-escape')
    wf.write("%s %d %-20s # %-30.30s - %-30.30s\n"%(song.id,type,data,art,tit))
    
    wf.close()
    #except:
    #   print "Error Appending to History File"

def history_load(filepath,lib):
    
    if not os.path.exists(filepath):
        return;
      
    line = True 
    newpath = filepath.replace("history","__history__");
    
    rf = open(filepath,"r")
    wf = open(newpath,"w");
    
    success = 0;
    error = 0;
    MpGlobal.Window.debugMsg("\nPlease Wait While Songs Are Processed. This May Take Awhile...")  
    
    MpGlobal.Window.debugMsg("\nUpdated %d Songs -- %d Error(s)"%(success,error)) 
    
    #last_id = hex64(0);
    errorList = [];
    
    while line:
        
        if MpGlobal.Application != None:
            # there is significant slow down delaying this even every 5 counts
            MpGlobal.Application.processEvents()
            
        line = rf.readline()
        wf.write(line);
        
        field = line[:line.find('#')].strip()
        comment = line[line.find('#'):].strip()
        
        if len(field) > 0:
        
            if field[0] != '#':
            
                (id,type,data) = field.split(" ",2)
                
                id = long(id.replace('_',''),16)
                id = hex64(id)
                type = atoi(type)

                if __history_NewSongEntry(lib,type,data,id):
                    success += 1;
                else:
                    error += 1;
                    errorList.append("%d - %s %s"%(type,id, comment))
                    #MpGlobal.Window.debugMsgReturn("\n%s\n"%(id)) 
 
                    
                #last_id = id;            
        MpGlobal.Window.debugMsgReturn("\nUpdated %d Songs -- %d Error(s)"%(success,error)) 
 
    MpGlobal.Window.debugMsg(" ... Done!"); 
    
    for err in errorList:
        MpGlobal.Window.debugMsg("\n%s"%(err)); 
             
    rf.close()
    wf.close();
    
    wf = open(filepath,"w"); # clear the history file
    wf.write("#History\n");
    wf.close();
    
    #MpGlobal.Window.debugMsg("\nUpdated %d Songs -- %d Error(s)"%(success,error))                    
                
def __history_NewSongEntry(lib,type,data,id):
    # fom file:
    #   item > path
    # last path prevents updating the same songs playcount twice
                    
    for song in lib:
                        
        if song.id == id:

            if (type == MpMusic.RATING):
                song[MpMusic.RATING] = atoi(data)
                song[MpMusic.SPECIAL] = True 
                song[MpMusic.EXIF] = createInternalExif(song) 
                return True;
            else:
                __history_NewDate__(data,song);
                return True;
            
    return False;
                            
def __history_NewDate__(date,song):
    time = getEpochTime(date) 
    
    song[MpMusic.PLAYCOUNT] += 1 
    song[MpMusic.SPECIAL] = True 
    
    if song[MpMusic.DATEVALUE] < time:
        # update the frequency value and datevalue only if the song 
        # has not been played since the entry
        old = song[MpMusic.DATEVALUE]
        
        displacement = 0
        if old != 0 :
            displacement = max(1, int(float(time - old)/(60*60*24)) ) # div by seconds in day
            
        n = 4
        if song[MpMusic.PLAYCOUNT] == 1:
            song[MpMusic.FREQUENCY] = ((n-1)*displacement)/n
        elif song[MpMusic.FREQUENCY] != 0 :
            song[MpMusic.FREQUENCY] = ((n-1)*song[MpMusic.FREQUENCY] + displacement)/n
        else:
            song[MpMusic.FREQUENCY] = displacement
    
        song[MpMusic.DATESTAMP] = date
        song[MpMusic.DATEVALUE] = time
    song[MpMusic.EXIF] = createInternalExif(song)      
    

# ######################################################
# Song Creation (from string)
# ######################################################

#def createBlankSong( path = "" ):
#    """
#        this is no longer used - songs are now of type Song in MpGlobalDefines
#    """
#    song = Song()#[[]]*MpGlobal.SONGDATASIZE
#    song[MpMusic.PATH]       = unicode(path)
#    song[MpMusic.ARTIST]      = u"Unknown Artist" 
#    song[MpMusic.TITLE]      = u"Unknown Title" 
#    song[MpMusic.ALBUM]      = u"Unknown Album" 
#    song[MpMusic.GENRE]       = u"None" 
#    song[MpMusic.DATESTAMP]  = "NEW"
#    song[MpMusic.DATEVALUE]  = 0
#    song[MpMusic.COMMENT]    = ""
#    song[MpMusic.RATING]      = 0
#    song[MpMusic.LENGTH]      = 64
#    song[MpMusic.SONGINDEX]  = 0
#    song[MpMusic.PLAYCOUNT]  = 0
#    song[MpMusic.SKIPCOUNT]  = 0
#    song[MpMusic.FILESIZE]   = 0
#    song[MpMusic.FREQUENCY]  = 0
#    song[MpMusic.BITRATE]    = 0
#    song[MpMusic.SPECIAL]    = False
#    song[MpMusic.SELECTED]   = False
#    song[MpMusic.EXIF] = createInternalExif(song)
#    return song
  
def createSong( song ):     # v1
    
    R = song[MpMusic.EXIF].split("|")

    song[MpMusic.ARTIST]     = R[0]
    song[MpMusic.TITLE]     = R[1]
    song[MpMusic.ALBUM]     = R[2]
    song[MpMusic.GENRE]      = R[6]
    song[MpMusic.DATESTAMP] = R[7]
    song[MpMusic.RATING]     = int(R[5])
    song[MpMusic.LENGTH]     = int(R[3])
    song[MpMusic.SONGINDEX] = 0
    song[MpMusic.PLAYCOUNT] = int(R[4])
    song[MpMusic.SKIPCOUNT] = 0
    song[MpMusic.FILESIZE]  = 0
    song[MpMusic.BITRATE]   = 0
    song[MpMusic.SPECIAL]   = False
    song[MpMusic.SELECTED]  = False
  
def createSongV2( song ):
    
    R = unicode(song[MpMusic.EXIF]).split("|")
    
    song[MpMusic.ARTIST]      = unicode(R[0])
    song[MpMusic.TITLE]      = unicode(R[1])
    song[MpMusic.ALBUM]      = unicode(R[2])
    song[MpMusic.GENRE]       = unicode(R[3])
    song[MpMusic.DATESTAMP] = unicode(R[4])
    song[MpMusic.RATING]      = int( R[6] )
    song[MpMusic.LENGTH]      = int( R[5] )
    song[MpMusic.SONGINDEX] = int( R[9] )
    song[MpMusic.PLAYCOUNT] = int( R[7] )
    song[MpMusic.SKIPCOUNT] = int( R[8] )
    song[MpMusic.FILESIZE]  = int( R[10] )
    song[MpMusic.BITRATE]   = int( R[11] )
    song[MpMusic.SPECIAL]   = False
    song[MpMusic.SELECTED]  = False
    #-- higher versions
    song[MpMusic.COMMENT]    = ""
    song[MpMusic.FREQUENCY]  = 0
    
def createSongV3( song ):
    
    
    R = unicode(song[MpMusic.EXIF]).split("|")
    
    song[MpMusic.ARTIST]      = unicode(R[0])
    song[MpMusic.TITLE]      = unicode(R[1])
    song[MpMusic.ALBUM]      = unicode(R[2])
    song[MpMusic.GENRE]       = unicode(R[3])
    song[MpMusic.COMMENT]    = unicode(R[4])
    song[MpMusic.DATESTAMP]  = unicode(R[5])
    song[MpMusic.LENGTH]      = atoi( R[6]  )
    song[MpMusic.RATING]      = atoi( R[7]  )
    song[MpMusic.SONGINDEX]  = atoi( R[10] )
    song[MpMusic.PLAYCOUNT]  = atoi( R[8]  )
    song[MpMusic.SKIPCOUNT]  = atoi( R[9]  )
    song[MpMusic.FILESIZE]   = atoi( R[11] )
    song[MpMusic.BITRATE]    = atoi( R[12] )
    song[MpMusic.FREQUENCY]  = atoi( R[13] )
    song[MpMusic.DATEVALUE]  = getEpochTime(song[MpMusic.DATESTAMP])
    song[MpMusic.SPECIAL]    = False
    song[MpMusic.SELECTED]   = False
    
    if song[MpMusic.DATEVALUE] == 0:
        song[MpMusic.DATESTAMP] = ""
    
    song.update()

def createSongV4( song ):
    u = unicode(song[MpMusic.EXIF])[1:-1]
    R = u.split("|")
    
    song[MpMusic.ARTIST]     = unicode(R[0])
    song[MpMusic.TITLE]      = unicode(R[1])
    song[MpMusic.ALBUM]      = unicode(R[2])
    song[MpMusic.GENRE]      = unicode(R[3])
    song[MpMusic.COMMENT]    = unicode(R[4])
    song[MpMusic.DATESTAMP]  = unicode(R[5])
    song[MpMusic.LENGTH]     = atoi( R[6]  )
    song[MpMusic.RATING]     = atoi( R[7]  )
    song[MpMusic.SONGINDEX]  = atoi( R[10] )
    song[MpMusic.PLAYCOUNT]  = atoi( R[8]  )
    song[MpMusic.SKIPCOUNT]  = atoi( R[9]  )
    song[MpMusic.FILESIZE]   = atoi( R[11] )
    song[MpMusic.BITRATE]    = atoi( R[12] )
    song[MpMusic.FREQUENCY]  = atoi( R[13] )
    song[MpMusic.DATEVALUE]  = getEpochTime(song[MpMusic.DATESTAMP])
    song[MpMusic.SPECIAL]    = False
    song[MpMusic.SELECTED]   = False
    song[MpMusic.EXIF]       = createInternalExif(song) # set the exif tag to the internal representation
    song.md5                 = R[14]
    
    if song[MpMusic.DATEVALUE] == 0:
        song[MpMusic.DATESTAMP] = ""
    
    song.update()    
    
def createExif( song ) :    # v1   
    """
        EXIF stands for EXtra InFo
        and contains all meta data inside a single string
        the format changes from time to time and to keep it painless i use tis wrapper
        update the call function when a new version should be used
        but keep all older version as the loader/saver uses them hardcoded based
        on a value in MpGlobal.
    """
    # create an EXIF string for internal player representation
    #R[0] = re.sub(r'%u(?P<uni>....)','\u\g<uni>',R[0])
    #R[1] = re.sub(r'%u(?P<uni>....)','\u\g<uni>',R[1])
    #R[2] = re.sub(r'%u(?P<uni>....)','\u\g<uni>',R[2])
    #artist|title|album|length|playcount|rating|genre|datestamp
    return createExifV3(song)

def createExifV2( song ) :

    return "%s|%s|%s|%s|%s|%d|%d|%d|%d|%d|%d|%d"%( \
        unicode(song[MpMusic.ARTIST]), \
        unicode(song[MpMusic.TITLE]), \
        unicode(song[MpMusic.ALBUM]), \
        unicode(song[MpMusic.GENRE]), \
        song[MpMusic.DATESTAMP], \
        song[MpMusic.LENGTH], \
        song[MpMusic.RATING], \
        song[MpMusic.PLAYCOUNT], \
        song[MpMusic.SKIPCOUNT], \
        song[MpMusic.SONGINDEX], \
        song[MpMusic.FILESIZE], \
        song[MpMusic.BITRATE] )
        
def createExifV3( song ) :
           # 0  1  2  3  4  5  6  7  8  9  0  1  2  3
    return "%s|%s|%s|%s|%s|%s|%d|%d|%d|%d|%d|%d|%d|%d"%( \
        unicode(song[MpMusic.ARTIST]), \
        unicode(song[MpMusic.TITLE]), \
        unicode(song[MpMusic.ALBUM]), \
        unicode(song[MpMusic.GENRE]), \
        unicode(song[MpMusic.COMMENT]), \
        song[MpMusic.DATESTAMP], \
        song[MpMusic.LENGTH], \
        song[MpMusic.RATING], \
        song[MpMusic.PLAYCOUNT], \
        song[MpMusic.SKIPCOUNT], \
        song[MpMusic.SONGINDEX], \
        song[MpMusic.FILESIZE], \
        song[MpMusic.BITRATE], \
        song[MpMusic.FREQUENCY] )

def createExifV4( song ) :
           # 0  1  2  3  4  5  6  7  8  9  0  1  2  3   4
    return "#%s|%s|%s|%s|%s|%s|%d|%d|%d|%d|%d|%d|%d|%d|%s;"%( \
        unicode(song[MpMusic.ARTIST]), \
        unicode(song[MpMusic.TITLE]), \
        unicode(song[MpMusic.ALBUM]), \
        unicode(song[MpMusic.GENRE]), \
        unicode(song[MpMusic.COMMENT]), \
        song[MpMusic.DATESTAMP], \
        song[MpMusic.LENGTH], \
        song[MpMusic.RATING], \
        song[MpMusic.PLAYCOUNT], \
        song[MpMusic.SKIPCOUNT], \
        song[MpMusic.SONGINDEX], \
        song[MpMusic.FILESIZE], \
        song[MpMusic.BITRATE], \
        song[MpMusic.FREQUENCY], \
        song.md5        );
 
def createInternalExif (song):
    """
        EXIF stands for EXtra InFo
        and contains extended meta data inside a single string for easier searching
        Internally we only need individual text fields represented, all other data
        would be useless when searching.
    """
           # 0  1  2  3  4  5  6  7  8  9  0  1  2  3
    return "%s %s %s %s %s"%( \
        unicode(song[MpMusic.ARTIST]), \
        unicode(song[MpMusic.TITLE]), \
        unicode(song[MpMusic.ALBUM]), \
        unicode(song[MpMusic.GENRE]), \
        unicode(song[MpMusic.COMMENT]) );
        
        
def get_md5(filepath):
        block_size=(1<<12);
        if os.path.exists( filepath ):
            md5 = hashlib.md5()
            rf = open(filepath ,"rb")
            while True:
                data = rf.read(block_size)
                if not data:
                    break
                md5.update(data)
            rf.close();
            return "%s"%md5.hexdigest()
        else:
            return ""     
     
# ######################################################
# Style Theme CSS
# ######################################################     
def load_css(style_name,object,dict=None,secondary=False):

    fpath = MpGlobal.installPath+"style/"+style_name+"/"

    if not os.path.exists(fpath):
        #object.setStyleSheet("")  # clear the style sheet
        return None;

    dict = read_css_dict(style_name,"theme",dict)
    if secondary:
        # when secondary is set to true
        # update the main dictionary with user defined values
        dict = read_css_dict(style_name,"user",dict)
    # after loading the dictionary, check for any definitions which contain
    # other definitions
    for key in dict: # replace all %key% in the text with value
        for sub in dict: # replace all %key% in the text with value
            dict[key] = dict[key].replace("%%%s%%"%sub,dict[sub])
     
    R = os.listdir(fpath)

    css = ""

    # load the main css file first, if one exists
    
    if "Main.css" in R:
        css += read_css_file(dict, fpath,"Main") 
        R.remove("Main.css")
    # load all remaining css files    
    for file in R:
        if fileGetExt(file) == "css":
            fname = fileGetName(file)
            if fname[:1] != 'x':
                css += read_css_file(dict, fpath,fname) 

    debugPreboot("Style Sheet: %s Size: %d bytes"%(style_name,len(css)))

    if object != None:
        object.setStyleSheet(css)

    return dict

def read_css_dict(style_name,fname="default",dict=None):
    """
       reads a css theme color dictionary
       a color dictionary stores color information for the theme    

       a dictionary can be passed to this function with initial values
       that will be overwritten if they exist in the file
    """
    #TODO: redo how dict key values are replaced
    # replace valuesa as they are read in, and prevent infinite loops
    if dict == None:
        dict = {}
    
    fpath = os.path.join( MpGlobal.installPath,"style",style_name,fname+".dict")
    
    if os.path.exists(fpath):
        l = " "

        rf = open(fpath,"r")
        
        while len(l) != 0:
            l  = rf.readline()
            e = l.strip()
            try:
                if len(e) > 0: # not empty
                    if e[0] != "#": # not a comment
                        (k,v) = e.split('=>')
                        k = k.strip()
                        v = v.strip()
                        dict[k] = v
            except:
                pass
            
        rf.close()

    # add extra variables 

    dict["IMAGE"] = os.path.join(  MpGlobal.installPath,"style",style_name,"images","");
    dict["STYLE"] = os.path.join( MpGlobal.installPath,"style",style_name,"");
    
    # URLS are funny in that they require foward slashes
    dict["IMAGE"] = dict["IMAGE"].replace("\\","/");
    dict["STYLE"] = dict["STYLE"].replace("\\","/");
    return dict
    
def read_css_file(dict,fpath,name):
    """
        reads in a css file into a string buffer
        comments ( /* ... */ ) are removed, as well
        as empty lines
    """
    fname = name + ".css"
    
    css = ""    
    l = " "

    rf = open(fpath+fname,"r")
    lc = 0
    while len(l) != 0:
        l  = rf.readline()
        e = l.strip()
        # allow for comments, ignore empty lines
        if len(e) > 0: # not empty
            if e[:2] != "/*": # not a comment
                for key in dict: # replace all %key% in the text with value
                    e = e.replace("%%%s%%"%key,dict[key])
                lc += 1    
                css += e+"\n"
    #print "lc: %d"%lc;            
    rf.close()
    
    return css

def css_dict_value(key,cdict,rdict):
    """
        rdict: dictionary loaded from a styles dictionary file
        cdcit: a new dictionary
        key:   key to test against
        if rdict contains the key, set convert that value to a QColor
        and store in cdict
    """
    #TODO this lloks like a oneliner that can be inlined somewhere
    if key in rdict:
        cdict[key] = color_stringToQColor(rdict[key])
    return cdict

def color_stringToQColor(string):
    #TODO this function looks un-neccessary
    hex = {'0':0, '1':1, '2':2, '3':3, '4':4,
           '5':5, '6':6, '7':7, '8':8, '9':9,   
           'A':10, 'B':11,'C':12, 'D':13, 'E':14, 'F':15,
           'a':10, 'b':11,'c':12, 'd':13, 'e':14, 'f':15 }
    hex_template = "#XXXXXX" 
    r=0;
    g=0;
    b=0;
    a=1;
    if len(string) == len(hex_template):
        r = hex[string[1]]*16 + hex[string[2]]
        g = hex[string[3]]*16 + hex[string[4]]
        b = hex[string[5]]*16 + hex[string[6]] 
    elif string[:4] == 'rgba':   #rgb(YYX,YYX,YYX)
        # for css alpha is in range 0 to 1.
        (i,j,k,a) = string[5:-1].split(',')
        r = int(i)
        g = int(j)
        b = int(k)
        a = float(a)
    elif string[:3] == 'rgb':   #rgb(YYX,YYX,YYX)
        (i,j,k) = string[4:-1].split(',')
        r = int(i)
        g = int(j)
        b = int(k)
        #string is now YYX,YYX,YYX
    return QColor(r,g,b,255*a);   

def css_save_dict(style_name,fname,dict):
    """
        save a color dictionary 
        sort the values for user convenience
        it is not recommeneded to use this for theme.dict
        the default themes may contain values beyond the standard set
    """
    fpath = os.path.join(MpGlobal.installPath,"style",style_name,fname+".dict")
    
    k = lambda x: x[0]
    R = sorted(dict.items(), key = k)
    
    wf = open(fpath,"w")
    for key,value in R :
        wf.write( "%-20s=> %s\n"%(key,value) )
    wf.close()
# ######################################################
# Misc system file access
# ######################################################
     
if isPosix:
    def dirCheckAttribNormal(path):
        """ return if the path is a directory, and not hidden, system or other
        """
        return 0; #TODO return file attributes    
else:
    def dirCheckAttribNormal(path):
        """ return if the path is a directory, and not hidden, system or other
        """
        return (win32file.GetFileAttributes(path) == win32con.FILE_ATTRIBUTE_DIRECTORY)     

def fileGetExt(file):
    """ return the extension part of the file"""
    file = unicode(file)
    return file[file.rfind(".")+1:]

def fileGetFileName(file):
    """ return the name + . + ext of the file"""
    file = unicode(file)
    # allow for both types of slashes in path uris
    return file[max(file.rfind("/"),file.rfind("\\"))+1:]
    
def fileGetName(file):
    """ return only the name part of the file"""
    fname = fileGetFileName(file)
    return fname[:fname.find(".")]
    
def fileGetPath(file):
    """ return the path, WITH the final slash"""
    file = unicode(file)
    # allow for both types of slashes in path uris
    return file[:max(file.rfind("/"),file.rfind("\\"))+1]  

def dirGetParentDirName(path):
    """ path with or without final backslash, and not a file path
        must be dir path
        return the name of the parent directory, or drive name
        
    """
    t = path[:]
    if path[-1] == "\\" or path[-1] == "/":
        t = path[:-1]
        
    name = fileGetFileName(t) # i think this makes me a cheater
    
    if name == "" :
        if isPosix:
            return opath[:1+opath.find('/',1)];
        else:
            return opath[:3] # return the drive only
    
    return name
            
def fileGetParentDir(path):
    """ return the path, with the final slash"""
    #path = fileGetPath(file)
    
    path = unicode(path)
    
    opath = path[:]
    if path[-1] == "\\" or path[-1]=="/" :
        path = path[:-1] # remove any trailing slashes as well
    
    i = max(path.rfind("/"),path.rfind("\\")) + 1
    
    if i<1:
        if isPosix:
            return opath[:1+opath.find('/',1)];
        else:
            return opath[:3] # return the drive only
    else:
        return path[:i] # remove the final back slash
    
if isPosix:
    def fileGetDrive(filepath):
        R = filepath.split('/')
        if len(R) == 0:
            return '/'
        elif R[0] == 'media' and len(R) == 1:
            return '/media/'
        elif R[0] == 'media' and len(R) > 1:
            return '/'+R[0]+'/'+R[1]+'/'
        else:
            return  '/'+R[0]+'/'
else:
    def fileGetDrive(filepath):
        return unicode(filepath)[0] + u":\\"

def fileGetSize(path):
    return (os.path.getsize(path) / 1024)
    
if isPosix:
    def driveGetFreeSpace(path):
        return 0; #TODO return freespace of given device /media/device/<dont care/
else: 
    def driveGetFreeSpace(path):
        import ctypes

        drive = unicode(path)[0] + u":\\"

        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(drive), None, None, ctypes.pointer(free_bytes))

        bytes = free_bytes.value
        kbytes = bytes/1024
        mbytes = kbytes/1024
        gbytes = mbytes/1024

        return (bytes,kbytes,mbytes,gbytes)

def pathIsUnicodeFree(path):
    path = unicode(path)
    return all(ord(c) < 256 for c in path)

def comparePath(p1,p2,len=0):
    """
        i have been having issues with comparing paths
        the slashes could either be foward or backwards depending on the OS
        or the user types them. I myself have song mixmatching paths in a single string
        easiest thing to do is strip all slashes, send to lowercase then compare
        first test, using Explorer, revealed that all issues with K-On Singles were
        resolved
        
    """
    
    p1 = unicode(p1).lower()
    p2 = unicode(p2).lower()
    # set all slashes to be the same
    p1 = p1.replace("\\","/")
    p2 = p2.replace("\\","/")
        
    return p1 == p2
    
def comparePartInPath(path,part,len=0):
    """
        i have been having issues with comparing paths
        the slashes could either be foward or backwards depending on the OS
        or the user types them. I myself have song mixmatching paths in a single string
        easiest thing to do is strip all slashes, send to lowercase then compare
        first test, using Explorer, revealed that all issues with K-On Singles were
        resolved
        
    """
    
    path = unicode(path).lower()
    part = unicode(part).lower()
    # set all slashes to be the same
    path = path.replace("\\","/")
    part = part.replace("\\","/")
        
    return path.find(part) >= 0
    
def comparePathLength(p1,p2,l = 0):
    
    p1 = unicode(p1).lower()
    p2 = unicode(p2).lower()
    
    p1 = p1.replace("\\","/")
    p2 = p2.replace("\\","/")
        
    if l == 0:
        l = len(p1)
        
    return p1[:l] == p2[:l]
    
def pathMatchExt(path) :
    """check if the file at path contains a song extension that is usable by the player"""
    fext = fileGetExt(path).lower()
    file_list = ( 'mp3',
                  'm4a', 'm4b', 'm4p', 'mpeg4', 'aac',
                  'asf','wma',
                  'flac',
                )
    return fext in file_list;    
    
def copyPlayListToDirectory(dir,list):

    # force all slashes the same direction

    dir = dir.replace("\\","/")
    # make sure the given directory terminates with a back slash
    if dir[-1] != "/":
        dir += "/"
        
    for song in list:
        validPath = createMiniPath(song)
        
        testMiniPathExists(dir, validPath)
        
        newPath = dir + validPath
        
        # if the file does not exist copy it
        if os.path.exists(newPath) == False:
            copy(song[MpMusic.PATH],newPath)

def testMiniPathExists( dir, mpath ):
    """ test that the calculated minpath exists
        if it does not, create it
    """
    # generate a list of all folders in the path name
    R = mpath.split("\\")
    R = R[:-1] # cut the file name out of the folder list
    
    path = dir
    for x in range(len(R)):
        os.path.join(path,R[x],"")
        if os.path.exists(path) == False :
            os.mkdir(path)

def createDirStructure(path):
    """ test that a structure in a given path exists
        if any sub folder in path does not exist
        create it
    """
    opath = path.replace("\\","/")
    R = opath.split("/")
    if not os.path.isdir(path):
        R = R[0:len(R)-1] # cut the file name out of the folder list
    
    if isPosix:
        path = '/'+R[0]+'/';    #TODO check top level path or assume it is /media/ or /home/
    else:
        path = R[0]+"\\"
    # C:\folder\folder2\file.mp3
    # C: folder folder2 file
    # for range : folder folder2
    for x in range(1,len(R)):
        path = os.path.join(path,R[x],"")
        if os.path.exists(path) == False :
            os.mkdir(path)   
            
def createMiniPath( song ):
    from UnicodeTranslate import Translate
    """
        given a song create a path like string like the following:
            ex: Artist\Album\filename.ext
        if artist fails, return "Unknown"
            ex: Unknown\Album\filename.ext
        if album fails, return none
            ex: Artist\filename.ext
            ex: Unknown\filename.ext
        this 'mini' path can then be appended to a base path
    """
    t_art = Translate(song[MpMusic.ARTIST]).rstring
    t_abm = Translate(song[MpMusic.ALBUM]).rstring
    
    nonascii = re.compile(ur"[^a-zA-z0-9()-+_ ]")
    #extraspace = re.compile(ur"\s+")
    
    t_art = nonascii.sub("",t_art) # remove certain characters that
    t_abm = nonascii.sub("",t_abm) # don't fit standard windows filepath types

    t_art = t_art.strip()   # strip whitespace
    t_abm = t_abm.strip()
    
    if t_art == "":
        t_art = "Unknown"
    
    t_art = t_art.replace(" ","_")
    t_abm = t_abm.replace(" ","_")
    t_art = k[:25]
    t_abm = t_abm[:25]
    
    if t_abm == "" or re.match("[none|unknown]",t_abm,re.I) != None:
        path = os.path.join(t_art,fileGetFileName(song[MpMusic.PATH]));
    else:
        path = os.path.join(t_art,t_abm,fileGetFileName(song[MpMusic.PATH]));
    
    #path = extraspace.sub(" ",path) # would make a good edition
    
    return path

def pathCreateURI(path):
    path = path.replace("\\","/");
    # undefined results with quote when string is not UTF-8
    # setting utf-8 here is easier than forcing
    # the whole application to use utf-8
    path = unicode(path).encode('utf-8')
    
    string = str("file:///"+urllib.quote(path));
    return string;
    
def URICreatePath(path):
    path = path.replace("file:///","");
    return urllib.unquote(path);

def OS_FileName_Correct(filename):
    """
        filename as filename, from output fileGetName
        so, no extension and no complete path.
        
        this function will make sure that that no illegal characters are in the name
        example '/' wil be removed
        some illegal characters could still get thru.
        unicode is allowed under certain locales of isalpha
        that may pose problems for some people.
        
    """
    
    white = " +=-_.()[]{}`~@#$%^&"
    
    s = unicode(filename)
    #print "".join([x for x in s if x.isalpha() or x.isdigit() or x in "+=-_.()[]{}`~@#$%^&"])
    return "".join([x for x in s if x.isalpha() or x.isdigit() or x in white])
    
    

   
def UnixPathCorrect(path):
    """
        If the path is not found, assume there is a case error
        if there is this function will return the corrected case
        assuming there are no alternate case collisions
        if for any other reason the path is wrong an empty 
        string will be returned
    """
    R = path.split('/');
    
    if R[0] == '~':
        newpath = '~/'
    else:
        newpath = '/'+R[0]
    
    for i in range(1,len(R)):
    
        testpath = os.path.join(newpath,R[i])
        
        if os.path.exists(testpath):
            newpath = testpath;
        else:
            S = os.listdir(newpath)
            #print S
            temp = R[i].lower();
            for item in S:
                if item.lower() == temp:
                    testpath 
                    newpath = os.path.join(newpath,item)
                    break;
            else:
                print 'UnixPathCorrect %s not found'%temp
                return ''
        
    return newpath
    
def stripDriveFromPath(driveList,filepath):
    """
       Check the filepath to see if it starts with a dive from the drive list
       and remove the drive.    
    """
    filepath = unicode(filepath)
    for drive in driveList:
        if filepath.startswith(drive):
            filepath = filepath[len(drive): ]
            break;
    # huge errors on linux when the resulting path starts with a slash
    if filepath[0] == '/' or filepath[0] == '\\':
        return filepath[1:]
    return filepath
    
if isPosix: # def systemDriveList
    """
        there are no 'drives' in linux/Ubuntu
        i will therefore return a list of mounted devices found in media
        this will unfortunatley list umounted devices as well.
    """
    def systemDriveList():
        R = os.listdir('/media/');
        S = [];
        for path in R:
            fpath = os.path.join('/media',path,''); # full file path to drive list
            if os.path.isdir(fpath):
                S.append(fpath);    # append the directo
        return Settings.DRIVE_ALTERNATE_LOCATIONS + S + ['/home/','/home/Music/','/']
else:
    def systemDriveList():
        return Settings.DRIVE_ALTERNATE_LOCATIONS + ['%s:\\' % d for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists('%s:' % d)]
    
# ###################################################################
# ###################################################################
#
# Imports
#
# ###################################################################
# ###################################################################       
        
import urllib
import re
if not isPosix:
    import win32file
    import win32con
    
import hashlib

from MpGlobalDefines import *
from MpScriptingAdvanced import *
from MpScripting import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import time
from calendar import timegm
from shutil import copy        
        
        
        