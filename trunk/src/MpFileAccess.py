# #########################################################
# #########################################################
# File: MpFileAccess
# Description:
#       Functions the deal with the OS and file paths go here
#   hopefully all os specific code can be grouped here.
# #########################################################
import os
import sys



try:
    import pylzma
except:
    print "cannot import pylzma"
    pylzma = None
    
isPosix = os.name == 'posix'
__devmode = "-devmode" in sys.argv;

def getInstallPath(forcehome=False):
    """
        Return the path that the application is installed in
        Assume first that it is installed localled
        Then assume it is installed to the appdata folder
        
        application is installed if a settings.ini file exists
        if that file does not exist then return no path
    """
    
    _localname_ = "user"   
    _appdataname_ = "ConsolePlayer"
    
    arg0path = fileGetPath(sys.argv[0])
    
    #path = os.path.join(os.getcwd(),_localname_,"");
    path = os.path.join(arg0path,_localname_,"");
    file = os.path.join(path,"settings.ini");
    if os.path.exists(file):
        debugPreboot("Install Path: %s"%path)
        return path
    
    # getenv('USERPROFILE') returns C:/Users/Nick/ or /home/nick/
    if isPosix: # get a global directory to save to
        home = os.getenv("HOME")
    else:
        home = os.getenv("APPDATA")
    
    
    if home != None and (not __devmode or "--install=home" in sys.argv): #only use global install path when not developing
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
 
# ##############################
#  Library save formats
def musicSave_LIBZ(filepath,songList,typ=0,block_size=128):
    """
        save a new file, but first compress it using LZMA.
        
        file is saved as a binary file.
       
        HEADER:
            several 8 byte frames in a 4:4 byte pattern
            4 bytes describing the value in format 'LXXX'
            4 byte integer
         
            the header ends when the first string 'SIZE' is found
            
        Frame
            8 byte header, followed by SIZE bytes corresponding to X LZMA compressed song representations.
            Frame Header:
                4 bytes - the word 'SIZE'
                4 bytes - unsigned integer, size of frame, excluding frame header
            Frame Body:
                SIZE bytes compressed using pyLZMA.compress()
            
            
        each frame will compress
        
        HEADERS:
        LVER - VERSION    :outlines if any changes to reading will be needed (future proofing)
        LTYP - TYPE       : bitwise or combination of save settings
                          :  1 - no compression
                          :  2 - remove drie list from start of path ( multi os mode )
        LBLK - BLOCK SIZE : maximum number of songs per block, after decompression 
        LCNT - COUNT      : count of all songs saved to the file        
        LFMT - SNG FORMAT : number of lines per song record     
        
        Based off of the following two docstrings. there is no reason to store the parameters used for saving.
        
        compress(string, 
             dictionary=23, 
             fastBytes=128, 
             literalContextBits=3, 
             literalPosBits=0, 
             posBits=2, 
             algorithm=2, 
             eos=1, 
             multithreading=1, 
             matchfinder='bt4') 

            Compress the data in string using the given parameters, returning a string containing 
            the compressed data.


        decompress(data[, maxlength]) 
            Decompress the data, returning a string containing the decompressed data. 
            If the string has been compressed without an EOS marker,
            you must provide the maximum length as keyword parameter.


        decompress(data, bufsize[, maxlength])
            Decompress the data using an initial output buffer of size bufsize.
            If the string has been compressed without an EOS marker, 
            you must provide the maximum length as keyword parameter.
    """
    
    s = datetime.datetime.now()
    
    with open(filepath,"wb") as FILE:
        FILE.write( struct.pack("4sI","LVER",1) );             # 
        FILE.write( struct.pack("4sI","LTYP",typ) );           # 
        FILE.write( struct.pack("4sI","LBLK",block_size) );    # number of songs in each block
        FILE.write( struct.pack("4sI","LCNT",len(songList)) ); # 
        FILE.write( struct.pack("4sI","LFMT",Song.repr_length() ) );
        LIBZ_write_songList(FILE,songList,typ,block_size)
        
    e = datetime.datetime.now()
    print "Saved %d songs to libz container in %s"%( len(songList), (e-s))
    
def LIBZ_write_songList(FILE,songList,typ,block_size): 
    """
        typ: bitwise or combination of flags.
            1 - no compression
            2 - remove drive
    """
    i=0;
    l = len(songList);
    
    
    drivelist=[];
    if typ&2 == 2: 
        drivelist=systemDriveList(); # fill this with values
        print "save using drive list: %s"%drivelist
        

    while i < l:
        block=""
        for x in xrange(block_size):
            if i < l:
                block += songList[i].__repr__(drivelist);
            else: break;
            i+=1;
            
        if typ&1 == 0 and pylzma != None: # no compression for typ|=1 
            # exec MpGlobal.t1=23;MpGlobal.t2=128;
            #dictionary=MpGlobal.t1,fastBytes=MpGlobal.t2
            block = pylzma.compress(block);

            
        # write a header for the block, SIZE=length of the block
        FILE.write( struct.pack("4sI","SIZE",len(block)) );
        FILE.write(block);

def LIBZ_decompress_to_file(src,dst):

    header=""
    data=""
    key =""
    H={};
    val =0
    
    with open(src,"rb") as FILE:
        # read the header
        bin = FILE.read(8);
        key,val = struct.unpack("4sI",bin)
        while key != "SIZE" and bin:
            header += "%s=%d\n"%(key,val);
            H [key] = val;
            bin = FILE.read(8);
            if bin:
                key,val = struct.unpack("4sI",bin)
        # now  read the data from the file.         
        typ = H.get("LTYP",0)      # needed to restore each song record.
        bin = FILE.read(val);        
        while bin:
        
            if typ&1 == 0 and pylzma != None:
                data += pylzma.decompress(bin);
            else:
                data += bin;
            bin = FILE.read(8);
            if bin:
                key,val = struct.unpack("4sI",bin)
                bin = FILE.read(val); # read val bytes from the frame   
        #data += FILE.read();
    
    with open(dst,"w") as FILE:
        FILE.write( header );
        FILE.write( data );
        
def LIBZ_compress_to_file(src,dst):

    header=""   #the binary form of header data
    data=""     # the binary form of text data ( may not be compressed )
    block=""    # a single block of data
    
    
    typ=0;
    blk=128;
    fmt=6;
    
    with open(src,"r") as FILE:
        line = FILE.readline()
        while line[0]=='L' and line[4] == '=': #TODO: this should never be a band name right?
            key,val= line.strip().split('=');
            header += struct.pack("4sI",key,int(val.strip()))
            if key == "LTYP": typ = int(val.strip());
            if key == "LBLK": blk = int(val.strip());
            if key == "LFMT": fmt = int(val.strip());
            line = FILE.readline()
            
        m=(blk*fmt)
        i=0;
        while line:
            # read blocks... the first line has already been read
            
            block="" # reset the block data
            while i < m and line:
                block += line
                line = FILE.readline()
                i+=1;
            i=0

            print ("%s...%s"%(block[:8],block[-8:])).replace('\n','<>')
            if typ&1==0 and pylzma != None:
                block=pylzma.compress(block)
 
            data += struct.pack("4sI","SIZE",len(block) );
            data += block;

    
    with open(dst,"wb") as FILE:
        FILE.write( header );
        FILE.write( data );
   
def musicLoad_LIBZ(filepath):
    """
        load the specified .libz file and return an array of songs.
    """
    

    if not os.path.exists(filepath):
    
        # temporary code:
        path = fileGetPath(filepath)
        file = fileGetName(filepath) + ".library"
        print "\n\n%s\n\n"%file
        fp = os.path.join(path,file)
        if os.path.exists(fp):
            return musicLoad(fp)
        # end temporary code    
        return [];
    
    R=[];
    drivelist = [];
    cnt = 0
    s = datetime.datetime.now()
    
    with open(filepath,"rb") as FILE:
        # ##################################
        # read the header
        header={};
        bin = FILE.read(8);
        key,val = struct.unpack("4sI",bin)
        while key != "SIZE" and bin:
            header[key] = val;
            bin = FILE.read(8);
            if bin:
                key,val = struct.unpack("4sI",bin)
                
        # ##################################
        # process the header dictionary
        typ = header.get("LTYP",0)      # needed for restoring file paths
        blk = header.get("LBLK",128)    # not really needed
        fmt = header.get("LFMT",Song.repr_length()) # needed to restore each song record.
        cnt = header.get("LCNT",0)
        
        if typ&2 == 2: 
            drivelist=systemDriveList(); 
            
        # ##################################
        # now  read the data from the file.         
        bin = FILE.read(val);        
        while bin:
        
            if typ&1 == 0 and pylzma != None: #compression is only used when typ&1 == 0.
                bin = pylzma.decompress(bin);
            
            R += LIBZ_process_block( bin , typ, fmt, drivelist );

            bin = FILE.read(8);
            if bin:
                key,size = struct.unpack("4sI",bin)
                bin = FILE.read(size); # read val bytes from the frame  
   
    e = datetime.datetime.now()
    print "Loaded %d/%d songs from libz container in %s"%(len(R),cnt,(e-s))
    return R;
   
def LIBZ_process_block(data,typ,fmt, drivelist):
    """
        given a decompressed block of songs return a list of songs.
    """
    R = [];
    
    i=0;
    j=0;
    l = len(R);
    
    s=0;
    e=0;
    for j in range(fmt):
        e = data.find("\n",e+1);
        if e==-1: # both negative one or the index of a \n, will return a slice without a newline
            break;

    while e != -1:  # this block of  code is skippped when the data only contains one song.
        repr = data[s:e]
        if len(repr) > 0:
            R.append( Song( repr,DRIVELIST=drivelist ) );
        
        # get the next song representation
        e+=1; # skip the new line
        s=e; 
        for j in range(fmt):
            e = data.find("\n",e+1);
            if e==-1:
                break;
                
    # restore the last song in the block.        
    
    repr = data[s:e]
    
    
    if len(repr) > 0:   
        R.append( Song( repr ) );
    
    return R;

# MusicLoad and MusicSave are old functions.    
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
            line2 = os.path.join("D:\\" , line2)
        
            
        array[index] = Song()
        
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
    fullname = name+date+'.libz'
    h,m = time.split(':')
        
    #if (atoi(h) > 12) or force:  # save backups in the afternoon only
    
    R = []
    dir = os.listdir(path)
    for file in dir:
        if file.startswith(name) and fileGetExt(file) == "libz":
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
        musicSave_LIBZ(newbu,MpGlobal.Player.library,Settings.SAVE_FORMAT);
     
# ##########################
# custom playlist formats
     
def playListSave(filepath,data,typ=0,index=0):
    # index = MpGlobal.Player.CurrentIndex
    driveList = systemDriveList()
    wf = open(filepath,"w")
    wf.write("#index=%d\n"%index);
    print "Playlist Saving %d songs"%len(data)
    for x in range(len(data)):
        path = data[x][MpMusic.PATH]
        if typ > 0:#alternate save formats remove the drive
            path = stripDriveFromPath(driveList,path)
        wf.write( "%s %s\n"%(data[x].id, unicode(path).encode('unicode-escape') ) )
    wf.close()
    
def playListLoad(filepath,source):
    
    if not os.path.exists(filepath):
        return [] # return empty array, then check status from that
        
    try:
        rf = open(filepath,"r")
    except:
        print "cannot open: %s"%filepath
        return [];
     
    array = []
    
    rpath = ''
    lookForDrive = False
    
    if Settings.SAVE_FORMAT == MpGlobal.SAVE_FORMAT_CWD:
        rpath = os.getcwd()[0]

    
    drivelist = systemDriveList();

    line = rf.readline()
    count = 0;
    

    while line:

        try:
            
            if line[0] == '#':
                R = line.split('=');
                Settings.PLAYER_LAST_INDEX = atoi(R[1]);
                line = rf.readline() # load the next line ( a file path?) 
                
            line = line.strip()
            
            if line[:2] == '0x':
                id,path = line.split(' ',1)
                id = hex64(id)
            else:
                id = hex64(0)
                path = line
            
            try:
                _ = unicode(path.strip(),'unicode-escape')
            except:
                pass
            else:
                path = _;
            
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
            
            #print path[10:85]
            
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
        except:
            print "\n\n\nerror\n\n\n"
        finally:
            
            line = rf.readline()
            count += 1;
            
            if count%25 == 0: # was Settings.SEARCH_STALL, but even 100 was way to much (25 still is)
                MpGlobal.Application.processEvents();
        
    rf.close()
    return array

# #########################  
  
def history_log(filepath,song,typ): 

    #exec for song in MpGlobal.Window.tbl_library.data: print "%s %d %s\n"%(song.id,MpMusic.DATESTAMP,song[MpMusic.DATESTAMP])

    if not os.path.exists(filepath):
        wf = open(filepath,"w")
        wf.write("#History\n")
        wf.close()
    #try:
    wf = open(filepath,"a")
    
    datetime = time.localtime(time.time())
    
    data = "None"
    
    if (typ == MpMusic.RATING):
        data = "%d"%song[MpMusic.RATING]
        path = createMiniPath(song)
    else: #if (typ == MpMusic.DATESTAMP)
        data = time.strftime("%Y/%m/%d %H:%M",datetime)
        typ = MpMusic.DATESTAMP

    art = song[MpMusic.ARTIST].encode('unicode-escape') 
    tit = song[MpMusic.TITLE].encode('unicode-escape')
    wf.write("%s %d %-20s # %-30.30s - %-30.30s\n"%(song.id,typ,data,art,tit))
    
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
                
def __history_NewSongEntry(lib,typ,data,id):
    # fom file:
    #   item > path
    # last path prevents updating the same songs playcount twice
                    
    for song in lib:
                        
        if song.id == id:

            if (typ == MpMusic.RATING):
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
# Song Creation (from string) - TODO these can all be removed at 0.5.0.0
# ######################################################
 
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
    t_art = t_art[:25]
    t_abm = t_abm[:25]
    
    if t_abm == "" or re.match("[none|unknown]",t_abm,re.I) != None:
        path = os.path.join(t_art,fileGetFileName(song[MpMusic.PATH]));
    else:
        path = os.path.join(t_art,t_abm,fileGetFileName(song[MpMusic.PATH]));
    
    #path = extraspace.sub(" ",path) # would make a good edition
    
    return path

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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import struct

from MpGlobalDefines import *
from MpSong import Song
from datatype_hex64 import *
from MpSort import *
from MpSearch import *
from MpScripting import *
from MpID3 import *
from SystemPathMethods import *


import time
import datetime
from calendar import timegm
from shutil import copy        
        
        
        