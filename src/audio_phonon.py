# #########################################################
# #########################################################
# File: audio_phonon
#
# Description:
#       Implements an audio player by inheriting audio_baseController
#   and then implementing each of the functions
#   
#   Phonon is distributed as part of Qt, and uses a generic
# audio decoder from the OS to play WAV and mp3 files on Windows.
# 
# #########################################################

from audio_baseController import *

try:
    from PyQt4.phonon import Phonon
    __IMPORT_PHONON__ = True
except:
    #debugPreboot("No Phonon Object")
    pass
else:

    MP_NOTHINGSPECIAL = 0
    MP_OPENING = 1
    MP_BUFFERING = 2
    MP_PLAYING = 3
    MP_PAUSED = 4
    MP_STOPPED = 5
    MP_ENDED = 6
    MP_ERROR = 7
    MP_UNKOWN = 8


    class PhononObject(GenericMediaObject):

        audioOutput = None
        mediaObject = None
        
        instance  = None    # instance of the audio driveer 
        __player__= None    # instance of object that performs playback
        __media__ = None    # instance of the current song beling played
    
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
            self.volume = value
            
        def getVolume(self):
            # return the current volume as a value from 0 (off or mute) to 100 (full on)
            return self.volume
            
    def __finished__(arg=None):
        """
            qt .connect. has an issue with linking to member functions
            it's tempermental and i cn't figure it out
            
            This function is for phonon only, but here it lies.
        """
        MpGlobal.Player.mp.isFinished = True
       