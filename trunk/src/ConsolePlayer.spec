# -*- mode: python -*-

"""
    ConsolePlayer.spec
        spec File for building ConsolePlayer with PyInstaller
    ----------------------------------------------------------

    Update PATH_TO_DEV_ROOT to the folder where you have
        placed the Console Player source.
    
    all other paths will automatically be updated from that value
    
"""

import os
isPosix = os.name == 'posix'

#fpath = os.path.abspath(__file__).replace('\\','/')
#PATH_TO_DEV_ROOT = fpath[:fpath.rfind('/')+1] # file path of the current file, and the project

# this assumes you are running the supplied exec.sh or exec.bat from the top level directory
if isPosix:
    PATH_TO_DEV_ROOT = '/home/nick/windows/D_DRIVE/Dropbox/Scripting/PyQt/console-player/src/'
else:
    PATH_TO_DEV_ROOT = os.path.join(os.getcwd(),"src","")

print "\n\n%s\n\n"%PATH_TO_DEV_ROOT
print os.getcwd();

EXT = ".exe"
ICOEXT = '.ico'

if isPosix:
    EXT = '';
    ICOEXT='.png'



def getVersionNumber(settings_path):
    """
        Returns the version number from a ConsolePlayer settings.ini file,
            or empty string if no file or version string is found
        path must be a full path to a settings file.
        no relative paths
    """
    version = "0.0.0.0";
    
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

# the "version.os.ext" format is a slight hack, on windows any posix files
# will show up as POSIX files, which makes sorting by file type in windows explorer easier to
# find the windows executable vs the linux executable
FULL_NAME = 'ConsolePlayer-%s.%s%s'%(my_version,os.name,EXT)


a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), 
              os.path.join(HOMEPATH,'support/useUnicode.py'), 
              PATH_TO_DEV_ROOT+'ConsolePlayer.py'],
              pathex=[PATH_TO_DEV_ROOT]
            )
             
pyz = PYZ(a.pure)

exe = EXE( pyz,
           a.scripts,
           a.binaries,
           a.zipfiles,
           a.datas,
           name=os.path.join('..','bin', FULL_NAME),
           debug=False,
           strip=False,
           upx=True,
           console=False, 
           icon= PATH_TO_DEV_ROOT+'icon'+ICOEXT)
          
app = BUNDLE(exe, name=os.path.join('dist', FULL_NAME) )
             
             

