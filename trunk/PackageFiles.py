from BytePack import *

folder = "D:\\Dropbox\\Scripting\\PyQt\\console-player\\src"


pack = Pack(folder+"\\user");
pack.setClassName("MpUnPack")
pack.setOutputFolder(folder)
pack.addFile("./icon.png")
pack.addFolder("./style/default/")
pack.addFolder("./style/No Theme/")
pack.addFolder("./images/")

for root,file in pack.files:
    print file
print "%d Files Packaged"%len(pack.files)    

pack.createPackage()

w = raw_input()