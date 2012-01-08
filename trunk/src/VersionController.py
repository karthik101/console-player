#!/usr/bin/python -O
__VERSION__ = "0.5.2.134"           
##########################################
# do not edit anything above this line unless you 
# know what you are doing
import os

# example use:
# import VersionController
# APPLICATION.VERSION = VersionController.AutoVersion(True) 
# del VersionController
# print MpGlobal.NAME

def AutoVersion(update):

    import VersionControl
    
    ver = __VERSION__
    
    if update:
        if os.path.exists("./VersionController.py"):
        
            #version = VersionControl.getVersion()
            vo = VersionControl.VersionController("./VersionController.py",__VERSION__)
            
            vo.updateBuild();
            
            vo.update();
            ver = vo.version
        else:
            print "version file not found - AV"

    del VersionControl
    
    return ver

