
from MpGlobalDefines import *
from datatype_hex64 import *
from Song_Object import Song
from SystemPathMethods import *
from Song_MutagenWrapper import *
from MpSort import *
from Song_Search import *   

from table_library import *
from MpScripting import *

def event_end_load_song():
    """
        void-function to run after all event_load_song have been
        run in the EventHandler.
        
        run a search for all songs added today
    """
    dt = DateTime();
    search = ".added =%s"%dt.currentDate();
    
    MpGlobal.Window.txt_searchBox.setText(search)
    #txtSearch_OnTextChange(search, -1)
    MpGlobal.Window.tbl_library.updateDisplay(search)  

def event_load_song(filepath):

    for song in MpGlobal.Player.library:
        if song[MpMusic.PATH] == filepath :
            return;
    try:
        song = id3_createSongFromPath(filepath)
        MpGlobal.Player.library.append(song)
        #todo use .added =%TODAY%
        #MpGlobal.Window.txt_searchBox.setText(".pcnt =0")
        #txtSearch_OnTextChange(".pcnt =0", -1)
        #MpGlobal.Window.tbl_library.updateDisplay(".pcnt =0") 
        MpGlobal.Window.search_label.setText("%d/%d"%(len(MpGlobal.Player.libDisplay),len(MpGlobal.Player.library)))
        
        
    except Exception as e:
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Error With Loading Song")
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%filepath)
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%e.args)
    
    # i can get away with posting multiple copies, because only one is saved.    
    MpGlobal.EventHandler.postEndEvent(event_end_load_song);

def event_load_folder(folderpath,subfolders=True):

    if os.path.isdir(folderpath):
        R = os.listdir(folderpath)
        for file in R:
            path = os.path.join(folderpath,file)
            if pathMatchExt(path): # and pathIsUnicodeFree(path):
                MpGlobal.EventHandler.postEvent(event_load_song,path)
            elif os.path.isdir(path) and subfolders:
                MpGlobal.EventHandler.postEvent(event_load_folder,path)