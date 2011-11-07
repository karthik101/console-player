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

# TODO move remaining functions
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
                song.update();
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
    song.update();    
    


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
from Song_Object import Song
from Song_LibraryFormat import *
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
        
        
        