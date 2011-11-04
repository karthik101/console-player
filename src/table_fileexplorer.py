import math 
import sys
import os  

import widgetTable
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MpGlobalDefines import *

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
                if len(self.cut_file) > 0:
                    contextMenu.addAction("paste %d File%s Here"%(len(self.cut_file),'s' if len(self.cut_file)>1 else ""),self.__Action_paste_file)
                elif self.cut_folder != "":
                    contextMenu.addAction("paste Folder",self.__Action_paste_folder)
                contextMenu.addAction("cut File%s"%('s' if len(self.selection) > 1 else ""),self.__Action_cut_file)
                
                contextMenu.addAction("New Folder",self.__Action_NewFolder)
            else:
                contextMenu.addAction("Open "+self.data[row][self.name],self.__Action_open_dir__)
                contextMenu.addSeparator()    
                contextMenu.addAction("Rename Folder",self.__Action_Rename_Folder)
                contextMenu.addAction("New Folder",self.__Action_NewFolder)
                if len(self.cut_file) > 0:
                    contextMenu.addAction("paste %d File%s Here"%(len(self.cut_file),'s' if len(self.cut_file)>1 else ""),self.__Action_paste_file)
                elif self.cut_folder != "":
                    contextMenu.addAction("paste Folder",self.__Action_paste_folder)
                if len(self.selection) == 1 :
                    contextMenu.addAction("cut Folder",self.__Action_cut_folder)
                    
                
                
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
                #TODO NOT REALLY SURE THIS APPIES ANYMORE:
                # i used to pend songs then load them later, but no longer
                if tempsong == None and len(MpGlobal.Player.external) > 0:
                    for ex_path in MpGlobal.Player.external:
                        if comparePath(ex_path,temppath) :
                            value = self.f_pending
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
        self.cut_folder = ""
        self.cut_file = []
        
        for i in self.selection:
            f = self.data[i][self.flag]
            if f != self.f_exists and f != self.f_invalid and f != self.f_pending and self.data[i][self.type] == self.t_mp3:
                self.data[i][self.flag] = self.f_pending
                MpGlobal.Player.external.append(self.data[i][self.path])
                
        external_Load_Start()
        Player_set_unsaved();
        
    def __Action_open_dir__(self):
        self.__load_Directory__(self.__act_dir1__)
    
    def __Action_explore_folder(self):
        """ open the folder contained in __act_dir2__
            act is special variable set when a context menu is opened
        """
        try:
            os.startfile(self.__act_dir2__)
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
    
    def __Action_Rename_File(self):
        """
            Rename a single file or a group of files.
        """
        self.cut_folder = ""
        self.cut_file = []
        
        R = list(self.selection)
        print len(R)
        fprompt = "";
        new_name = ""

        #determine the prompt for the new file name
        if len(R) == 0:  
            print "No Items Selected to rename"
            return
        else:
            fprompt = fileGetName(self.data[R[0]][self.name])
        
        prompt = 'Pattern Rename songs:\ne.g. $art => artist_name\nAll standard search terms apply except dates.'    
        dialog = dialogRename(fprompt,'Rename File',prompt)  
        
        #get the new file name
        if dialog.exec_():
                new_name = dialog.edit.displayText();
        else: 
            debug("User canceled rename request")
            return;    
        
        # enough for now, this should be expanded into renaming multiple songs
        # by using the already defined .art .ttl etc. ~ 
        # then appending incrementing numbers for any colliding songs.
        
        # a template song is used to check the pattern renaming, and then
        # askthe user if this is what they want.
        template_song = None
        for row in R: 
            s = self.data[row][self.song]
            if s != None:
                template_song = s;
                break;
            # if template_song != None and s != None and template_song != s:
            #     template_song = None;
            #     break;  
            continue;
            
        sample = OS_FileName_Correct( MpMusic.expandExifMacro(new_name,'$',template_song) )
        
        if sample != new_name: # show a second prompt if the user wants pattern replacement
            message = 'Songs to Modify: %d\n'%len(R)
            message += 'Rename Pattern:\n%s\n'%new_name
            message += 'Sample:\n%s\n'%sample
            message += 'Continue?:'
            msgBox = QMessageBox(MpGlobal.Window)
            msgBox.setWindowTitle('Confirm Rename')
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText(message)
            #    "Delete Song Confirmation", message,
             #   QMessageBox.NoButton, self)
            msgBox.addButton("Rename", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            
            if msgBox.exec_() != QMessageBox.AcceptRole:
                debug("Rename Request Canceled By User")
                return;
        #
        filepath = self.__act_dir2__ # root path is the same for all selected songs
        
        for row in R:

            song = self.data[row][self.song]
            
            if song == None:
                continue;
                
            if song == MpGlobal.Player.CurrentSong:
                debug("File is currently in use")
                continue;

            fileext  = fileGetExt(self.data[row][self.name])
            
            name = MpMusic.expandExifMacro(new_name,'$',song)
            
            name = OS_FileName_Correct(name).strip() # strip illegal characters with a sudo whitlist
            
            if name != '':
                path = os.path.join(filepath,name+'.'+fileext)
                
                debug(path)

                if path != "" and not os.path.exists(path):
                    self._rename_file_(row,song[MpMusic.PATH],path)
            
        return;
        Player_set_unsaved();
        
    def __Action_Rename_Folder(self):
        
        #print "Current Folder: %s"%self.currentPath
        #print "Target  Folder: %s"%self.__act_dir1__ 
        #print "Working Folder: %s"%self.__act_dir2__ 
        #print "Renaming: %s"%self.__act_dir2__
        
        self.cut_folder = ""
        self.cut_file = []
        
        R = [] # list of songs in the target folder, and all sub folders
        
        folder_path = self.__act_dir1__   # root path to change
        root_path = self.__act_dir2__
        #TODO UNIX PATH CORRECT on root_path
        if isPosix:
            root_path = UnixPathCorrect(root_path)
        
        if root_path == "" or not os.path.exists(root_path):
            debug("Error Path Does Not Exist on File System:\n%s\n"%root_path)
            return;
            
        dirlist = [self.__act_dir1__, ]
        
        # this loop will gather all songs in the current library
        # that exist in child folders of the selected folder from the explorer window
        flag_AccessError = False # can't rename a folder if a child song is in use
        while len(dirlist) > 0:
            path = dirlist.pop()
            dir = os.listdir(path)
            
            for fname in dir:
                temppath = os.path.join(path,fname)
                # append new folders to the pathlist
                # append files to the file list
                tempsong = None
                #TODO reset checkattrib
                if os.path.isdir(temppath) :#and dirCheckAttribNormal(temppath):
                    dirlist.append( temppath )
                elif pathMatchExt(fname): # file is a playable song file

                    for song in MpGlobal.Player.library:
                        if comparePath(song[MpMusic.PATH],temppath) :
                            #print song
                            R.append(song)
                            if song == MpGlobal.Player.CurrentSong:
                                flag_AccessError = True;
                            break;
                    MpGlobal.Application.processEvents();
                    
            debug("%d Folders remaining"%len(dirlist))
        print " %d Songs will be affected"%len(R) 
        
        
        
        if flag_AccessError:
            debug("File is currently in use")
            return;
        
        # get the new folder name, and whether the user will commit to this 
        
        dialog = dialogRename(self.data[self.__act_row__][1],"Rename Folder")
        
        if dialog.exec_():
            print "accepted"
        else: 
            flag_AccessError = True
        
        new_name = dialog.edit.displayText();
        
        print flag_AccessError, new_name
        
        if flag_AccessError:
            debug("User canceled rename request")
            return;

        new_path = os.path.join(root_path,new_name)
        
        print "New Name: %s"%new_path
        
        try:
        
            os.rename(folder_path,new_path)
        
        except Exception as e:
            for i in e:
                debug("%s"%str(i))
                
        else:
            print "folder renamed..."
            self.data[self.__act_row__][1] = new_name;
            for song in R:
                song_path = song[MpMusic.PATH][len(folder_path):]
                # on unix/POSIX the player will do a PATHFIX then next time it is played
                song[MpMusic.PATH] = new_path+song_path
                print song[MpMusic.PATH]
        
        finally:
            self.FillTable()
        
        Player_set_unsaved();
        return;
    
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
            sub = ['%smusic\\' % d for d in drives if os.path.exists('%s/music/' % d)]
            sub += ['%splayer\\' % d for d in drives if os.path.exists('%s/player/' % d)]
            sub += ['%sdiscography\\' % d for d in drives if os.path.exists('%s/discography/' % d)]
            sub += ['%sjapanese\\' % d for d in drives if os.path.exists('%s/japanese/' % d)]
            sub += ['%smisc\\' % d for d in drives if os.path.exists('%s/misc/' % d)]
        
        
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
from MpSong import Song
from datatype_hex64 import *

from MpScripting import *
from MpSort import *
from MpSearch import *
from MpCommands import *

from MpApplication import *