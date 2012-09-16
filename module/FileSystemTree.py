#! python "$this"

import os,sys
from  Leaf import Leaf
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class FSObject( object ):
    type = 0;
    mode = 0;

    def __init__(self,filepath):
        self.filepath=filepath
        self.size = 0;
        if os.path.exists(filepath):
            self.mode = os.stat(filepath).st_mode

    def __getitem__(self,item):
  
        if item == 'path':
            return self.filepath
        elif item == 'name':    
            return os.path.split(self.filepath)[1]
        elif item == 'ext':    
            return os.path.splitext(self.filepath)[1][1:]
        elif item == 'parent': # return the directory for which this file is contained within.
            return os.path.split(self.filepath)[0]    
        elif item == 'size':    
            return self.size
        elif item == 'mode': 
            return self.mode
        return "fail:"+str(item)
        #raise AttributeError(" cannot find %s"%item)
    
    def __contains__(self,item):
        return item in ('path','name','ext','parent','size','mode')
    
    def isDir(self):
        return type(self) == FSDir
    def isFile(self):
        return type(self) == FSFile
    
class FSFile( FSObject ):
    type = 0x100;
    pass
    
class FSDir( FSObject ):
    processed = False;
    type = 0x10;
    pass

def _size_of(path):
    """ return size in bytes or 0 """
    try:
        size = os.path.getsize(path)
        return size
    except:
        pass
    return 64;
  
def _new_leaf(parent,object,name='name',icon=None):
    return Leaf(parent,object[name],object,icon)
  
def _process_directory(dleaf):  
    my_path = dleaf.data['path']
    try:
        flist = os.listdir(my_path)
    except:
        flist = []
        
    for file in flist:
        fullpath = os.path.join(my_path,file)
        try :
            realpath = os.path.realpath(fullpath) # resolve symlinks on linux, does not really change anything on windows
            if os.path.isdir(realpath):
                l = _new_leaf(dleaf,FSDir(fullpath),'name',QStyle.SP_DirIcon)
            else:
                leaf = _new_leaf(dleaf,FSFile(fullpath),'name',QStyle.SP_FileIcon)
                leaf.data.size = _size_of(fullpath)
        except:
            print " *** ERROR : %s"%fullpath
    if len(dleaf.children) == 0:
        dleaf.setEmptyFolder()
    dleaf.data.processed = True
    
def loadRoot( dleaf , recourse=False):

    size = 0;
    
    if dleaf.data.processed == False:
        _process_directory(dleaf) # if no data has been loaded from the directory, load the information now.

    # now that data is loaded, sum the size of each item in the directory
    # and set as the size for this folder
    
    for child in dleaf.children:
        if type(child.data) == FSDir:
            if recourse:
                size += loadRoot(child)
        else:
            size += child.data.size
            
    dleaf.data.size = size
    
    return size
   
def getRoot( path ):
    root = _new_leaf(None,FSDir(path),name='path')
    if os.name == 'nt':
        root.join_string = '\\'
    else:
        root.join_string = '/'
    # we want to sort directories first
    root.sort_key = lambda o : "%s%s"%(o.data.type,o.data['name'])
    return root
    
if __name__ == '__main__':           
    
    tf = FSFile("void")
    print True==tf.isFile()
    print False==tf.isDir()
    td = FSDir("void")
    print False==td.isFile()
    print True==td.isDir()
    
    start_dir = "C:\sample"
 
    
    #root = getRoot( start_dir )

    #loadRoot( root ) # recursivley move through all directories and get file size.
    
    #print root.toList()
 
    #import os,sys
    #from PyQt4.QtCore import *
    #from PyQt4.QtGui import *
    #from widgetLargeTree import *
    #from widgetLargeTable import *
    #app = QApplication(sys.argv)

    
    #table = LargeTree()
    #table.columns.append(TableColumn(table,'size','size'))
    #table.container.resize(320,240)
    #table.container.show()
    #table.set(root.toList())
    
    #sys.exit(app.exec_())    
    