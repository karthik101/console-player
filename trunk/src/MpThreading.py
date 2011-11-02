# #########################################################
# #########################################################
# File: MpThreading
# Description:
#       File contains all functions and objects relating
#   to threads in the Media player.
# #########################################################
import sys;
from PyQt4.QtCore import *

from MpGlobalDefines import *
from MpScripting import *
from MpSort import *
from MpSearch import *
from MpPlayer import *

class MpThread(QThread):
    """
        Template class for threads in the Media Player
    """
    def __init__(self,parent=None):
        super(MpThread, self).__init__(parent)
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
    
    def start(self):
        super(MpThread, self).start(QThread.LowPriority)
        
    def run(self):
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Template Thread Not Initialized\n") 
       
class MediaPlayerThread(MpThread): 
    
    def run(self):
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Thread Starting")

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
                        setConsoleColor()#resets the color
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
                        diagMessage(MpGlobal.DIAG_PLAYBACK,"\n%s->N:%d O:%d;"%(song[TITLE],time,song[LENGTH]) );
                        # delaying autonext solves a Phonon Bug (Multi-Threading, registration)
                        MpMusic.AUTO_SIGNAL_ISSUED = True   # prevent multiple queueings of auto next

                        #if isPosix: print " > AUTONEXT"
                        MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),MpGlobal.Player.autonext)
                        #if isPosix: print " < AUTONEXT"
                        
                        p.updateSongRecord(song,time)
                        #if isPosix: print " . RECORD UPDATE"
                        #MpGlobal.Player.autonext()
                    # playback: play one, then wait for next song to be assigned
                    elif state == MP_ERROR and p.CurrentSong != None:
                        song = p.CurrentSong
                        MpMusic.AUTO_SIGNAL_ISSUED = True
                        MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),MpGlobal.Player.autonext)
                        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Thread Starting - %s - %s"%(song[ARTIST],song[TITLE]))
                    elif state == MP_ENDED:
                        p.setTime(0)
                        p.updateTimeDisplay(0)
                        MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),0)
                        MpGlobal.Window.emit(SIGNAL("UPDATE_PLAYBUTTON"),False) 
                        
                    self.mutex.unlock()    
        except Exception as e:
            for i in e:
                MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%str(i))
                        
            
      
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
            
class Thread_LoadMedia(MpThread):
    def run(self): 
        while MpGlobal.ENABLE_MUSIC_LOAD :
            if len(MpGlobal.Player.external) > 0:
                file = MpGlobal.Player.external.pop(0)
                
                for song in MpGlobal.Player.library:
                    if song[MpMusic.PATH] == file :
                        continue
                try:
                    song = id3_createSongFromPath(file)
                    MpGlobal.Player.library.append(song)
                except Exception as e:
                    MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Error With Loading Song")
                    MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%file)
                    MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%e.args)
                    
            else:
                MpGlobal.ENABLE_MUSIC_LOAD = False
                
        MpGlobal.Window.emit(SIGNAL("LOAD_FINISHED"))
        
        
        
        


     