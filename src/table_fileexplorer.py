import math 
import sys
import os  

import widgetTable
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *

isPosix = os.name == 'posix'

class TableFileExplorer(widgetTable.Table):
    """
        Main controller for a File System Explorer tab
    """
    # use data as the main store
    type = 0 # type of record
    name = 1 # name part of path
    path = 2 # path of record
    flag = 3 # True when already in library
    song = 4 # the matching song with any entry
    f_none=0
    f_exists = 1
    f_invalid = 2
    f_pending = 4 #TODO new value
    t_dir = 1
    t_mp3 = 2
    t_otr = 4
    __act_dir1__ = ""
    __act_dir2__ = ""
    __act_row__ = 0
    
    
    currentPath = "C:\\"
    textEditor = None
    icon_dir = None
    icon_mp3 = None
    brush_highlight1 = QBrush(QColor(200,200,0,48))
    brush_highlight2 = QBrush(QColor(200,0,0,48))
    brush_highlight3 = QBrush(QColor(0,0,200,48))
    
    #edit = None;
    contextMenu = None # for songs
    
    cut_file = []   # the list of [path,SONG=None] items that will be pasted somewhere new
    cut_folder = "" # the path to the folder that will be moved on paste
    
    def __init__(self,parent,textEdit):
    
        if isPosix:
            self.currentPath = '/'
        else:
            self.currentPath = 'C:\\'
        
    
        header = ("   ","Path")
        super(TableFileExplorer,self).__init__(parent,header)
        self.textEditor = textEdit
        self.__load_Directory__(self.currentPath)

        self.rowSpacing = 4
        self.table.horizontalHeader().hide()
        #myHeader = self.table.horizontalHeader()
        #myHeader.setClickable(False)
        #myHeader.setDefaultAlignment(Qt.AlignLeft)
        #myHeader.setResizeMode(1,QHeaderView.Stretch)
        self.table.resizeColumnToContents(0)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.manageDriveList()
        self.textEditor.activated.connect(self.__index_Change__)
         
    def FillTable(self,offset=-1):    
        """fill the table with data, starting at index offset, from the Display Array"""
        R = []
        k=0;
        if offset < 0 :
            offset = self.scrollbar.value()

        size = len(self.data) # in case size is zero, prevent any drawing to it
        for i in range(self.rowCount):
            k = i+offset; # the k'th element of the data array
            
            if k < len(self.data) and size > 0:
                R = self.FillRow(k)
                brush = self.FillRowColor(k)
                self.model.setData(self.model.index(i,0),R[0],Qt.DecorationRole)
                self.model.setData(self.model.index(i,1),R[1])
                
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),brush,Qt.BackgroundRole)
            else:
                self.model.setData(self.model.index(i,0),None,Qt.DecorationRole)
                self.model.setData(self.model.index(i,1),"")
                for j in range(self.colCount):
                    self.model.setData(self.model.index(i,j),self.brush_default,Qt.BackgroundRole)
            
    def FillRow(self,index):
        if self.data[index][self.type] == self.t_dir:
            return [MpGlobal.icon_Folder,self.data[index][self.name]]
        else:
            return [MpGlobal.icon_None,self.data[index][self.name]]
    
    def FillRowColor(self,index):
        if index in self.selection:
            if self.table.hasFocus() :
                return self.brush_selected
            else:
                return self.brush_selectedOOF
        elif self.data[index][self.flag] == self.f_pending:
            return self.brush_highlight3
        elif self.data[index][self.flag] == self.f_invalid :
            return self.brush_highlight2
        elif self.data[index][self.flag] == self.f_exists :
            return self.brush_highlight1
        return self.brush_default
    
    def rightClickEvent(self,event):
    
    
        self.FillTable()
        
        item = self.table.indexAt(event.pos())
        row = item.row() + self.getDisplayOffset()
            
        if len(self.selection) > 0 and row < len(self.data):

        # modify the context menu based on click context
            t = self.data[row][self.type]
            contextMenu = QMenu(self.table)
            
            #contextMenu.addSeparator()
            self.__act_dir1__ = self.data[row][self.path]
            self.__act_dir2__ = self.currentPath
            self.__act_row__  = row;
            
            if t == self.t_mp3:
                contextMenu.addAction("Play Song",self.__Action_play_song__)
                contextMenu.addAction("Add to Library",self.__Action_load_song__)
                contextMenu.addSeparator()    
                contextMenu.addAction("Rename File",self.__Action_Rename_File)
                contextMenu.addAction("New Folder",self.__Action_NewFolder)
                
            else:
                contextMenu.addAction("Open "+self.data[row][self.name],self.__Action_open_dir__)
                contextMenu.addSeparator()    
                contextMenu.addAction("Rename Folder",self.__Action_Rename_Folder)
                contextMenu.addAction("New Folder",self.__Action_NewFolder)
                
            contextMenu.addSeparator() 
            if len(self.cut_file) > 0:
                contextMenu.addAction("paste %d Item%s"%(len(self.cut_file),'s' if len(self.cut_file)>1 else ""),self.__Action_paste_file)
            elif self.cut_folder != "":
                contextMenu.addAction("paste Item",self.__Action_paste_folder)
                
            if len(self.selection) > 1:
                contextMenu.addAction("cut Items (%d)"%len(self.selection),self.__Action_cut_file)
            else:
                contextMenu.addAction("cut Item",self.__Action_cut_folder)
                     
                
                
            contextMenu.addSeparator()
            contextMenu.addAction("Open Directory",self.__Action_explore_folder) #+dirGetParentDirName(self.currentPath)
            
            #contextMenu.addAction("Explore "+self.parentFolderName)
            #self.__Show_Context_Menu__(event.globalPos(),row)
            # iconText returns the text used in constructing the menu
            
            action = contextMenu.exec_( event.globalPos() )
                #if action != None:
                #    text = action.iconText()
                #    print text
                #self.FillTable()  
            #self.table.removeChild(contextMenu)
            del contextMenu
            
    def DoubleClick(self,item):
        offset = self.getDisplayOffset()
        index = offset+item.row()
        if index < len(self.data):
            path = self.data[index][self.path]
            
            if os.path.isdir(path):
                #self.parentFolderName = self.data[index][self.name]
                self.__load_Directory__(path)
                
            elif pathMatchExt(path):
                self.__Action_play_song__(path)
        
    def resizeEvent(self,event):
        self.resize_Column()
        
    def resize_Column(self):
        w1 = self.table.columnWidth(0)
        w2 = self.table.width()
        self.table.setColumnWidth(1,w2-w1-1)   
        
    def __sortData__(self,reverse=False):
        g = lambda x: x[self.name]
        h = lambda x: x[self.type]
        
        self.data.sort(key = g, reverse=reverse )
        self.data.sort(key = h, reverse=reverse )
        
    def __load_Directory__(self,path):

        path = unicode(path)
        self.data = []
        
        self.currentPath = path
        
        self.selection= set()
        
        try :
            R = os.listdir(path)
            # with the files found in the directory set the data array to contain
            
            self.__manage_FileList__(R,path)
                
            if len(self.data) == 0 :
                self.data = [ [self.t_otr,"No Files","",False] ,]
                
            self.textEditor.setEditText(self.currentPath)

            #self.textEditor.setCurrentIndex(0)
            # update the table with the new data, and move the offest to zero    
            self.UpdateTable(0)
            
            self.manageDriveList()
        except:
            pass
        
    def __manage_FileList__(self,R,path):
        """ R, as list of fname in path
            small list is roughly 200 items or less
            a large list needs special work
        """
        for fname in R:
            temppath = os.path.join(path,fname)
            # append new folders to the pathlist
            # append files to the file list
            tempsong = None
            #TODO reset checkattrib
            if os.path.isdir(temppath) :#and dirCheckAttribNormal(temppath):
                self.data.append( [self.t_dir,"%s"%fname,temppath,False,None] ) 
            elif pathMatchExt(fname):
                value = self.f_none
                # we know that the path is a song, check if it is in the library
                
                for song in MpGlobal.Player.library:
                    if comparePath(song[MpMusic.PATH],temppath) :
                        value = self.f_exists
                        tempsong = song
                        break;
                    
                #if not pathIsUnicodeFree(temppath):
                #    value = self.f_invalid 
                
                self.data.append( [self.t_mp3,fname,temppath,value,tempsong] ) 
        
            MpGlobal.Application.processEvents()
        self.__sortData__();
             
    def __Goto_ParentDir__(self):
        dir = fileGetParentDir(self.currentPath)
        
        if dir != "":
            self.__load_Directory__(dir)
    
    def __Goto_NewDir__(self):
        path = self.textEditor.currentText();
        if os.path.isdir(path):
            self.__load_Directory__(path)
            
    def __index_Change__(self,index):
        path = self.textEditor.itemText(index);
        if os.path.isdir(path):
            self.__load_Directory__(path)
            
    def __Action_play_song__(self,path=None):
        if path == None and len(self.selection) > 0:
            path = self.getSelection()[0][self.path]
            
        if path != None:# and pathIsUnicodeFree(path):
            MpGlobal.Player.playState = MpMusic.PL_NO_PLAYLIST
            temp = id3_createSongFromPath(path)
            if MpGlobal.Player.load(temp) :
                MpGlobal.Player.play()
                
    def __Action_load_song__(self):
        """ add the selected songs to the list of songs to load"""
        pass
        
    def __Action_open_dir__(self):
        self.__load_Directory__(self.__act_dir1__)
    
    def __Action_explore_folder(self):
        """ open the folder contained in __act_dir2__
            act is special variable set when a context menu is opened
        """
        try:
            explorerOpen(self.__act_dir2__)
        except:
            pass

    def __Action_NewFolder(self):
        """
            create a new folder with the given name
        """
        dialog = dialogRename("New Folder","Create Folder")
        
        if not dialog.exec_():
            print "Folder Creation Reject"
            return;

        name = dialog.edit.displayText();
        
        name = OS_FileName_Correct(name).strip() 

        path = os.path.join(self.currentPath,name);
        
        if not os.path.exists(path):
            self.data.insert(0, [self.t_dir,name, path ,False,None] ) 
            os.mkdir(path);
            self.FillTable();
    
    def __Action_cut_file(self):
        self.cut_folder = ""
        self.cut_file = []

        R = list(self.selection)
        for row in R: 
            p = self.data[row][self.path]
            s = self.data[row][self.song]
            self.cut_file.append([p,s])
        
    def __Action_paste_file(self):
        """
            take the selected files that were 'cut'
            and paste them to the target folder
        """
    
        dst = self.__act_dir2__
        
        for file,song in self.cut_file:
            self._paste_one_file(file,dst,song);
            
        self.cut_folder = ""
        self.cut_file = []
        #self.FillTable();
        self.__load_Directory__(self.currentPath);
        Player_set_unsaved();

    def _paste_one_file(self,src,dst_folder,song=None):
    
        src_name = fileGetFileName(src)
        src_dir  = fileGetPath(src)
        
        if not comparePath(src_dir,dst_folder):
        
            dst = os.path.join(dst_folder,src_name);
            
            try:
                os.rename(src,dst);
                print dst
                if song!=None:
                    song[MpMusic.PATH] = dst
            except:
                print "could not move file"
            else:
                self.data.insert(0, [self.t_mp3,src_name, dst,song!=None,song] ) 
    
    def __Action_cut_folder(self):
        """
            cutting a folder is as easy as saving the current selected folder
        """
        R = list(self.selection)
        
        self.cut_folder = ""
        self.cut_file = []
        
        if len(R) == 1:
            self.cut_folder = self.data[R[0]][self.path]
            
        print self.cut_folder
        
    def __Action_paste_folder(self):
            
        tar_dir  = self.__act_dir2__
        cut_name = fileGetFileName(self.cut_folder)
        cut_dir  = fileGetPath(self.cut_folder)
               
        if not comparePath(tar_dir,cut_dir) and \
            not comparePathLength(self.cut_folder,tar_dir) : # paths are not identicle , and src folder is not parent of child folder
            
            new_dir = os.path.join(tar_dir,cut_name);
            
            print new_dir
            
            try:
                os.rename(self.cut_folder,new_dir)
            except:
                print "could not move folder"
            else:
                self.data.insert(0, [self.t_dir,cut_name, new_dir,False,None] ) 
                self.FillTable();
        else:
            print "paste error"
        # clear the cut variables
        self.cut_folder = ""
        self.cut_file = []
        Player_set_unsaved();
    
    def _rename_file_(self,row,filepath,newpath):
        try:
            #debug(file)
            #debug(path)
            os.rename(filepath,newpath)
        
        except Exception as e:
            for i in e:
                debug("%s"%str(i))  
        else:
            song = self.data[row][self.song]
            if song != None:
                song[MpMusic.PATH] = newpath
            self.data[row][1] = fileGetFileName(newpath);
        finally:
            self.FillTable()
      
    def manageDriveList(self):
        drives = systemDriveList()
        #sub1 = ['%s/music/' % d for d in drives if os.path.exists('%s/music/' % d)]
        #sub2 = ['%s/player/' % d for d in drives if os.path.exists('%s/player/' % d)]
        if self.textEditor != None:
            # add some custom paths to the default list of drives
            # most of these are convenient for me, no one else has my file system
            sub =  [os.path.join(d,'music'      ,'') for d in drives if os.path.exists(os.path.join(d,'music'      ,''))]
            sub += [os.path.join(d,'Player'     ,'') for d in drives if os.path.exists(os.path.join(d,'Player'     ,''))]
            sub += [os.path.join(d,'Discography','') for d in drives if os.path.exists(os.path.join(d,'Discography',''))]
            sub += [os.path.join(d,'Japanese'   ,'') for d in drives if os.path.exists(os.path.join(d,'Japanese'   ,''))]
            sub += [os.path.join(d,'Misc'       ,'') for d in drives if os.path.exists(os.path.join(d,'Misc'       ,''))]
        
        
            R = drives+sub
            R.sort()
            self.textEditor.clear()
            
            index = 0;
            if self.currentPath in R:
                index = R.index(self.currentPath)
            else:
                R = [self.currentPath,]+R
                
            for item in R:
                self.textEditor.addItem(item)

            self.textEditor.setCurrentIndex(index)
    
    
class dialogRename(QDialog):
    def __init__(self,text='',title='Rename', prompt='', parent=None):
    
        super(dialogRename,self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 50)
        
        hbox = QHBoxLayout();
        vbox = QVBoxLayout(self);
        self.edit = LineEdit()

        self.btna = QPushButton("Accept")
        self.btnc = QPushButton("Cancel")
        
        hbox.addWidget(self.btnc)
        hbox.addWidget(self.btna)
        
        vbox.addWidget(self.edit)
        
        
        if len(prompt) > 0:
            vbox.addWidget(QLabel(prompt))
            
        vbox.addLayout(hbox)
        
        self.btna.clicked.connect(self.accept)
        self.btnc.clicked.connect(self.reject)
        self.edit.returnPressed.connect(self.accept)
        
        self.edit.setText(text)
        
       
from MpGlobalDefines import *
from Song_Object import Song
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from Song_Search import *
from MpCommands import *
from MpPlayerThread import *
from MpEventMethods import * 
from MpApplication import *