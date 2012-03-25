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

# TODO:
#   var song_list can be either a song or list of songs
#   functions that remove should return the list of songs removed
#   a value of NONE is an error for any function that returns songs or list of songs
# MpGlobal.Player.playlist_removeSlice(s,e=-1) remove all elements from playlist starting at s and ending at e, e==-1 means last item
# MpGlobal.Player.playlist_insert(s,song_list) insert element song_list at position s such that playlist s returns the first element in song_list
# MpGlobal.Player.playlist_getItem(index)   return song at index
# MpGlobal.Player.playlist_removeIndex(index)   remove song at index
# MpGlobal.Player.playlist_clear()
# and functions for all other playlist operations
# these functions should send signals to update display information



import os.path
from PyQt4.QtCore import *

from random import *

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

__IMPORT_VLC__    = False # derp, this is needed otherwise it will not be defined
__IMPORT_PHONON__ = False # when it is not installed

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

print "VLC: %s PHONON: %s"%(__IMPORT_VLC__,__IMPORT_PHONON__)
    
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
    #  --noaudio : force creation of base audio player instead of vlc or phonon
    
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
    quickList_Genre = []
    isPlaying = False;
    CurrentIndex=0  # current index in the playlist to play
    CurrentSong = None
    stopNext = False    # whether to stop playback when song finishes
    stopIndex = -1     # stop playback when song at index finishes
    lastSortType = 0
    
    volume = 50;
    equilizer = 0; # +/- value to add to volume
    EQ_PLAYBACK_SCALE = 2 # either, 1,2,3,4 for 100%,50%,33%,25%,etc
                          # determines maximum volume swing of equilizer for playback
    
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
        
        if self.CurrentIndex == self.stopIndex and self.CurrentIndex >= 0:
            self.setStopNext(True)
            self.stopIndex = -1;
        
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
                MpGlobal.Window.emit(SIGNAL("UPDATE_TIMEBAR"),0)    
                self.updateDisplayIndex()
                self.updateTimeDisplay(0)
                MpGlobal.Window.emit(SIGNAL("FILL_PLAYLIST")) 
                MpGlobal.Window.emit(SIGNAL("FILL_LIBRARY")) 
                MpGlobal.Window.emit(SIGNAL("UPDATE_INFODISPLAY"),self.CurrentSong)
                
                MpMusic.AUTO_SIGNAL_ISSUED = False
                diagMessage(MpGlobal.DIAG_PLAYBACK,'{L}');
                self.setEquilizer()
                #if isPosix: print "   < load"
                return True

        # cannot play a song, prompt the user to select a song
        self.mp.mediaUnload()   # unload any song currently loaded
        self.CurrentSong = None
        self.updateTimeDisplay(0)
        MpGlobal.Window.emit(SIGNAL("UPDATE_PLAYBUTTON"),False) 
        MpGlobal.Window.emit(SIGNAL("UPDATE_INFODISPLAY"),None) 
        diagMessage(MpGlobal.DIAG_PLAYBACK,'{F}');
        #if isPosix: print "   < fail load"
        return False

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
    
    def play_fromDisk(self,path):
    
        self.playState = MpMusic.PL_NO_PLAYLIST
        
        temp = id3_createSongFromPath(path)
        
        
        
        if MpGlobal.Player.load(temp) :
        
            MpGlobal.Player.play()
            self.playState = MpMusic.PL_NO_PLAYLIST
            self.updateDisplayIndex()
            
        else: # on error reload the current song
            self.loadSong()
    
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
            MpGlobal.Window.emit(SIGNAL("QUEUE_FUNCTION"),self.mp.mediaStop)
            #self.mp.mediaStop()
            
            
        self.isPlaying = False;
    def cont(self):
        """Stop playback when the current song finishes playing"""
        self.setStopNext(not self.stopNext)
        self.stopIndex = -1;
        
    def next(self,play=True):
        """start playing the next song (relative to current song)"""
        if MpGlobal.INPUT_PLAY_GOTO_ZERO :
            
            self.playlist_start(True) # /*IDENTICLE CODE*/ from on Blank Input
                
        elif ( self.CurrentIndex < len(self.playList)-1 ):
            # only change the index if in playlist playback mode
            if self.playState != MpMusic.PL_NO_PLAYLIST:
                self.CurrentIndex += 1
            
            if self.stopNext:
                self.loadSong(self.CurrentIndex)
                self.setStopNext(False)
            else:
                self.playSong(self.CurrentIndex)
            
        else:
            self.isPlaying = False
            self.CurrentIndex = 0;
            self.loadSong(0)
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
        # ###########################################################
        # set backups, and update the state machine
        
        song = self.CurrentSong
        
        if Settings.LOG_HISTORY:
            history_log(MpGlobal.FILEPATH_HISTORY,song,MpMusic.DATESTAMP)

        if self.CurrentIndex == self.stopIndex:
            self.setStopNext(True)

        # ###########################################################
        # conditionally change the song based off of the current state

        if MpGlobal.INPUT_PLAY_GOTO_ZERO :
            #if isPosix: print "   . START NEW LIST"  
            self.playlist_start(True) # /*IDENTICLE CODE*/ from on Blank Input
        elif not self.checkCurrentSong(): # somehow the index to current song was messed up
                                      # this happens if the user manually trashes the playlist and manually builds one
            self.playSong(0)
            self.setStopNext(False)
            self.stopIndex = -1
            
        elif MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_LOOP_ONE:
            #if isPosix: print "   . LOOP CURRENT"  
            self.playSong(self.CurrentIndex)
            
        elif MpGlobal.PLAYLIST_END_POLICY == MpGlobal.PLAYLIST_END_CREATE_NEW and \
            self.CurrentIndex == len(self.playList)-1 and \
            MpGlobal.INPUT_PLAY_GOTO_ZERO == False:
            #if isPosix: print "   . CREATE NEW LIST FROM INDEX"  
            
            musicSave_LIBZ(MpGlobal.FILEPATH_LIBRARY,self.library,Settings.SAVE_FORMAT|1);
            
            num = MpGlobal.Window.btn_spn.value()
            selectByNumber(num) # set selection to the numbered option option
            
            self.playList_new_fromSelection(MpGlobal.PLAYLIST_SIZE,autoStart = not self.stopNext)
            self.library_clearSelection()
            self.setStopNext(False)

            
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

            self.loadSong(self.CurrentIndex)

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
        # only change the index when in playlist playback mode
        if self.playState != MpMusic.PL_NO_PLAYLIST and self.CurrentIndex > 0:
            self.CurrentIndex -= 1

        if ( self.CurrentIndex >= 0 ) :
  
            if self.stopNext:
                self.loadSong(self.CurrentIndex)
                self.setStopNext(False)
            else:
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
        if value > 200:
            value = 200
        if value < 0 :
            value = 0

        self.volume = value
        
        self.setEquilizer() # which will then set the volume
    
    def getVolume(self):
        return self.volume
        
    def setEquilizer(self):
        """
            update the equilizer value for the volume controls
            the volume is then adjusted automatically
            
            a song contains a 15 bit unsigned integer number for the equilizer
            this value is between 0 to 32767, with 16384 being the
            value that corresponds to OFF.
            
            the eq value of the song can modify the volume of playback by as
            much as 50% of the current playback volume.
        """
        value = self.volume
        
        self.equilizer = 0;
        if self.CurrentSong != None:
            scale =  - ( float(self.CurrentSong[EnumSong.EQUILIZER] - EnumSong.EQ_MID_POINT) / EnumSong.EQ_MID_POINT )
            #print scale
            self.equilizer = ( value / self.EQ_PLAYBACK_SCALE ) * scale
            
            value += self.equilizer
            
        if value > 200:
            value = 200
        if value < 0 :
            value = 0

        #print "[%d/32767] EQ VALUE: %d VOL: %d"%(self.CurrentSong[EnumSong.EQUILIZER],self.equilizer,value)
            
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
        
        if self.CurrentIndex < len(self.playList) and self.CurrentIndex > 0:
            return self.playList[self.CurrentIndex]
        return None
        
    def checkCurrentSong(self):
        """
            return true if the CurrentIndex and CurrentSong variables agree
            return self.playList[self.CurrentIndex] == self.CurrentSong
        """
        
        state = False
        
        if self.CurrentIndex < len(self.playList) and self.CurrentIndex >= 0:
            state = self.playList[self.CurrentIndex] == self.CurrentSong
            
        if not state:
            MpGlobal.Player.CurrentIndex = -1
            
        return state
     
    # ############################### 
     
    def library_clearSelection(self): 
        #MpGlobal.Player.library_clearSelection()
        self.selCount = 0
        for x in range(len(self.library)):
            self.library[x][MpMusic.SELECTED] = False
        UpdateStatusWidget(0,self.selCount)    
        MpGlobal.Window.emit(SIGNAL("FILL_LIBRARY")) 
    
    # ###############################
    
    def playlist_create( self, song_list, size, hash_size ):
    
        playlist = [] # resulting list
        
        if len(song_list) == 0:
            return []
        # ###############################
        # add to selection from gui
        ShuffleList(song_list)

        size = min(size,len(song_list)) # length of the playlist to return
        
        if hash_size > 0:  
            # create a hash table and count the songs per artist
            # limit the max number of somgs per artist to the hash number
            D = {}
            for song in song_list:
                a = song[MpMusic.ARTIST]
                
                if a in D:
                    D[a] += 1
                else:
                    D[a] = 1
                    
                if D[a] <= hash_size:
                    playlist.append(song)
                    
                if len(playlist) == size:
                    break;

            ShuffleList(playlist)
        else:
            playlist = song_list[:size]
            
        return playlist
        
    def playList_new_fromSelection(self,size=-1,autoStart=False):
        # MpGlobal.Player.playList_new_fromSelection()
        """ create a new playlist
            pull the songs needed to make the playlist from the library
            and quick select tab.
            
            library - any song with selected = true
            quick_select - any artist / genre that is selected
        """
        song_list = getSelection(False)
        
        if size == -1:
            size = MpGlobal.PLAYLIST_SIZE
        
        playlist = self.playlist_create(song_list,size,MpGlobal.PLAYLIST_ARTIST_HASH_SIZE)
        
        self.playlist_set(playlist,autoStart) 
    
    def playlist_new( self, song_list, size, hash_size, autoStart=False ):
        # from the given list of songs create a new playlist
        # of size SIZE, and start playback if needed.
        
        playlist = self.playlist_create(song_list,size,hash_size)    
        
        self.playlist_set(playlist,autoStart)    
        
    def playlist_set(self,song_list,autoStart=False):
        """ using song_list set the list of songs as the new playlist
            begin playback at the first song in the list
        """
        self.playList = song_list[:]
        
        self.CurrentIndex = 0
        
        # if autoStart, begin playback immediatley
        # otherwiae load the current song, but wait until the current song
        # finishes playing to load the first song
        
        if autoStart :
            self.playSong(0)
            self.setStopNext(False)
        elif self.state() != MP_PLAYING:
            self.loadSong(0)
            self.setStopNext(False)
        else: # wait for the song to finish, then the new list will start  
            MpGlobal.INPUT_PLAY_GOTO_ZERO = True
            self.CurrentIndex = -1
           
        self.updatePlayTimeDisplay()
        self.updateDisplayIndex()
        
        setSearchTime()     
        
        MpGlobal.Window.tbl_playlist.updateTable(0,MpGlobal.Player.playList)
        MpGlobal.Window.tab_library.table.updateTable()
            
        playListSave(MpGlobal.FILEPATH_PLAYLIST_CURRENT,MpGlobal.Player.playList,Settings.SAVE_FORMAT)
        if Settings.SAVE_BACKUP:
            musicBackup(MpGlobal.FOLDERPATH_BACKUP,MpGlobal.Player.library,Settings.SAVE_FORMAT,MpGlobal.Force_Backup);
       
    def playlist_start( self, forceStart=False ):
        self.library_clearSelection()
    
        MpGlobal.PLAYLIST_SIZE = Settings.PLAYLIST_SIZE_DEFAULT
        MpGlobal.PLAYLIST_ARTIST_HASH_SIZE = 0
        MpGlobal.INPUT_PLAY_GOTO_ZERO = False
        
        self.stopIndex = -1

        if self.stopNext == False or forceStart == True:
            self.playSong(0)
        else:
            self.loadSong(0)
            
        self.setStopNext(False)
        
    def playlist_removeRange(self,start,end):
        """ remove, and return, the list of songs starting at 'start' and ending at 'end'
        
            if start=3, and end=7, this will return a list of songs including the song at index 3, up
                to and excluding the song at index 7.
                the 4 songs between 3 and 7 will be returned.
                
            the following must be true:     
            end  > start,
            end  <= len(playList)
        """
        # the following are equivalent
        # e-1,s-1, returns a reversed list of the same numbers
        # range(e-1,s-1,-1)
        # range(s,e)        
        index_list = range(end-1,start-1,-1)
 
        return playlist_removeIndexList( index_list )
        
    def playlist_removeIndexList(self,index_list):
        """ remove the songs found at the index in the playlist 
        
            index_list can be an unsorted list.
            
            index_list must be a list of integers as indexes into the playList
            
            this function handles the case of updating the current index when songs are removed,
            however nothing is done if the current song is in fact removed.
        """
        # list must be in reverse order for the indexes to be preserved.
        # this way the greatest index is removed first, and i will not need to
        # offset all other indexes in the list as a result.
        index_list.sort(reverse=True) 
        
        song_list = []
        
        for i in index_list:
            song_list.append( self.playList.pop(i) )
            if i < self.CurrentIndex: # update the current index for similar reseaons
                self.CurrentIndex -= 1
        # TODO: an orphan song is created if the current song is in the list to remove
        # does the following fix this
        index = self.CurrentIndex # circumvent checkCurrentSong setting CI to -1
        if index >= len(self.playList): # fix the range
            index = len(self.playList) - 1  
        
        if not self.checkCurrentSong() and index >= 0:
            if self.state()==MP_PLAYING:
                self.playSong(index)
            else:
                self.loadSong(index)
                
        self.updateSongDisplay()
        self.updatePlayTimeDisplay()
        
        MpGlobal.Window.tbl_playlist.updateTable(-1,MpGlobal.Player.playList)
        
        song_list.reverse() # items were added in reverse order to this list  
        
        return song_list
     
    def playlist_insertSongList(self,index,song_list):
    
        if index <= self.CurrentIndex: # adjust the current index + the number of songs being dropped before ti
            self.CurrentIndex += len(song_list)
            
        self.playList = self.playList[:index] + song_list + self.playList[index:]

        MpGlobal.Window.tbl_playlist.updateTable(-1,MpGlobal.Player.playList)
        
        self.updateDisplayIndex()
        self.updatePlayTimeDisplay()
        
    def playlist_reinsertIndexList(self,index_list,row):
        """ remove all songs at the indices found in index_list
            then reinsert the removed songs at index row
            
            if a removed song would affect the meaning of the row value,
            row will be udated to reflect these changes

            this function combines the following operations:
                song_list = playlist_removeIndexList(index_list)
                playlist_insertSongList(row,song_list)
            and adds the following:
                handling for when the current song is removed.
            
            index_list must be a unique set of integers less than the length of the current playlist
            example:
            
            returns:    the new range of selected songs
            
            index does not need to be sorted in any particular direction
                upon insert the original order of the songs will be preserved.
            
            0 1 2 3 4 5 6 7 8 9 
            remove 3,5,7, insert 4
            0 1 2 4 6 8 9  and 3 5 7
            insert at 3: (removing 3 will cause an update on the row index)
            0 1 2 3 5 7 4 6 8 9
        """
        # list must be in reverse order for the indexes to be preserved.
        # this way the greatest index is removed first, and i will not need to
        # offset all other indexes in the list as a result.
        
        song_list = [ self.playList[index] for index in index_list ]
        
        index_list.sort(reverse=True) 

        for i in index_list:
            self.playList.pop(i)
            if i < row:
                row -= 1;
            if i < MpGlobal.Player.CurrentIndex: # update the current index for similar reseaons
                MpGlobal.Player.CurrentIndex -= 1
           
        self.playList = self.playList[:row] + song_list + self.playList[row:]
        
        if row >= len(self.playList): # fix for when drop target is outside the range of the list
            row = len(self.playList)-1
        
        if row <= MpGlobal.Player.CurrentIndex: # update the current index for similar reseaons
                MpGlobal.Player.CurrentIndex += len(song_list)
        
        if MpGlobal.Player.CurrentSong in song_list:
            MpGlobal.Player.CurrentIndex = row + song_list.index(MpGlobal.Player.CurrentSong)   

        self.updateDisplayIndex()    

        MpGlobal.Window.tbl_playlist.updateTable(-1,MpGlobal.Player.playList)
        
        return range( row,row+len(song_list) )    
        
    def playlist_shuffleIndexList(self,index_list):
        """ take all songs at indices in index_list and shuffle there position"""
        song_list = [ self.playList[index] for index in index_list ]
        

        ShuffleList(song_list) # shuffle selection array in place
        
        for x in range(len(index_list)):
            self.playList[ index_list[x] ] = song_list[x]
            if song_list[x] == self.CurrentSong:
                self.CurrentIndex = index_list[x]
        
        
        self.updateDisplayIndex()
        
    def playlist_shuffleRandom(self,s,e):
        """ take all songs at indices in index_list and shuffle there position"""

        p1 = MpGlobal.Player.playList[:s]
        p2 = MpGlobal.Player.playList[s:e]
        p3 = MpGlobal.Player.playList[e:]
        
        shuffle(p2)
        
        self.playList = p1+p2+p3
        
        for x in range(s,e):
            if self.playList[x] == self.CurrentSong:
                self.CurrentIndex = x
        
        #self.updateDisplayIndex()
        
    def playlist_removeIndex(self,index):
    
        song = None
        
        if index >= 0 and index < len(self.playList):
        
            song = self.playList.pop(index)
            
            if index == self.CurrentIndex:
                self.playSong(0)
            elif index < self.CurrentIndex:
                self.CurrentIndex -= 1;
         
        self.updateSongDisplay()
         
        return song;
     
    def playlist_clear(self):
        self.playList = []
        self.CurrentIndex = -1
        #TODO update displayed song
        
        MpGlobal.Player.checkCurrentSong()
        #self.updateDisplayIndex()    
        self.updateSongDisplay()
        self.updatePlayTimeDisplay()

    def playlist_PlayTime(self):
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
    
    def get_playlist(self):
        return self.playList
    
    def len_playlist(self):
        return len(self.playList)
    
    def updatePlayTimeDisplay(self):
        """ send a signal to update the display of how long the current playlist is """
        UpdateStatusWidget(1,MpGlobal.Player.playlist_PlayTime())
        
    def updateSongDisplay(self):
        """ not implemented """
        # delay-call info_UpdateDisplay with argumentself.CurrentSong
        # - or call this function with no arguments:
        #   info_UpdateCurrent
        MpGlobal.Window.emit(SIGNAL("UPDATE_SONGINFO")) 
        
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
            MpGlobal.Window.emit(SIGNAL("UPDATE_INDEXINFO"),"Disk") 
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
