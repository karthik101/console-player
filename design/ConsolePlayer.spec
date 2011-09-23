# -*- mode: python -*-

"""
    ConsolePlayer.spec
        spec File for building ConsolePlayer with PyInstaller
    ----------------------------------------------------------

    Update PATH_TO_DEV_ROOT to the folder where you have
        placed the Console Player source.
    
    all other paths will automatically be updated from that value
    
"""

PATH_TO_DEV_ROOT = "C:/Dropbox/Scripting/PyQt/ConsolePlayer/src/";

import os

def getVersionNumber(settings_path):
    """
        Returns the version number from a ConsolePlayer settings.ini file,
            or empty string if no file or version string is found
        path must be a full path to a settings file.
        no relative paths
    """
    version = "";
    if os.path.exists(settings_path):
        rf = open(settings_path,"r")
        
        line = True 

        while line:
            line = rf.readline().strip()

            i = line.index(":") # first index of a colon   
            key,value = ( line[:i], line[i+1:])

            if (key == "str_VERSION"):
                version = value;
                break;
                
        rf.close();
        
    return version;

my_version = getVersionNumber(PATH_TO_DEV_ROOT+"user/settings.ini");

a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), 
              os.path.join(HOMEPATH,'support\\useUnicode.py'), 
              PATH_TO_DEV_ROOT+'ConsolePlayer.py'],
              pathex=[PATH_TO_DEV_ROOT]
            )
             
pyz = PYZ(a.pure)

exe = EXE( pyz,
           a.scripts,
           a.binaries,
           a.zipfiles,
           a.datas,
           name=os.path.join('dist', 'ConsolePlayer-%s.exe'%(my_version)),
           debug=False,
           strip=False,
           upx=True,
           console=False, 
           icon= PATH_TO_DEV_ROOT+'icon.ico')
          
app = BUNDLE(exe,
             name=os.path.join('dist', 'ConsolePlayer-%s.exe.app'%(my_version)))
             
             

