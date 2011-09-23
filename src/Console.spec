# -*- mode: python -*-
isPosix = os.name == 'posix'
EXT = ".exe"
ICOEXT = '.ico'

# this assumes you are running the supplied exec.sh or exec.bat from the top level directory
PATH_TO_DEV_ROOT = os.path.join(os.getcwd(),"src","")

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
    
a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), 
              os.path.join(HOMEPATH,'support/useUnicode.py'), 
              PATH_TO_DEV_ROOT+'ConsolePlayer.py'],
              pathex=[PATH_TO_DEV_ROOT]
            )
        
pyz = PYZ(a.pure)

FULL_NAME = 'ConsolePlayer-%s.%s%s'%(my_version,os.name,EXT)


exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('..','bin', FULL_NAME),
          debug=False,
          strip=False,
          upx=True,
          console=True , 
          icon= PATH_TO_DEV_ROOT+'icon'+ICOEXT)
