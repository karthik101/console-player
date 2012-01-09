# #########################################################
# #########################################################
# File: MpPlayer
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


from SystemPathMethods import *
from SystemDateTime import DateTime
from MpScripting import *
from Song_MutagenWrapper import *
from MpGlobalDefines import *
from Song_Object import Song
from Song_LibraryFormat import *
from datatype_hex64 import *
from MpSongHistory import *

#__IMPORT_VLC__    = False
#__IMPORT_PHONON__ = False

MP_NOTHINGSPECIAL = 0
MP_OPENING = 1
MP_BUFFERING = 2
MP_PLAYING = 3
MP_PAUSED = 4
MP_STOPPED = 5
MP_ENDED = 6
MP_ERROR = 7
MP_UNKOWN = 8

from audio_baseController import *
from audio_phonon import *
from audio_vlc import *

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
            "Unable to import VLC or PHONON media player",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    del app
    sys.exit(1)

def getNewAudioPlayer():

    #__IMPORT_VLC__   = False
    #__IMPORT_PHONON__ = False
    #TODO: allow sys.argv:
    #   --vlc : force vlc
    #   --phonon : force phonon
    #  --noaudio : force creatyion of base audio player instead of vlc or phonon
    
    #return GenericMediaObject();
    
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
    
class MediaManager(object):
    """ primary object for controlling the library, playlist and playback of music
        
    """
    mp = None # the media player object, Instance of VLCObject
    library = []
    libDisplay = []     # sorted and searched version of library
    libDelete = []
    playList = []
    selCount = 0
    quickList = []
    isPlaying = False;
    CurrentIndex=0  # current index in the playlist to play
    CurrentSong = None
    stopNext = False    # whether to stop playback when song finishes
    stopIndex = -1     # stop playback when song at index finishes
    lastSortType = 0
    
    playState = MpMusic.PL_PLAYLIST_CONSECUTIVE
    
   
    def __init__(self,obj):
        """
            obj - an instance of VLCObject or PHONONObject, or any other media player
                  that extends GenericMediaObject
        """
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
        
        

        if type(self.CurrentSong) == Song:
        
            path = self.CurrentSong[MpMusic.PATH]
        
            if not os.path.exists(path) and isPosix: 
                    path = UnixPathCorrect(path)
                    if path != '': # if the returned path exists
                        self.CurrentSong[MpMusic.PATH] = path
            #if isPosix: print "   > load"
            if self.mp.mediaLoad(path) and path != '':
                # if the load was successful update the display info
                MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBARMAXVAL"),self.CurrentSong[MpMusic.LENGTH])    
                self.updateDisplayIndex()
                self.updateTimeDisplay(0)
                MpGlobal.Window.emit(SIGNAL("FILL_PLAYLIST")) 
                MpGlobal.Window.emit(SIGNAL("FILL_LIBRARY")) 
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
            self.CurrentSong[MpMusic.SKIPCOUNT] += 1
        self.next()
    def autonext(self):
        """advance to the next song in the playlist, Called automatically on song End"""
        
        # if this index was marked as the stop index
        
        song = self.CurrentSong
        
        #if isPosix: print "   > LOG HISTORY"
        if Settings.LOG_HISTORY:
            history_log(MpGlobal.FILEPATH_HISTORY,song,MpMusic.DATESTAMP)
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
            
            musicSave_LIBZ(MpGlobal.FILEPATH_LIBRARY,MpGlobal.Player.library,Settings.SAVE_FORMAT|1);
            
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
            length = self.CurrentSong[MpMusic.LENGTH]
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
        self.mp.setVolume(value)
        
    def getVolume(self):
        return self.mp.getVolume()
        
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
            s += song[MpMusic.LENGTH]
            
        return DateTime.formatTimeDelta(s)
    
    def updateTimeDisplay(self,time):
        if self.CurrentSong != None:
            a = DateTime.formatTimeDelta(time)
            b = DateTime.formatTimeDelta(self.CurrentSong[MpMusic.LENGTH])
            c = DateTime.formatTimeDelta(self.CurrentSong[MpMusic.LENGTH] - time)
            if time > self.CurrentSong[MpMusic.LENGTH] :
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
        # update the lengths if there is a discrepancy using newtime as the new length
        if song == None:
            debug("None Song Passed to updateSongRecord")
            return
        
        if newtime >= 0:
            if (newtime < song[MpMusic.LENGTH]-1 or newtime > song[MpMusic.LENGTH]+1) and newtime > 1 :
                MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s : OldTime: %d NewTime: %d"%(song[MpMusic.TITLE],song[MpMusic.LENGTH],newtime))  
                song[MpMusic.LENGTH] = newtime
            
        dt = DateTime()
        days_elapsed = dt.daysElapsed(song[MpMusic.DATESTAMP]) # number of days since the date stamp

        
        song[MpMusic.DATESTAMP] = dt.currentDateTime();
        song[MpMusic.DATEVALUE] = DateTime.now();
        
        song.updateFrequency(days_elapsed)

        song[MpMusic.PLAYCOUNT] += 1 
        
        song.update();
        # refill the library, if it was in view, its text needs to be updated
        #Player_set_unsaved()
        MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),Player_set_unsaved)
        MpGlobal.Window.emit(SIGNAL("FILL_LIBRARY"))
