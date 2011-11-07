# #########################################################
# #########################################################
# File: audio_vlc
#
# Description:
#       Implements an audio player by inheriting audio_baseController
#   and then implementing each of the functions
#   
#   VLC is the default audio player for this application
#   libvlc is loaded by vlc.py, and functions are made to interact with it 
# through python. VLC needs to be installed under a standard installation.
# 
# #########################################################

from audio_baseController import *
import os.path

from SystemPathMethods import *

try:
    import vlc
    __IMPORT_VLC__ = True
except:
    #debugPreboot("No VLC Object")
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

     
    class VLCObject(GenericMediaObject):
        """ Instanciation of a VLC Media Object"""
        # i have everything wrapped up in control statements so
        # that even if the player does not work the application will
        # not crash
        instance  = None    # instance of the audio driveer 
        __player__= None    # instance of object that performs playback
        __media__ = None    # instance of the current song beling played
            
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
                self.volume = value
        def getVolume(self):
            # return the current volume as a value from 0 (off or mute) to 100 (full on)
            return self.volume
         

      