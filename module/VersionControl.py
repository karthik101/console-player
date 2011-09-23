#!/usr/bin/python -O
__VERSION__="0.0.0.0"# padding str#################
     
# USAGE
# import VersionControl
# version = VersionControl.getVersion()
# vo = VersionControl.VersionController("./MpVersion.py")
# vo.updateBuild();
     
def getVersion():
    return __VERSION__;

class VersionController(object):

    def __init__(self,filepath,version=None):
        self.fpath = filepath; # full path to a version.py file
        
        if type(version) != str:
            self.version = getVersion();
        else:
            self.version = version;

    def updateRelease(self):
        self.version = incrementValue(0,self.version)

    def updateMajor(self):
        self.version = incrementValue(1,self.version)

    def updateMinor(self):
        self.version = incrementValue(2,self.version)

    def updateBuild(self):

        self.version = incrementValue(3,self.version)
    
    def setBuild(self,value):

        R=self.version.split('.')
        build = int(R[3])
        R[3] = str(value)
        self.version =  '.'.join(R)
    
    def setVersion(self,version):
        self.version = version
        
    def update(self):
        # open the file for read and writing simutaneously
        vlen = len(self.version);
        mlen = 20; # 4 version numbers, at max 4 characters each + 3 seperating periods + 1
        plen = mlen-vlen; #length of padding
        padding = "                                             "[:plen]
        wrf = open(self.fpath,"r+")
        wrf.write("#!/usr/bin/python -O\n")
        wrf.write("__VERSION__ = \"%s\"%s\n"%(self.version,padding));
        wrf.close();
        
def incrementValue(index,version):
    R=version.split('.')
    build = int(R[index])
    R[index] = str(build+1)
    return '.'.join(R)
