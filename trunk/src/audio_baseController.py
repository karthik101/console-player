
# this is a base classs for an audio object.
# any implementation, phonon, vlc, etc needs to implement these functions

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