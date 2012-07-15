
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
    DSP_SETTINGS = {}    
    volume = 0;         

    def __init__(self):
        self.media=None
        self.ready = False;
        self.volume = 50;
        self.isPlaying = False
        self.time = 0;
        self.state = MP_NOTHINGSPECIAL
        pass
        
    def isValid(self):
        # return whether the media player initialized correctly
        # TODO: Can i remove this function
        return True;
        
    def Release(self):
        # TODO - this may no longer be needed
        # unload the music and delete any objects needed to 
        self.state = MP_NOTHINGSPECIAL
        pass
        
    def mediaUnload(self):
        # Remove the song from memory, making no song read yto play. 
        #
        # when finished, mediaReady should return false
        self.media=None
        self.ready = False;
        self.isPlaying = False
        self.time = 0;
        self.state = MP_NOTHINGSPECIAL
        
    def mediaLoad(self,file,play=False):
        # given a file path load the song so that it can be played.
        # when play=True call mediaPlay when finished loading
        # return true on success
        self.state = MP_OPENING
        self.media = file
        self.ready = True
        self.isPlaying = play
        self.time = 0;
        self.state = MP_PLAYING if play else MP_PAUSED
        
        return True
        
    def mediaPlay(self):  
        # no matter the current state of a song that has been loaded, continue playback.
        # if it was Stopped, start over
        # if it was paused, resume.
        if self.mediaReady():
            self.isPlaying = True
            self.state = MP_PLAYING    
        
    def mediaStop(self):  
        # Stop playback of the song. if the song is to be resumed it should 
        # somehow restart from time = 0.
        if self.mediaReady():
            self.isPlaying = False
            self.time = 0;
            self.state = MP_STOPPED
        
    def mediaPause(self):  
        # if the song is playing pause playback, otherwise do nothing.
        if self.mediaReady():
            self.isPlaying = False
            self.state = MP_PAUSED
        
    def mediaforward(self):
        # not used - but would allow for fast-fowarding
        pass
        
    def mediabackward(self):
        # not used - but would allow for rewinding
        pass
        
    def media_getTime(self):
        # return the current position of the song in seconds.
        if self.mediaReady():
            if (self.isPlaying):     # this is a work around to having a timer increment while "playing"
                self.time += 1;     # this function will be called about 8 times a second in the main player thread
        if self.time > 250:
            self.time = 0;
            self.state = MP_ENDED
            self.isPlaying = False
            
         
        return self.time;
        
    def media_setTime(self,seconds):
        # jump to the given time in seconds
        # if time is greater than the length of the song, the song finished signal should be produced.
        self.time = seconds;  
        if self.time > 250:
            self.time = 0;
            self.state = MP_ENDED
            self.isPlaying = False
            
    def mediaReady(self):
        # return true when calling mediaPlay would result in sound beling played
        # otherwise return false.
        return self.ready
    
    def mediaState(self):
        # determine the current state of the media, then return one of these values.
        
        #return MP_NOTHINGSPECIAL
        #return MP_OPENING
        #return MP_BUFFERING
        #return MP_PLAYING
        #return MP_PAUSED 
        #return MP_STOPPED
        #return MP_ENDED
        #return MP_ERROR

        return self.state;

    def setVolume(self,value):
        # value is from between 0 and 100.
        # the volume should be set accordingly.
        self.volume = value
        
    def getVolume(self):
        # return the current volume as a value from 0 (off or mute) to 100 (full on)
        return self.volume
        
    def setDSP(self,d):
        pass
    def getDSP(self):
        return {};
    def setInfo(self,song):
        pass
    def getInfo(self,song):
        return None
        