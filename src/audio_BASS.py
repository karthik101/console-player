
# this is a base classs for an audio object.
# any implementation, phonon, vlc, etc needs to implement these functions
# the 

from audio_baseController import *
import os.path

from SystemPathMethods import *
 
from Song_Object import *
 
import PyBASS    
  
# TODO: A hack is needed for stopping playback / detecting end of playback
# when playback is finished status will return stopped.
# therefor a call to mp.stop must set some kind of flag
  
def toUTF16(string):
    return unicode(string).encode("utf-16")[2:]
    
class PyBASSPlayer(GenericMediaObject):
    
    def __init__(self,plugin_path=""):
        self.invoke(plugin_path);
        
        self.DSP_SETTINGS = {"STEREO2MONO":0,"DSPTEST":True}
    
    def invoke(self,plugin_path):
        #plugin_path = "D:\\Dropbox\\Scripting\\PyQt\\console-player\\src\\user\\plugins\\"
        PyBASS.bass_init();    
        
        # get all dlls in the plugins folder and attempt to load them
        for plugin in [ p for p in os.listdir(plugin_path) if fileGetExt(p).lower()=='dll' ]:
            
            path = os.path.join(plugin_path,plugin);
            
            val = PyBASS.load_plugin(path);
            print "Loading Plugin: %s %s"%(plugin,val==0)
                
    def isValid(self):
        return True;
    
    
    def Release(self):
        """ unload the VLC player entirely
            delete the media, player and instance
        """    
         
        PyBASS.bass_free()
    
    def mediaUnload(self):
        PyBASS.unload();
            
    def mediaLoad(self,file,play=False):
        ret = False;
        try:
            #print os.stat(file)
            #if isPosix: print "    . Path Fix"
            self.mediaUnload(); # remove the old file
            
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
                    
            if not isPosix:        
                path = toUTF16(file)  
            else:
                path = file;

            if isExist:
                # TODO - File load error
                # python claims the file exists but sometimes 
                # the load still fails, claiming the path does not exist.
                # by simply re encoding the file path and checking
                # if the file exists again solves the issue. strange.

                for i in range(5):
                    path_utf16 = toUTF16(file);
                    fex = PyBASS.utf16_fexists(path_utf16)
                    if fex:
                        ret = PyBASS.load(path_utf16,1);
                        if i > 0: 
                            print "Loaded on %d-th attempt"%i
                        PyBASS.setDSPBlock( self.DSP_SETTINGS )
                        #print self.DSP_SETTINGS
                        break;
                else:
                    print "for fell thru on load."
                    raise IOError("Failed to load file");
            else:
                print "file not found"
                #debug(" *** File Not Found;")
                #debug("PATH: %s"%file)
        except IOError:
            raise IOError("Failed to load file");
        except Exception as e:
            
            print "VLC instance Error: %s"%(e.args)
            #self.__media__
            #self.__media__ = None;
        
        
        #if isPosix: print "    . if-Play"
        if play :
            self.mediaPlay()
        elif ret: # if loaded successfully
            # initial state is STOPPED which is used as ENDED
            # start then pause to get the state away from stopped
            PyBASS.play();
            PyBASS.pause();
   
        return ret
    
    def mediaPlay(self):  
        PyBASS.play();
            
    def mediaStop(self):
        PyBASS.setPosition(0);
        PyBASS.pause(); 
            
    def mediaPause(self):  
        PyBASS.pause();
            
    def mediaforward(self):
        """Go forward 1s"""
        
        PyBASS.setPosition(PyBASS.getPosition() + 1)

    def mediabackward(self):
        """Go backward 1s"""
        PyBASS.setPosition(PyBASS.getPosition() - 1)
        
    def media_getTime(self):
        return int(PyBASS.getPosition())
    def media_setTime(self,seconds):
        PyBASS.setPosition(seconds)
        
    def mediaReady(self):
        return True;
    
    def mediaState(self):
            
        s = PyBASS.status();
        
        #if s == vlc.State.NothingSpecial:
        #    return MP_NOTHINGSPECIAL
        #elif s == vlc.State.Opening:
        #    return MP_OPENING
        if s == PyBASS.P_STALLED:
            return MP_BUFFERING
        elif s == PyBASS.P_PLAYING:
            return MP_PLAYING
        elif s == PyBASS.P_PAUSED:
            return MP_PAUSED 
        #elif s == PyBASS.P_STOPPED:
        #    return MP_STOPPED
        elif s == PyBASS.P_STOPPED:
            return MP_ENDED
        #elif s == vlc.State.Error:
        #    return MP_ERROR
        else:
            print "Unknown State: %s"%s
            return MP_UNKOWN
            
    def setVolume(self,value):
        PyBASS.setVolume(max(0.0,min(1.0,value/100.0)));

    def getVolume(self):
        # return the current volume as a value from 0 (off or mute) to 100 (full on)
        return PyBASS.getVolume();
     
    def getInfo(self):
        return PyBASS.getSongInfo();
        
    def setInfo(self,song):
        D = {};
        D["DSP_AVERAGE_MAGNITUDE"] = song[EnumSong.EQUILIZER]
        PyBASS.setSongInfo(D);
        
    def setDSP(self,dict_dsp):
        """
            before this can be used,
            the subchannel struct needs memory of which blocks are on.
            it then needs to call the respective free for each DSP block that
            is on.
            dict_dsp is a dict-of-tuples-of arguments eg:
            
            STEREO2MONO : (i,) # i can  be 0 - off, 1-R,2-L,3-MONO
            DSPTEST : True
        """
        
        self.DSP_SETTINGS = dict_dsp
        
    def updateDSP(self,dict_dsp):
        if "updateDSPBlock" in PyBASS.__dict__:
            #print "pybass dsp update"
            PyBASS.updateDSPBlock(dict_dsp);
            for key,val in dict_dsp.items():
                self.DSP_SETTINGS[key] = val;
        
    def getDSP(self):
        return self.DSP_SETTINGS
        