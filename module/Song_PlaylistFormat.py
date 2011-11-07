

from SystemPathMethods import *
from Song_Object import *
from datatype_hex64 import *

def playListSave(filepath,data,typ=0,index=0):
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
                    if comparePath( source[x][MpMusic.PATH] ,path ):
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
    
 