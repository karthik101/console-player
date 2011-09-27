# #########################################################
# #########################################################
# File: MpThreading
# Description:
#       Main player object can be found here
# #########################################################

# basic rule fo this file: you can not directly update the gui
# all gui updates must be done through a window message*
# special care should be taken to ensure functions called from MpScripting
# do not update the display, if they do, they will need to queue through messageing
# as well
# *only true if the function call originates from a thread

# when current song is none
#QObject::connect: Cannot queue arguments of type 'QTextBlock'
#(Make sure 'QTextBlock' is registered using qRegisterMetaType().)
#QObject::connect: Cannot queue arguments of type 'QTextCursor'
#(Make sure 'QTextCursor' is registered using qRegisterMetaType().)

# fixed by adding check if null, but how can it be null at that point?
# Traceback (most recent call last):
#   File "C:\Users\Nick\Documents\My Dropbox\Scripting\PyQt\ConsolePlayer\src\MpPlayer.py", 
# line 517, in run p.updateSongRecord(p.CurrentSong,time)
#   File "C:\Users\Nick\Documents\My Dropbox\Scripting\PyQt\ConsolePlayer\src\MpPlayer.py", line 440, in updateSongRecord
#     if (newtime < song[MpMusic.LENGTH]-1 or newtime > song[MpMusic.LENGTH]+1) and newtime > 1 :
# TypeError: 'NoneType' object is not subscriptable



import os.path
from PyQt4.QtCore import *
#from MpApplication import *
from MpFileAccess import *
from MpScripting import *
from MpScriptingAdvanced import *
from MpID3 import *
from MpGlobalDefines import *


__IMPORT_VLC__    = False
__IMPORT_PHONON__ = False

try:
    import vlc
    __IMPORT_VLC__ = True
except:
    debugPreboot("No VLC Object")
       
try:
    from PyQt4.phonon import Phonon
    __IMPORT_PHONON__ = True
except:
    debugPreboot("No Phonon Object")


        
if not __IMPORT_VLC__ and not __IMPORT_PHONON__:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Music Player",
            "Unable to import a suitable media player",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    del app
    sys.exit(1)
        
PATH      = MpMusic.PATH     
EXIF      = MpMusic.EXIF     
ARTIST    = MpMusic.ARTIST   
TITLE     = MpMusic.TITLE    
ALBUM     = MpMusic.ALBUM    
GENRE     = MpMusic.GENRE    
DATESTAMP = MpMusic.DATESTAMP
COMMENT   = MpMusic.COMMENT  
RATING    = MpMusic.RATING   
LENGTH    = MpMusic.LENGTH   
SONGINDEX = MpMusic.SONGINDEX
PLAYCOUNT = MpMusic.PLAYCOUNT
SKIPCOUNT = MpMusic.SKIPCOUNT
FILESIZE  = MpMusic.FILESIZE 
BITRATE   = MpMusic.BITRATE  
FREQUENCY = MpMusic.FREQUENCY
DATEVALUE = MpMusic.DATEVALUE
SPECIAL   = MpMusic.SPECIAL  
SELECTED  = MpMusic.SELECTED 

MP_NOTHINGSPECIAL = 0
MP_OPENING = 1
MP_BUFFERING = 2
MP_PLAYING = 3
MP_PAUSED = 4
MP_STOPPED = 5
MP_ENDED = 6
MP_ERROR = 7
MP_UNKOWN = 8

def getNewAudioPlayer():

    #__IMPORT_VLC__   = False
    #__IMPORT_PHONON__ = False

    if __IMPORT_VLC__:
        debugPreboot("VLC   : Initalizing");
        return VLCObject();
    
    elif __IMPORT_PHONON__:
        if __IMPORT_VLC__:
            debugPreboot("VLC   : found");
        else:
            debugPreboot("VLC   : not found");
        debugPreboot("PHONON: Initalizing");
        return PhononObject();
    
    
class GenericMediaObject(object):
    
    instance  = None
    __player__= None
    __media__ = None

    def __init__(self):
        pass
    def isValid(self):
        return True;
        
    def Release(self):
        pass
        
    def mediaUnload(self):
        pass
        
    def mediaLoad(self,file,play=False):
        pass
        
    def mediaPlay(self):  
        pass
        
    def mediaStop(self):  
        pass
        
    def mediaPause(self):  
        pass
        
    def mediaforward(self):
        pass
        
    def mediabackward(self):
        pass
        
    def media_getTime(self):
        pass
        
    def media_setTime(self,seconds):
        pass    
        
    def mediaReady(self):
        pass   
    
    def mediaState(self):

            #return MP_NOTHINGSPECIAL
            #
            #return MP_OPENING
            #
            #return MP_BUFFERING
            #
            #return MP_PLAYING
            #
            #return MP_PAUSED 
            #
            #return MP_STOPPED
            #
            #return MP_ENDED
            #
            #return MP_ERROR

            return MP_UNKOWN

    def setVolume(self,value):
        pass
    
class VLCObject(GenericMediaObject):
    """ Instanciation of a VLC Media Object"""
    # i have everything wrapped up in control statements so
    # that even if the player does not work the application will
    # not crash
    instance  = None
    __player__= None
    __media__ = None
    def __init__(self):
        self.invoke();
    
    def invoke(self):
        """
            If the initalization fails
            an attempt can be made to restart it from the command line
            by typing:
                exec MpGlobal.Player.mp.invoke()
        """
        try:
            self.__instance__ = None;
            if isPosix:
                #'--plugin-path=/usr/lib/vlc'
                self.__instance__ = vlc.Instance('--plugin-path=%s'%Settings.POSIX_VLC_MODULE_PATH)
            else:
                self.__instance__ = vlc.Instance()
        except Exception as e:
            print "VLC instance Error: %s"%(e.args)
            
        if self.__instance__ == None:
            print "VLC instance Error: No Instance was created"
        else:    
            try:
                self.__player__ = self.__instance__.media_player_new()
            except Exception as e:
                print "VLC Player Error: %s"%(e.args)
    def isValid(self):
        return self.__instance__ != None;
    
    
    def Release(self):
        """ unload the VLC player entirely
            delete the media, player and instance
        """    
         
        if self.__media__ != None:
            self.__media__ = None
        self.__player__.release()
        self.__instance__.release()
        self.__player__ = None
        self.__instance__ = None;
    
    def mediaUnload(self):
            self.__media__ = None
            
    def mediaLoad(self,file,play=False):
        # clear the old media object
        self.__media__ = None
        # attempt to open a new file to play
        
        try:
            #print os.stat(file)
            #if isPosix: print "    . Path Fix"
            isExist = os.path.exists(file)
            #attempt to fix the file path if on a case sensitive file system
            if not isExist and isPosix: 
                # although MpGlobal.Player also does a path fix
                # we do need to check here just in case.
                newFilePath = UnixPathCorrect(file)
                if os.path.exists(newFilePath):
                    file = newFilePath
                    isExist = True
                    debug( "Path Correction: \n%s"%file )
                    
            path = pathCreateURI(unicode(file))  
            
            
            
            if isExist and self.__instance__ != None:

                #debug( "> "+path )
                #if isPosix: print "    . New Media"
                self.__media__ = self.__instance__.media_new(path)
                #if isPosix: print "    . Set Media"
                self.__player__.set_media(self.__media__)
            else:
                debug(" *** File Not Found; Instance: (%s)"%(self.__instance__ != None))
                debug("PATH: %s"%file)
                debug("URI : %s"%path)   
        except Exception as e:
            print "VLC instance Error: %s"%(e.args)
            #self.__media__
            #self.__media__ = None;
        
        
        #if isPosix: print "    . if-Play"
        if play and self.__media__ != None:
            self.mediaPlay()
            
        return (self.__media__ != None)
    
    def mediaPlay(self):  
        if self.__media__ != None:
            self.__player__.play()
        else:
            debug( "VLC instance Error : Cannot Play" )
            
    def mediaStop(self):  
        if self.__media__ != None:
            self.__player__.stop()
            self.__media__.release()
        else:
            debug( "VLC instance Error : Cannot Stop" )
            
    def mediaPause(self):  
        if self.__media__ != None:
            self.__player__.pause()
        else:
            debug( "VLC instance Error : Cannot Pause" )
            
    def mediaforward(self):
        """Go forward 1s"""
        if self.__player__ != None:
            self.__player__.set_time(__player__.get_time() + 1000)

    def mediabackward(self):
        """Go backward 1s"""
        if self.__player__ != None:
            self.__player__.set_time(__player__.get_time() - 1000)
        
    def media_getTime(self):
        if self.__media__ != None and self.mediaState() != 0:
            t = self.__player__.get_time();
            return int(t/1000)
        else:
            return 0
    def media_setTime(self,seconds):
        if self.__player__ != None:
            self.__player__.set_time(seconds*1000)
        
    def mediaReady(self):
        return self.__media__ != None
    
    def mediaState(self):
        if self.__player__ == None:
            return MP_UNKOWN;
            
        s = self.__player__.get_state();
        
        if s == vlc.State.NothingSpecial:
            return MP_NOTHINGSPECIAL
        elif s == vlc.State.Opening:
            return MP_OPENING
        elif s == vlc.State.Buffering:
            return MP_BUFFERING
        elif s == vlc.State.Playing:
            return MP_PLAYING
        elif s == vlc.State.Paused:
            return MP_PAUSED 
        elif s == vlc.State.Stopped:
            return MP_STOPPED
        elif s == vlc.State.Ended:
            return MP_ENDED
        elif s == vlc.State.Error:
            return MP_ERROR
        else:
            print "Unknown State: %s"%s
            return MP_UNKOWN
    def setVolume(self,value):
        if self.__player__ != None:
            self.__player__.audio_set_volume(value)
  
class PhononObject(GenericMediaObject):
    #instance  = None
    #__player__= None
    __media__ = None

    audioOutput = None
    mediaObject = None
    def __init__(self):

        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, None )
        self.mediaObject = Phonon.MediaObject( None )
        
        #self.mediaObject.setPrefinishMark(500)
        
        #self.mediaObject.prefinishMarkReached.connect(__finished__)
        self.mediaObject.finished.connect(__finished__)

        #reg = QVariant(Phonon.MediaSource(None))
        #reg = QVariant((None))
        #qRegisterMetaType("Phonon.MediaSource")
        #qRegisterMetaType("MediaSource")
        #id = QMetaType.type('MediaSource')

        Phonon.createPath(self.mediaObject, self.audioOutput)
        
        self.isFinished = False
    def isValid(self):
        return (self.audioOutput != None and self.mediaObject != None);
    def Release(self):
        self.mediaUnload()
        self.mediaObject = None
        self.audioOutput = None
        
    def mediaUnload(self):
        if self.__media__ != None:
            self.isFinished = False
            self.mediaObject.clear()
            self.__media__ = None

    def mediaLoad(self,file,play=False):
    
        self.isFinished = False
        
        try:
            if os.path.exists(file):
                self.__media__ = Phonon.MediaSource(file)
                if self.__media__ != None:
                    self.mediaObject.setCurrentSource(self.__media__)

        except:
            self.__media__ = None
            
        if self.__media__ != None:
            if play:
                self.mediaPlay()
            else:
                self.mediaStop()
                
        return (self.__media__ != None)
            
    def mediaPlay(self):
        
        if self.__media__ != None:
            self.isFinished = False  
            self.mediaObject.play()

    def mediaStop(self):  
        
        if self.__media__ != None:
            self.isFinished = False
            self.mediaObject.stop()
        
    def mediaPause(self):  

        if self.__media__ != None:
            self.isFinished = False
            self.mediaObject.pause()
            
    def mediaforward(self):
        pass
        
    def mediabackward(self):
        pass
        
    def media_getTime(self):
        # time is returned in milliseconds,
        # we need seconds
        bool = (self.mediaState() in (MP_PLAYING,MP_PAUSED))
        #print ("\n%d"%(self.mediaObject.remainingTime()/1000))
        if self.__media__ != None and bool:
            return (self.mediaObject.currentTime()/1000)
        else:
            return 0
        
    def media_setTime(self,seconds):
        if self.__media__ != None:
            self.mediaObject.seek(seconds*1000)  
        
    def mediaReady(self):
        return self.__media__ != None
    
    def mediaState(self):
        try :
            state = self.mediaObject.state()
        
            if self.isFinished:    
                return MP_ENDED
            
                #return MP_NOTHINGSPECIAL
            if state == Phonon.LoadingState:
                return MP_OPENING
            if state == Phonon.BufferingState:
                return MP_BUFFERING
            if state == Phonon.PlayingState:
                return MP_PLAYING
            if state == Phonon.PausedState:
                return MP_PAUSED 
            if state == Phonon.StoppedState:
                return MP_STOPPED
            
            if state == Phonon.ErrorState:
                return MP_ERROR
        except:
            pass
        return MP_UNKOWN

    def setVolume(self,value):
        self.audioOutput.setVolume(value/100.0)
        
def __finished__(arg=None):
    """
        qt .connect. has an issue with linking to member functions
        it's tempermental and i cn't figure it out
        
        This function is for phonon only, but here it lies.
    """
    MpGlobal.Player.mp.isFinished = True
  
class MediaManager(object):
    """ primary object for controlling the library, playlist and playback of music
        
    """
    mp = None # the media player object, Instance of VLCObject
    library = []
    libDisplay = []     # sorted and searched version of library
    libDelete = []
    playList = []
    selCount = 0
    external = []       # list of paths to load
    quickList = []
    isPlaying = False;
    CurrentIndex=0  # current index in the playlist to play
    CurrentSong = None
    stopNext = False    # whether to stop playback when song finishes
    stopIndex = -1     # stop playback when song at index finishes
    lastSortType = 0
    
    playState = MpMusic.PL_PLAYLIST_CONSECUTIVE
    
   
    def __init__(self,obj):
        self.mp = obj;
        self.setVolume(Settings.PLAYER_VOLUME)

        #if Settings.SCREENSAVER_ENABLE_CONTROL :
        #TODO check OS, windows only
        
            
    def load(self,song=None):
        """ given a song, attempt to load
        """
        if song == None:
            song = self.getCurrentSong(); # grabs by Currentindex
            
        self.CurrentSong = song
        
        # this was in the play function
        # it is now here as a test. the idea is that whenever a song is finished playing
        # it will load zero next. but if a different song is loaded first, that is the chosen song
        # we don't want to go to zero next
        MpGlobal.INPUT_PLAY_GOTO_ZERO = False   
        
        

        if self.CurrentSong != None:
        
            path = self.CurrentSong[PATH]
        
            if not os.path.exists(path) and isPosix: 
                    path = UnixPathCorrect(path)
                    if path != '': # if the returned path exists
                        self.CurrentSong[PATH] = path
            #if isPosix: print "   > load"
            if self.mp.mediaLoad(path) and path != '':
                # if the load was successful update the display info
                MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBARMAXVAL"),self.CurrentSong[LENGTH])    
                self.updateDisplayIndex()
                self.updateTimeDisplay(0)
                MpGlobal.Window.emit(SIGNAL("ON_SONG_LOAD_FILLTABlE")) 
                MpGlobal.Window.emit(SIGNAL("UPDATE_INFODISPLAY"),self.CurrentSong)
                
                MpMusic.AUTO_SIGNAL_ISSUED = False
                diagMessage(MpGlobal.DIAG_PLAYBACK,'{L}');
                #if isPosix: print "   < load"
                return True

        # cannot play a song, prompt the user to select a song
        self.mp.mediaUnload()   # unload any song currently loaded
        self.CurrentSong = None
        MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),0)
        MpGlobal.Window.emit(SIGNAL("UPDATE_PLAYBUTTON"),False) 
        MpGlobal.Window.emit(SIGNAL("UPDATE_INFODISPLAY"),None) 
        diagMessage(MpGlobal.DIAG_PLAYBACK,'{F}');
        #if isPosix: print "   < fail load"
        return False

    def loadNoPlayback(self,song=None):
        """
            Secondary load functionfor loading music to play
            and also run code specific for when no music is playing,
            or when music is to stop playing.
        """
        self.load(song)
        MpGlobal.Window.emit(SIGNAL("SET_PLAYBUTTON_ICON"),MpMusic.PAUSED)
        if Settings.SCREENSAVER_ENABLE_CONTROL and MpGlobal.SSService != None :
            MpGlobal.SSService.Reset()
    
    def loadSong(self,index=-1):
        if index == -1:
            index = self.CurrentIndex
            
        if index >= len(self.playList):
            print "Cannot Load index: %d"%index
        else:
            self.CurrentIndex = index
            self.playState = MpMusic.PL_PLAYLIST_CONSECUTIVE
            song = self.getPlayListIndex(self.CurrentIndex)
            self.load(song)
            MpGlobal.Window.emit(SIGNAL("SET_PLAYBUTTON_ICON"),MpMusic.PAUSED)
            
            if Settings.SCREENSAVER_ENABLE_CONTROL and MpGlobal.SSService != None :
                MpGlobal.SSService.Reset()

    def playSong(self,index=0):
        self.CurrentIndex = index
        self.playState = MpMusic.PL_PLAYLIST_CONSECUTIVE
        song = self.getPlayListIndex(self.CurrentIndex)
        self.load(song)
        self.play()
        
    def play(self):
        # if media is ready play it  
        if self.mp.mediaReady():
            self.isPlaying = True;
            self.mp.mediaPlay()
            MpGlobal.Window.emit(SIGNAL("SET_PLAYBUTTON_ICON"),MpMusic.PLAYING)
        else:
            MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"No Song To Play")

        if self.stopNext :
            self.stopIndex = -1
            
        if Settings.SCREENSAVER_ENABLE_CONTROL and MpGlobal.SSService != None :
            MpGlobal.SSService.disable()
            
    def pause(self):
        if self.mp.mediaReady():
            self.mp.mediaPause()
            MpGlobal.Window.emit(SIGNAL("SET_PLAYBUTTON_ICON"),MpMusic.PAUSED)
            
        if Settings.SCREENSAVER_ENABLE_CONTROL and MpGlobal.SSService != None :
            MpGlobal.SSService.Reset()# return to the original state, instead of right out enabling it
    
    def playPause(self):
        """Play or pause the current media object"""
        if self.mp.mediaReady():
            if self.mp.mediaState() == MP_PLAYING :
                self.pause()#self.mp.mediaPause()
            else:
                self.play()#self.mp.mediaPlay()
        else:
            #debug( "PlayPause, Not Ready %d"%self.CurrentIndex)
            self.playSong(self.CurrentIndex)
    def stop(self):
        """Stop Song Playback"""
        if self.mp.mediaReady():
            # by updateing the song display first, then 
            # stopping it, we get the illusion that the song is ready to play,
            # but not loaded.
            # otehrwise by defualt the player will display "select a song to play"
            
            MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),0) 
            #pGlobal.Window.emit(SIGNAL("UPDATE_INFODISPLAY"),self.CurrentSong) 
            self.updateTimeDisplay(0);
            #MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),self.mp.mediaStop)
            self.mp.mediaStop()
            
            
        self.isPlaying = False;
    def cont(self):
        """Stop playback when the current song finishes playing"""
        self.setStopNext(not self.stopNext)
        self.stopIndex = -1;
        
    def next(self,play=True):
        """start playing the next song (relative to current song)"""
        if MpGlobal.INPUT_PLAY_GOTO_ZERO :
            
            startNewPlaylist() # /*IDENTICLE CODE*/ from on Blank Input
                
        elif ( self.CurrentIndex < len(self.playList)-1 ):
            self.CurrentIndex += 1
            self.playSong(self.CurrentIndex)
            
        else:
            self.isPlaying = False
            self.CurrentIndex = 0;
            self.loadNoPlayback(self.getPlayListIndex(0))
            self.setStopNext(False)
    def manualNext(self):
        """
            Advance to the next song in the playlist as usual
            However increase skipcount for current song
        """
        if self.CurrentSong != None: 
            self.CurrentSong[SKIPCOUNT] += 1
        self.next()
    def autonext(self):
        """advance to the next song in the playlist, Called automatically on song End"""
        
        # if this index was marked as the stop index
        
        song = self.CurrentSong
        
        #if isPosix: print "   > LOG HISTORY"
        if Settings.LOG_HISTORY:
            history_log(MpGlobal.FILEPATH_HISTORY,song,DATESTAMP)
        #if isPosix: print "   < LOG HISTORY"   
        
        if self.CurrentIndex == self.stopIndex:
            self.setStopNext(True)
            self.stopIndex = -1
          
        if MpGlobal.INPUT_PLAY_GOTO_ZERO :
            #if isPosix: print "   . START NEW LIST"  
            startNewPlaylist() # /*IDENTICLE CODE*/ from on Blank Input
        elif MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_LOOP_ONE:
            #if isPosix: print "   . LOOP CURRENT"  
            self.playSong(self.CurrentIndex)
        elif MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_CREATE_NEW and \
            self.CurrentIndex == len(self.playList)-1 and \
            MpGlobal.INPUT_PLAY_GOTO_ZERO == False:
            #if isPosix: print "   . CREATE NEW LIST FROM INDEX"  
            
            musicSave(MpGlobal.FILEPATH_LIBRARY,MpGlobal.Player.library,Settings.SAVE_FORMAT);
            
            num = MpGlobal.Window.btn_spn.value()
            selectByNumber(num) # set selection to the numbered option option
            
            if self.stopNext:
                self.setStopNext(False)
                createPlayList(MpGlobal.PLAYLIST_SIZE,autoLoad=True) # create a new play list
                MpGlobal.INPUT_PLAY_GOTO_ZERO = False# design flaw requires this line
            else:
                createPlayList(MpGlobal.PLAYLIST_SIZE,autoStart=True) # create a new play list
            
            MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),0)    
        elif MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_LOOP_SAME and \
            self.CurrentIndex == len(self.playList)-1 and \
            MpGlobal.INPUT_PLAY_GOTO_ZERO == False:
            #if isPosix: print "   . PLAY GOTO ZERO"  
            self.playSong(0)
        elif self.stopNext and MpGlobal.INPUT_PLAY_GOTO_ZERO == False:
            #if isPosix: print "   . STOP PLAYING"  
            self.setStopNext(False)
            self.stopIndex = -1
            #updateSondRecord(self.currentSong)
            #self.isPlaying = False
            if ( self.CurrentIndex < len(self.playList)-1 ):
                self.CurrentIndex += 1
            else:
                self.CurrentIndex = 0;

            self.loadNoPlayback(MpGlobal.Player.getCurrentSong())

            MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),0)    
        else:
            #if isPosix: print "   > GOTO NEXT SONG"  
            self.next();  
            #if isPosix: print "   < GOTO NEXT SONG"
                
    def fadeNext(self):
        """
            Advance to the next song in the playlist as usual.
            However,:
            if current song pos > 90%  
                act as autoNext
            if less than 45 seconds in
                act as manual next
            if other, call next
            
        """        
        pos = self.getTime()
        if self.CurrentSong != None:
            length = self.CurrentSong[LENGTH]
            if float(pos)/length > 0.9 :
                self.updateSongRecord(self.CurrentSong)
                self.autonext()
            elif pos < 45:
                self.manualNext()
            else:
                self.next();
        
    def prev(self):
        """start playing the prev song (relative to current song)"""
        if ( self.CurrentIndex > 0 ):
            self.CurrentIndex -= 1
            self.playSong(self.CurrentIndex)
    
    def state(self):
        return self.mp.mediaState()
    def getTime(self):
        return self.mp.media_getTime();
    def setTime(self,time):
        if self.mp.mediaReady():
        
            if self.isPlaying != True:
                self.play()
            self.mp.media_setTime(time)
    def setVolume(self,value):
        if value > 100:
            value = 100
        if value < 0 :
            value = 0
        Settings.PLAYER_VOLUME  = value
        self.mp.setVolume(value)
     
    def setStopNext(self,value):
        self.stopNext = value
        MpGlobal.Window.emit(SIGNAL("SET_CONTBUTTON_ICON"),self.stopNext)
        MpGlobal.Window.emit(SIGNAL("FILL_PLAYLIST"))
        
    def getPlayListIndex(self,index):
        """
            Return the song in the playlist at the given index
            check to make sure the index is within range
            return None if it does nto exist
        """
        if index < len(self.playList):
            return self.playList[index]
        return None  
        
    def getCurrentSong(self):
        """
            Equivalent to getPlayListIndex(CurrentIndex)
            returns the song at the current player index
            or none
        """
        
        if self.CurrentIndex < len(self.playList):
            return self.playList[self.CurrentIndex]
        return None
    
    def playListPlayTime(self):
        """
            return a formatted string containing the play time
            for the current play list
            
            
            
            so far, only operations are 
                \.playlist\.append
                \.playlist\.pop
                \.playlist\s=
            this function must be called when ever the playList is changed
            
            UpdateStatusWidget(1,MpGlobal.Player.playL    istPlayTime())
            
        """
        s = 0
        for song in self.playList:
            s += song[LENGTH]
            
        return convertTimeToString(s)
    
    def updateTimeDisplay(self,time):
        if self.CurrentSong != None:
            a = convertTimeToString(time)
            b = convertTimeToString(self.CurrentSong[LENGTH])
            c = convertTimeToString(self.CurrentSong[LENGTH] - time)
            if time > self.CurrentSong[LENGTH] :
                MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEINFO"),"%s/%s"%(a,b)) 
            else:
                MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEINFO"),"%s/%s - %s"%(a,b,c))    
        else:
            MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEINFO"),"") 
        
    def updateDisplayIndex(self):
        if self.playState == MpMusic.PL_NO_PLAYLIST:
            MpGlobal.Window.emit(SIGNAL("UPDATE_INDEXINFO"),"disk") 
        else:
            MpGlobal.Window.emit(SIGNAL("UPDATE_INDEXINFO"),"%d/%d"%(self.CurrentIndex+1,len(self.playList))) 

    def updateSongRecord(self,song,newtime=-1):
        # update the given song because it has just finished playing
        # update the time if there is a discrepancy
        if song == None:
            debug("None Song Passed to updateSongRecord")
            return
        
        if newtime >= 0:
            if (newtime < song[MpMusic.LENGTH]-1 or newtime > song[MpMusic.LENGTH]+1) and newtime > 1 :
                MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s : OldTime: %d NewTime: %d"%(song[MpMusic.TITLE],song[MpMusic.LENGTH],newtime))  
                song[MpMusic.LENGTH] = newtime
            
        old = getEpochTime(song[MpMusic.DATESTAMP])
        song[MpMusic.DATESTAMP] = getNewDate()  
        # date value also needs to be updated, it is only used when searching
        song[MpMusic.DATEVALUE] = getEpochTime(song[MpMusic.DATESTAMP]) 
        new = getEpochTime(song[MpMusic.DATESTAMP])
        
        displacement = 0
        if old != 0 :
            #print "value  :",(new - old), "   normal :",(new - old)/(60*60*24)
            displacement = max(1, int(float(new - old)/(60*60*24)) ) # div by seconds in day
        # if the song has only been playd once, and this is the second play
        # we only have one data point, so bias that value
        # if the frequency is none zero, bias the old frequency
        # otherwise set the value equal to the displacement 
        #   will be set to one on first play if loaded after 2011-02-26
        #   will be set to a calculated displacement if added before 201-02-26
        n = 4
        #print "Disp:",displacement
        if song[MpMusic.PLAYCOUNT] == 1:
            song[MpMusic.FREQUENCY] = (song[MpMusic.FREQUENCY] + (n-1)*displacement)/n
        elif song[MpMusic.FREQUENCY] != 0 :
            song[MpMusic.FREQUENCY] = ((n-1)*song[MpMusic.FREQUENCY] + displacement)/n
        else:
            song[MpMusic.FREQUENCY] = displacement
            #print int(float(new - old)/(60*60*24))

        song[MpMusic.PLAYCOUNT] += 1 
        
        song[MpMusic.EXIF] = createInternalExif(song)
        # refill the library, if it was in view, its text needs to be updated
        #Player_set_unsaved()
        MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),Player_set_unsaved)
        MpGlobal.Window.emit(SIGNAL("FILL_LIBRARY"))