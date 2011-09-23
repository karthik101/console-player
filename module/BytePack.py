#!/usr/bin/python -O
import os
import sys
import struct
# BytePack.py

TAB = "    ";    # define the size of a single tab for  
TA2 = TAB + TAB  # writing the generated class file
TA3 = TA2 + TAB
TA4 = TA3 + TAB
TA5 = TA4 + TAB
TA6 = TA5 + TAB

def bytes_from_file(filename, chunksize=8192):
    """
        Generator yeilds each byte from the given file
        file is closed automatically when the loop breaks
    """
    with open(filename, "rb") as rf:
        while True:
            chunk = rf.read(chunksize)
            if chunk:
                for b in chunk:
                    #yield "\\x%02X"%struct.unpack("B",b)
                    yield "\\x%02X"%ord(b)
            else:
                break
        rf.close()

def pathExpandRelative(root,path):
    """
        Expand relative paths into path root and file name
        eg
            root = "C:\\folder1\\folder2\\"
            file = "./../folder3\\file.txt"
        becomes
            root = "C:\\folder1\\"
            file = "folder3\\file.txt"
        fullpath = C:\\folder1\\folder3\\file.txt
    """
    getFolderParent = lambda s : s[:s.replace('\\','/')[:-1].rfind('/')+1]  #assuming folder is slash-terminated  
    
    if path[:2] == ('./'):

        path = path[2:]      
        # then process any indicators to go up one sub level
        while path[:2] == ('../'):
            path = path[3:]
            root = getFolderParent(root)  
    else:
        root = ""
        
    return (root,path)
    
class Pack(object):
    # max character length for doc-string
    #   [ 1 ][ 2 ][ 3 ][ 4 ][ 5 ][ 6 ][ 7 ][ 8 ][ 9 ][ 0 ][ 1 ][ 2 ][ 3 ][ 4 ][]
    """ 
        Class: Pack
        add files and folders to this object, then call createPackage()
        all files, and files found in the folders will have binary copies
        written to a single python file. this python file will allow easy export
        of the files
        
        TODO:
            if a file is added using a relative path e.g. ./../File.txt
            it should unpack to one sublevel down from the final install path 
            in UnPack
            This Needs whitelist/blacklist mode on file extenstions when adding 
                by folder as well as whitelist/blacklist on 
                    file name/folder name
            Add Run Length Encoding
                for example, many files contain tons of zero padding
                for strings of \\x00 replace with COUNT*00
                we get \\xA019*00\\x37 
                the format is 4 characters per byte so no start/stop characters
                are required to indicate the beginning/ending of the encoding
                just search for an asterisk, go back until you get a slash
                then move foward 4 characters, then everything up 
                to 2 characters  after the asterisk is replaced with
                "\\xXX"*COUNT
    """
    
        
    def __init__(self,root=""):
        self.FILE = None;       # FILE I/O Object
        self.files = []         # list of files to pack
        self.folders = []       # list of folder to find files in
        self.classList = []     # list of outpout class names
        self.fileList = []      # list of files in output name format
        self.outputFolder = "./"
        self.outputFile = "./UnPack.py"
        self.setRootFolder(root)
        self.setClassName("UnPack")
        self.mainFunctionName = "UnPackFiles";
            
    def addFile(self,fpath):
        
        
        fpath = fpath.replace("\\","/");
        
        # first replace any relative indicators
        root,fpath = pathExpandRelative(self.root,fpath)

        exists = False
        for (r,f) in self.files:
            if r==root and f==fpath:
                exists = True

        if not exists:
            self.files.append([root,fpath])
    
    def addFolder(self,fpath,subFolders=True):
        if fpath[-1] not in "\\/":
            fpath = os.path.join(fpath,"") # include final backslash
        
        root,fpath = pathExpandRelative(self.root,fpath)
        
        folders = [root+fpath,];

        while len(folders) > 0:
            fpath = folders.pop(0);
            R = os.listdir(fpath)
            for item in R:
                path = fpath+item
                if os.path.isdir(path) and subFolders:
                    folders.append(os.path.join(path,""))
                else:
                    path = path.replace(root,"./")
                    self.addFile(path)
    
    def setRootFolder(self,root=""):
        if root=="":
            self.root = os.getcwd().replace("\\","/");
        else:
            self.root = root;
            
        if self.root[-1] not in "\\/":
            self.root = os.path.join(self.root,"") # include final backslash
            
    def setOutputFolder(self,folder):
        if folder[-1] not in "\\/":
            folder = os.path.join(folder,"") # include final backslash
        self.outputFolder = folder 
        self.__setOutputFileName()
        
    def setClassName(self,name):
        self.className = name
        self.outputClass = "%s.py"%self.className
        self.__setOutputFileName()
        
    def __setOutputFileName(self):
        self.outputFile = os.path.join(self.outputFolder,self.outputClass)
    
    def setMainFunctionName(self,name):
        self.mainFunctionName = name;
        
    def createPackage(self):
        """
            with all files added from addFile and addFolder
            read binary data and write a new class object derived from UnPack
        """
        self.open();
        for path,item in self.files:
            self.writeNewFileObject(path,item)
        self.close();
            
    def file_to_class_name(self,fname):
        fname = fname.upper();
        fname = fname.replace(".","_")
        fname = fname.replace("\\","/")
        fname = fname.replace(self.root.upper(),"")
        fname = fname.replace("/","_")
        fname = fname.replace(" ","_")
        fname = fname.strip("_")
        return fname
        
    def open(self):  

        self.FILE = open(self.outputFile,"w")
        self.FILE.write( '"""\n' )
        self.FILE.write( TAB+"Warning this file is Auto Generated...\n" )
        self.FILE.write( TAB+"To use:\n")
        self.FILE.write( TA2+"from %s import %s\n"%(self.className,self.mainFunctionName) );
        self.FILE.write( '"""\n' )
        self.FILE.write( 'import os\n' )
        self.FILE.write( 'import sys\n\n' )
        
        self.writeDefaultObject();
        
    def close(self):
    
        write = self.FILE.write
        #-----------------------------------------------------
        # Write a List of Classes
        write("_classList_ = ( ")
        for i in range(len(self.classList)):
           write( "%s, "%self.classList[i] )
           if (i>0 and i%4==0):
                write( "\\\n" )
                write("              ")
        write("\n            )\n\n")
        
        #-----------------------------------------------------
        # Write a List of files
        write("_fileList_ = ( ")
        for i in range(len(self.files)):
           write( "\"%s\", "%self.files[i][1] )
           if (i>0 and i%4==0):
                write( "\\\n" )
                write("              ")
        write("\n            )\n\n")
        #-----------------------------------------------------
        # Write the Class Generator Function
        write("def %s():\n"%self.mainFunctionName)
        write(TAB+"for item in _classList_:\n")
        write(TA2+"yield item\n\n");
        #-----------------------------------------------------
        # files
        write("def files():\n")
        write(TAB+"return _fileList_\n\n")
        #-----------------------------------------------------
        # count
        write("def count():\n")
        write(TAB+"return len(_classList_) # Count = %d\n\n"%len(self.classList))
        #-----------------------------------------------------
        write("if __name__ == \"__main__\":\n")
        write(TAB+"for obj in %s():\n"%self.mainFunctionName)
        write(TA2+"obj(root=\"./\").verify()\n");
        write("\n\n");   
        self.FILE.close();
              
    def writeDefaultObject(self):
        """
            Writes a copy of the UnPack class to the target file
            all files packed are saved as classes derived from UnPack
        """
        # class UnPack
        self.FILE.write("class UnPack(object):\n")
        #init
        self.FILE.write(TAB+"def __init__(self,root=\"./\"):\n")
        self.FILE.write(TA2+"self.fpath = root+self.fname;\n")
        self.FILE.write(TA2+"self.root = root;\n\n")
        #save
        self.FILE.write(TAB+"def save(self):\n")
        self.FILE.write(TA2+"self.checkPath();\n")
        self.FILE.write(TA2+"FILE = open(self.fpath,\"wb\")\n")
        self.FILE.write(TA2+"for byte in self.data:\n")
        self.FILE.write(TA3+"FILE.write(\"%c\"%byte)\n")
        self.FILE.write(TA2+"FILE.close()\n")
        #verify
        self.FILE.write("\n"+TAB+"def verify(self):")
        self.FILE.write("\n"+TA2+"byteF = 0; byteS = 0;")
        self.FILE.write("\n"+TA2+"index = 0; error = 0;")
        self.FILE.write("\n"+TA2+"if os.path.exists(self.fpath):")
        self.FILE.write("\n"+TA3+"FILE = open(self.fpath, \"rb\");")
        self.FILE.write("\n"+TA3+"chunk = FILE.read(1024)")
        self.FILE.write("\n"+TA3+"while chunk:")
        self.FILE.write("\n"+TA4+"for byteF in chunk:")
        self.FILE.write("\n"+TA5+"byteF = \"\\\\x%02X\"%ord(byteF)")
        self.FILE.write("\n"+TA5+"byteS = \"\\\\x%02X\"%ord(self.data[index]);")
        self.FILE.write("\n"+TA5+"index += 1;")
        self.FILE.write("\n"+TA5+"if byteF!=byteS:")
        self.FILE.write("\n"+TA6+"error |= 2")
        self.FILE.write("\n"+TA6+"break;")
        self.FILE.write("\n"+TA4+"chunk = FILE.read(1024)")
        self.FILE.write("\n"+TA3+"if index != self.size:")
        self.FILE.write("\n"+TA4+"error |= 4;")
        self.FILE.write("\n"+TA3+"FILE.close()")
        self.FILE.write("\n"+TA2+"else:")
        self.FILE.write("\n"+TA3+"error |= 1")
        self.FILE.write("\n"+TA2+"if error:")
        self.FILE.write("\n"+TA3+"# print \"Saving: %d %s:\"%(error,self.fpath)")
        self.FILE.write("\n"+TA3+"self.save();\n\n")
        #checkPath
        self.FILE.write(TAB+"def checkPath(self):\n")
        self.FILE.write(TA2+"R = self.fname.replace(\"\\\\\",\"/\").split('/')\n")
        self.FILE.write(TA2+"fname = R.pop()\n")
        self.FILE.write(TA2+"path = self.root\n")
        self.FILE.write(TA2+"if len(path) > 0:\n")
        self.FILE.write(TA3+"if path[-1] == \"\\\\\" or path[-1] == '/': path = path[:-1];\n")
        self.FILE.write(TA2+"while len(R) > 0:\n")
        self.FILE.write(TA3+"path = os.path.join(path,R.pop(0),"")\n")
        self.FILE.write(TA3+"if not os.path.exists(path):\n")
        self.FILE.write(TA4+"os.mkdir(path)\n\n")
        self.FILE.write("\n\n");
    def writeNewFileObject(self,path,fname):
        count = 0;
        
        file = fname;
            
        self.className = self.file_to_class_name(file)
        
        self.classList.append(self.className)
        self.fileList.append(file)
        
        self.FILE.write("class %s( UnPack ):\n"%self.className)
        
        
        self.FILE.write(TAB+"fname = \"%s\"\n"%file)
        self.FILE.write(TAB+"data = \"")
        # consider storing as %c, no spaces and as string no list
        #for Byte in bytes_from_file(fname):
        #    self.FILE.write("%2d,"%Byte)
        #    count += 1;
        #    if count > 0 and count % 512 == 0:
        #        self.FILE.write("\\\n"+TAB3)
        for Byte in bytes_from_file(path+fname):
            self.FILE.write(Byte)
            count += 1;
            if count > 0 and count % 512 == 0:
                self.FILE.write("\\\n")
        self.FILE.write("\"\n")
        self.FILE.write(TAB+ "size = %d\n"%count)
        self.FILE.write("\n")
        return count

if __name__ == "__main__":

    def main():
        print "Example Usage:"
        print ""
        print "pack = Pack()"
        print "pack.setOutputFolder(\"C:\\\")"
        print "pack.addFile(\"./test.txt\")"
        print "pack.addFolder(\"./MyFolder/\",False)"
        print "pack.createPackage()"
        #folder = "C:\\Dropbox\\Scripting\\PyQt\\ConsolePlayer\\src"
        #pack = Pack(folder+"\\user");
        #pack.setClassName("MpUnPack")
        #pack.setClassName("MpUnPack")
        #pack.setOutputFolder(folder)
        #pack.addFile("./icon.png")
        #pack.addFolder("./style/default/")
        #pack.addFolder("./style/No Theme/")
        #pack.addFolder("./images/")
        #pack.createPackage()
    main()
