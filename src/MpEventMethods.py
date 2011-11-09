
from MpGlobalDefines import *
from datatype_hex64 import *
from Song_Object import Song
from SystemPathMethods import *
from Song_MutagenWrapper import *
from MpSort import *
from MpSearch import *   

def event_load_song(filepath):

    for song in MpGlobal.Player.library:
        if song[MpMusic.PATH] == filepath :
            return;
    try:
        song = id3_createSongFromPath(filepath)
        MpGlobal.Player.library.append(song)
    except Exception as e:
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"Error With Loading Song")
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%filepath)
        MpGlobal.Window.emit(SIGNAL("DEBUG_MESSAGE"),"%s"%e.args)
    
def event_load_folder(folderpath,subfolders=True):

    if os.path.isdir(folderpath):
        R = os.listdir(folderpath)
        for file in R:
            path = os.path.join(folderpath,file)
            if pathMatchExt(path): # and pathIsUnicodeFree(path):
                MpGlobal.EventHandler.postEvent(event_load_song,path)
            elif os.path.isdir(path) and subfolders:
                MpGlobal.EventHandler.postEvent(event_load_folder,path)