
from MpGlobalDefines import *
from Song_Object import Song
from Song_LibraryFormat import *
from SystemPathMethods import *
from SystemDateTime import DateTime
from MpScripting import *

import codecs
#wf = codecs.open('filepath', 'w', 'utf-8')
#wf.write(line)

  
def history_log(filepath,song,typ): 

    #exec for song in MpGlobal.Window.tab_library.table.data: print "%s %d %s\n"%(song.id,MpMusic.DATESTAMP,song[MpMusic.DATESTAMP])

    if not os.path.exists(filepath):
        with codecs.open(filepath, 'w', 'utf-8') as wf:
            wf.write("#History\n")
    #try:
    with codecs.open(filepath, 'a', 'utf-8') as wf:
   
        data = 0
        path = song.shortPath()
        date = DateTime().currentDateTime().replace(" ","_");
        
        if (typ == MpMusic.RATING):
            data = song[MpMusic.RATING]
        else: #if (typ == MpMusic.DATESTAMP) 
            typ = MpMusic.DATESTAMP
            
        wf.write("%d %s %04X %s\n"%(typ,date,data,path))
        
        wf.close()

    return;
    
def history_load(filepath,lib):
    
    if not os.path.exists(filepath):
        return;
      
    line = True 
    newpath = filepath.replace("history","__history__");
    
    rf = codecs.open(filepath, 'r', 'utf-8')
    wf = codecs.open(newpath, 'w', 'utf-8')
    
    success = 0;
    error = 0;
    print "\nPlease Wait While Songs Are Processed. This May Take Awhile..."
    
    print "\nUpdated %d Songs -- %d Error(s)"%(success,error)
    
    #last_id = hex64(0);
    errorList = [];
    
    while line:
        
        #if MpGlobal.Application != None:
        # there is significant slow down delaying this even every 5 counts
        MpGlobal.Application.processEvents()
            
        line = rf.readline()
        wf.write(line);
        
        field = line[:line.find('#')].strip()
        comment = line[line.find('#'):].strip()
        
        if len(field) > 0:
        
            if field[0] != '#':
            
                (type,date,data,path) = field.split(" ")

                type = atoi(type)
                data = int(data,16)
                date = date.replace("_"," ");

                if __history_NewSongEntry(lib,type,date,data,path):
                    success += 1;
                else:
                    error += 1;
                    errorList.append("%d - %s"%(type,path))
                    
        print "\nUpdated %d Songs -- %d Error(s)"%(success,error)
 
    print" ... Done!" 
    
    for err in errorList:
        print "\n%s"%(err); 
             
    rf.close()
    wf.close();
    
    with codecs.open(filepath, 'w', 'utf-8') as wf:
        wf.write("#History\n")
    
    #MpGlobal.Window.debugMsg("\nUpdated %d Songs -- %d Error(s)"%(success,error))        

    return;
                
def __history_NewSongEntry(lib,typ,date,data,path):
    # fom file:
    #   item > path
    # last path prevents updating the same songs playcount twice
                    
    for song in lib:
                        
        if song.shortPath() == path:

            if (typ == MpMusic.RATING):
                song[MpMusic.RATING] = data
                song[MpMusic.SPECIAL] = True 
                song.update();
                return True;
            else:
                __history_NewDate__(date,song);
                return True;
            
    return False;
                            
def __history_NewDate__(date,song):
    time = DateTime().getEpochTime(date) 
    
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
    song.update();    
    
