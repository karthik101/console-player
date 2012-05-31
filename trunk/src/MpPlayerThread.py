# #########################################################
# #########################################################
# File: MpPlayerThread
# Description:
#       File contains all functions and objects relating
#   to threads in the Media player.
# goals for this file
#   Remove MpThread. no need for a base class that DOES NOTHING
#
# #########################################################
import sys;
from PyQt4.QtCore import *

from MpGlobalDefines import *
from Song_Object import Song
from datatype_hex64 import *
from MpScripting import *
from MpSort import *
from Song_Search import *
from MpPlayer import *

import traceback

class MediaPlayerThread(QThread): 
    
    def __init__(self,parent=None):
        super(MediaPlayerThread, self).__init__(parent)
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.restart = False
        self.abort = False
        self.RunOnce = False
        
        # define what function to call when 'run' is called

    def __del__(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()
    
    def run(self):

        time = 0
        state = 0
        p = MpGlobal.Player
        a = b = c = ""
         
        # this try is for debug only and should be removed later
        # TODO: on POSIX i get a random crash (SEGFAULT?) on song change
        try:
         
            while True :
                
                
                QThread.msleep(125)
                #on application Quit, i get an error
                # seems that the thread cant quit during the sleep.
                # as well as several errors where the application does
                # not fully close ( this thread
                # still alive in the process ID in windows)
                # 
                if (MpGlobal == None):
                    break;  
                if (MpGlobal.Player == None):
                    break;  
                time = MpGlobal.Player.getTime()
                state = MpGlobal.Player.state()
                
                if MpGlobal.Console_State_Counter > 0:
                    MpGlobal.Console_State_Counter -= 1;
                    if MpGlobal.Console_State_Counter == 0:
                        MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),setConsoleColor) # reset color
                        
                        #MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Console_State_Counter=0")
                if p.isPlaying :
                    self.mutex.lock()
                    if state == MP_PLAYING :
                        MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),time)
                        p.updateTimeDisplay(time) # update time string                   
                    elif state == MP_ENDED and p.playState == MpMusic.PL_PLAYLIST_CONSECUTIVE and MpMusic.AUTO_SIGNAL_ISSUED == False:
                        # MpMusic.AUTO_SIGNAL_ISSUED is a signal that will prevent this segment from
                        #   from being running again until a new song is loaded in some way
                        # this code can only be run if we are in playlist playback mode "CONSECUTIVE", and a song has finished playing
                        song = p.CurrentSong
                        if song != None:
                            diagMessage(MpGlobal.DIAG_PLAYBACK,"\n%s->N:%d O:%d;"%(song[MpMusic.TITLE],time,song[MpMusic.LENGTH]) );
                            # delaying autonext solves a Phonon Bug (Multi-Threading, registration)
                            MpMusic.AUTO_SIGNAL_ISSUED = True   # prevent multiple queueings of auto next

                            #if isPosix: print " > AUTONEXT"
                            MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),MpGlobal.Player.autonext)
                            #if isPosix: print " < AUTONEXT"
                            
                            p.updateSongRecord(song,time)
                            #if isPosix: print " . RECORD UPDATE"
                            #MpGlobal.Player.autonext()
                    elif state == MP_ENDED and p.playState == MpMusic.PL_NO_PLAYLIST:
                        MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),MpGlobal.Player.loadSong)
                        
                    # playback: play one, then wait for next song to be assigned
                    elif state == MP_ERROR and p.CurrentSong != None:
                        song = p.CurrentSong
                        MpMusic.AUTO_SIGNAL_ISSUED = True
                        MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),MpGlobal.Player.autonext)
                        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Thread Starting - %s - %s"%(song[MpMusic.ARTIST],song[MpMusic.TITLE]))
                    elif state == MP_ENDED:
                        p.setTime(0)
                        p.updateTimeDisplay(0)
                        MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),0)
                        MpGlobal.Window.emit(SIGNAL("UPDATE_PLAYBUTTON"),False) 
                        
                    self.mutex.unlock()    
        except Exception as e:
            for i in e:
                MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%str(i))
                        
                report = traceback.format_exc().replace(', line', "\nLINE:").replace(', in', '\nMETHOD:').replace('  File', "\nFILE:")
                report += "\nARGS: %s"%e.args
                report += "\nMESSAGE: %s"%e.message
                
                print report
      
        if (MpGlobal == None):
            # please please please may this code
            # be totally unreachable
            # looks like it can be reached...
            # TODO: why?
            print "Thread Crash - No Parent"
            wf = open("./CRASH_REPORT.txt","w")
            wf.write("Application Crashed unexpectedly\n")
            wf.write("Main program No Longer Exists\n")
            wf.write("Thread has no Parent\n")
            wf.close();
        else:    
            MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Thread Ended")
       
       
        
        


     