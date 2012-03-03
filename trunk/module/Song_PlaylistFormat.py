
# NOTE:
# this file currently supports reading / writing of M3U files
# this is the new paylist format
# for legacy reasons, it allows reading of the old style playlist format
# if an old style format is used, the following functions will automatically handle the
# conversion  to/from the old and new styles. 

# format for binary search:
# for each song generate the following tuple, and store in an array
# ( Song, Song[PATH].lower().reverse() )  # any other path operation found in the compare_path function should be added here as well.
# sort by the reversed path.
# when searching perform a similar operation to the input path, then binary search for the song

from SystemPathMethods import *
from Song_Object import *
from datatype_hex64 import *
from SystemDateTime import DateTime

import codecs

# sort the library given to playlist load
# use a binary search to find the songs
# for 4096 songs in the library. a linear search for a playlist of 50 songs is:
#       50*4096 = 204800 comparisons  ~200k
# for a binary search it is:
#       50*12 = 600 comparisons
# plus NlogN overhead from sort= 4096*12 = 49152 ~ 50k
# it can be estimated that a binary search will be 4 times faster
# sort time >> search time

def playListSave(filepath,data,typ=0,index=0):

    ext = fileGetExt(filepath)
    
    if ext == 'playlist':
        filepath = filepath[:-8]+'m3u'
    
    playList_Save_M3U(filepath,data,typ)

def playList_Save_oldstyle(filepath,data,typ=0,index=0): 
    # index = MpGlobal.Player.CurrentIndex
    driveList = systemDriveList()
    wf = open(filepath,"w")
    wf.write("#index=%d\n"%index);
    print "Playlist Saving %d songs"%len(data)
    for x in range(len(data)):
        path = data[x][EnumSong.PATH]
        if typ > 0:#alternate save formats remove the drive
            path = stripDriveFromPath(driveList,path)
        wf.write( "%s %s\n"%(data[x].id, unicode(path).encode('unicode-escape') ) )
    wf.close()

def playListLoad(filepath,source):

    ext = fileGetExt(filepath)
    
    new_path = ""
    
    if ext == 'playlist':
        new_path = filepath[:-8]+'m3u'
    if ext == 'm3u':
        new_path = filepath
    
    if new_path != "" and os.path.exists(new_path):
        return playList_Load_M3U(new_path,source)
            
    return playList_Load_oldstyle(filepath,source)[1]


def playList_Load_oldstyle(filepath,source):
    
    if not os.path.exists(filepath):
        return (0,[]) # return empty array, then check status from that
        
    try:
        rf = open(filepath,"r")
    except:
        print "cannot open: %s"%filepath
        return (0,[]);
     
    array = []
    
    rpath = ''
    lookForDrive = False

    drivelist = systemDriveList();

    line = rf.readline()
    count = 0;
    

    last_index = 0
    
    while line:

        try:
            
            if line[0] == '#':
                R = line.split('=');
                last_index = atoi(R[1]);
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
                    if comparePath( source[x][EnumSong.PATH] ,path ):
                        array.append(source[x])
                        break
        except Exception as e:
            print "\n\n\nerror\n\n\n"
            print e
        finally:
            
            line = rf.readline()
            count += 1;
        
    rf.close()
    
    return (last_index,array)    

def playList_Save_M3U(filepath,data,typ=0): 

    driveList = systemDriveList()
    
    wf = codecs.open(filepath,"w",encoding='utf-8')

    dt = DateTime();
    dt.timer_start()
    
    for x in range(len(data)):
    
        path = data[x][EnumSong.PATH]
        
        if typ > 0:#alternate save formats remove the drive
            path = stripDriveFromPath(driveList,path)
            
        wf.write( "%s\n"%( unicode(path) ) )
        
    wf.close()
    
    dt.timer_end();
    print "Saved %d songs to m3u container in %s"%( len(data), DateTime.formatTimeDeltams(dt.timedelta))
    
def playList_Load_M3U(filepath,library):
    """
        load an M3U playlist, the file paths in the the meu file will be converted
        to a list of Song objects
        
        filepath - path to the file to load
        library - a list of songs already in memory
    """
    dt = DateTime();
    dt.timer_start()

    if not os.path.exists(filepath):
        return [] 
        
    try:
        rf = codecs.open(filepath,"r",encoding='utf-8')
    except:
        print "cannot open m3u file:\n   %s"%filepath
        return [];
     
    bsearch = SongPath_Lookup(library) 
     
    playlist = []

    line = rf.readline()
    
    count = 0
    
    while line:

        try:
        
            line = line.strip()
            
            if line[0] == '#':
                line = rf.readline() # load the next line ( a file path?) 
                continue

            song = bsearch.find(line)#path_to_song(line,library)    
                
            if song != None:
                playlist.append(song)
                
        except Exception as e:
            print "\n\n\nerror\n\n\n"
            print e
        finally:
            
            line = rf.readline()
            count += 1;
                
    rf.close()
    
    dt.timer_end();
    print "Loaded %d songs from m3u container in %s"%( len(playlist), DateTime.formatTimeDeltams(dt.timedelta))

    return playlist
    
def path_to_song(path,library):

    for song in library:
        if song[EnumSong.PATH].endswith( path ):
            return song
            
    return None

    
class SongPath_Lookup(object):
    """
        match a partial path to a Song from a given library
        of songs.
    """
    def __init__(self,library):
        
        self.lib = [None] * len( library )
        
        # create a list of ( song , reverse path ) objects
        for i in range(len(library)):
        
            song = library[i]
            path = song[EnumSong.PATH]
            
            path = self.convert_path(path)
            
            self.lib[i] = ( song , path )
            
            #print self.lib[i]
            
        g = lambda x : x[1]

        self.lib.sort(key=g)
    
    def convert_path(self,path):
        # lowercase, stick correct, and reverse the path
        return path.lower().replace("\\","/")[::-1]
    
    def find(self,path):
        """ implement a special case binary search
            a Song object will be returned if the following is true:
                song[EnumSong.PATH].endswith(path)
        """
        
        path = self.convert_path(path)
        
        # now find a path that starts with 'path' in the  
        s,e = 0,len(self.lib)-1

        while s <= e:
            
            i = (s+e) / 2
            
            item = self.lib[i][1]
            
            #print s,i,e, item, path
            
            if item.startswith(path):
                 return self.lib[i][0]      
            
            if   path < item:
                e = i - 1
            elif path > item:
                s = i + 1   
            
        return None
          
     

if __name__ == "__main__":
    lib = [
            {EnumSong.PATH: "abc"}, \
            {EnumSong.PATH: "def"}, \
            {EnumSong.PATH: "ghi"}, \
            {EnumSong.PATH: "jkl"}, \
            {EnumSong.PATH: "mno"}, \
            {EnumSong.PATH: "pqr"}, \
            {EnumSong.PATH: "stu"}, \
            {EnumSong.PATH: "vwx"}, \
    
          ]
    
    

    
    bsearch = SongPath_Lookup(lib)
        
    for item in lib:
        print item[EnumSong.PATH],bsearch.find( item[EnumSong.PATH] )
        
    lib2 = [
            {EnumSong.PATH: "bc"}, \
            {EnumSong.PATH: "ef"}, \
            {EnumSong.PATH: "hi"}, \
            {EnumSong.PATH: "kl"}, \
            {EnumSong.PATH: "no"}, \
            {EnumSong.PATH: "qr"}, \
            {EnumSong.PATH: "tu"}, \
            {EnumSong.PATH: "wx"}, \
    
          ] 
    lib3 = [
            {EnumSong.PATH: "c"}, \
            {EnumSong.PATH: "f"}, \
            {EnumSong.PATH: "i"}, \
            {EnumSong.PATH: "l"}, \
            {EnumSong.PATH: "o"}, \
            {EnumSong.PATH: "r"}, \
            {EnumSong.PATH: "u"}, \
            {EnumSong.PATH: "x"}, \
    
          ] 
     
    #for item in lib2:
    #    print item[EnumSong.PATH],bsearch.find( item[EnumSong.PATH] )   
    #for item in lib3:
    #    print item[EnumSong.PATH],bsearch.find( item[EnumSong.PATH] )     
        
    print bsearch.find( "a" )  # none end with a      
    print bsearch.find( "z" )  # none end with z
        
 