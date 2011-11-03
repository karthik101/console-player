
# this is a base classs for an audio object.
# any implementation, phonon, vlc, etc needs to implement these functions
# the 

MP_NOTHINGSPECIAL = 0
MP_OPENING = 1
MP_BUFFERING = 2
MP_PLAYING = 3
MP_PAUSED = 4
MP_STOPPED = 5
MP_ENDED = 6
MP_ERROR = 7
MP_UNKOWN = 8
    
class GenericMediaObject(object):
    
    instance  = None    # instance of the audio driveer 
    __player__= None    # instance of object that performs playback
    __media__ = None    # instance of the current song beling played
    volume = 0;         
    
    def __init__(self):
        pass
    def isValid(self):
        return True;
        
    def Release(self):
        # TODO - this may no longer be needed
        # unload the music and delete any objects needed to 
        pass
        
    def mediaUnload(self):
        # Remove the song from memory, making no song read yto play. 
        #
        # when finished, mediaReady should return false
        pass
        
    def mediaLoad(self,file,play=False):
        # given a file path load the song so that it can be played.
        # when play=True call mediaPlay when finished loading
        pass
        
    def mediaPlay(self):  
        # no matter the current state of a song that has been loaded, continue playback.
        # if it was Stopped, start over
        # if it was paused, resume.
        pass
        
    def mediaStop(self):  
        # Stop playback of the song. if the song is to be resumed it should 
        # somehow restart from time = 0.
        pass
        
    def mediaPause(self):  
        # if the song is playing pause playback, otherwise do nothing.
        pass
        
    def mediaforward(self):
        # not used - but would allow for fast-fowarding
        pass
        
    def mediabackward(self):
        # not used - but would allow for rewinding
        pass
        
    def media_getTime(self):
        # return the current position of the song in seconds.
        pass
        
    def media_setTime(self,seconds):
        # jump to the given time in seconds
        # if time is greater than the length of the song, the song finished signal should be produced.
        pass    
        
    def mediaReady(self):
        # return true when calling mediaPlay would result in sound beling played
        # otherwise return false.
        pass   
    
    def mediaState(self):
        # determine the current state of the media, then return one of these values.
        
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
        # value is from between 0 and 100.
        # the volume should be set accordingly.
        pass
        
    def getVolume(self):
        # return the current volume as a value from 0 (off or mute) to 100 (full on)
        return self.volume
        
        
        