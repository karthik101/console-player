# -*- mode: python -*-




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





FULL_NAME = 'ConsolePlayer%s'%(EXT)




a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), 
              os.path.join(HOMEPATH,'support\\useUnicode.py'), 
              PATH_TO_DEV_ROOT+'ConsolePlayer.py'],
              pathex=[PATH_TO_DEV_ROOT])
             
pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('..','bin', FULL_NAME),
          debug=False,
          strip=False,
          upx=True,
          console=False )
          
coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'ConsolePlayer'))
