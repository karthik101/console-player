#!/usr/bin/python -O
__VERSION__ = "0.4.1.163"           





# ################################################
# do not edit anything above this line unless you 
# know what you are doing
import os

# example use:
# import VersionController
# APPLICATION.VERSION = VersionController.AutoVersion(True) 
# APPLICATION.VERSION = VersionController.ResetBuildNumber(True) 
# del VersionController
# print MpGlobal.NAME
file="./VersionController.py"

def AutoVersion(update):

    import VersionControl
    
    ver = __VERSION__
    
    if update:
        if os.path.exists(file):
        
            #version = VersionControl.getVersion()
            vo = VersionControl.VersionController(file,__VERSION__)
            
            vo.updateBuild();
            
            vo.update();
            ver = vo.version
        else:
            print "version file not found - AV"

    del VersionControl
    
    return ver
    
def ResetBuildNumber():

    import VersionControl
    
    ver = __VERSION__
    
    if os.path.exists(file):
    
        #version = VersionControl.getVersion()
        vo = VersionControl.VersionController(file,__VERSION__)
        
        vo.setBuild(1);
        
        vo.update();

        ver = vo.version
    else:
        print "version file not found - RB"

    del VersionControl

    return ver
    
if __name__ == "__main__":
    print AutoVersionUpdate()
