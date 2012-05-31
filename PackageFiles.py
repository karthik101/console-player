from BytePack import *

# This program auto generates MpUnPack.py, by copying all files in

folder = "D:\\Dropbox\\Scripting\\PyQt\\console-player\\src"


pack = Pack(folder+"\\user");
pack.setClassName("MpUnPack")
pack.setOutputFolder(folder)
pack.addFile("./icon.png")
pack.addFolder("./style/default/")
pack.addFolder("./style/No Theme/")
pack.addFolder("./images/")
pack.addFolder("./plugins/")

for root,file in pack.files:
    print file
print "%d Files Packaged"%len(pack.files)    

pack.createPackage()

w = raw_input()