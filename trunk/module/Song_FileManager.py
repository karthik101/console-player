import os
import sys

from Song_Object import *
from SystemPathMethods import *

class Song_File_Manager(object):
    """    
        Moving or handling of files is relativley easy, the OS provides
        a set of function for manipulating files, copy, move etc.
        
        Moving a song is much more difficult. The definition of a song requires
        knowing where it is located in order to play it.
        
        When renaming or moving a folder, all songs within that folder must be found
        and then updated
        
        This module provides a way to set files, folders and most importently Songs,
        so that they can be moved.
        
        cut and paste can be performed by set and then move
        
        Note: it may be best to call these functions from a separate thread.
        as move operations may take a long time.
    """
    file_list = []
    folder_list = []
    song_list = []
    library = []    # list of songs. used when moving a folder
    rename_dict = {}
    
    def setFile(self,file_list):
        """
            file_list as a single file  path
            or list-of-file paths
            
        """
        if isinstance(file_list,basestring):
            self.file_list.append(file_list)
        else:
            self.file_list += file_list
            
    def setFolder(self,dir_list):
        """
            dir_list as a single file  path
            or list-of-file paths
            
        """   
        if isinstance(dir_list,basestring):
            self.folder_list.append(dir_list)
        else:
            self.folder_list += dir_list
    
    def setSong(self,song_list):
        """
            song_list as a single song
            or list-of-songs
            
        """   
        if isinstance(song_list,Song):
            self.song_list.append(song_list)
        else:
            self.song_list += song_list
      
    def setLibrary(self,lib):
        """
            set the library of songs to pull from.
            when moving a folder this will be used to update there paths
        """
        self.library = lib
      
    def setRenameDict(self,d):
        self.rename_dict = d
      
    def countFile(self):
        return len(self.file_list)
    
    def countFolder(self):
        return len(self.folder_list)
      
    def countSong(self):
        return len(self.song_list)
      
    def count(self):
        """ count of all files,folders and songs"""
        return self.countFolder() + self.countFile() + self.countSong()
    
    def move(self,dst):
        """
            dst as directory folder to move all files/folders to
            
            set files or folders with setFolder or setFile
            
            conveniance function. calls:
                moveFile
                moveFolder
                moveSong
                
            when finished the list of files/folders/songs is cleared
        """
        print "move start"
        self.moveFile(dst)
        self.moveFolder(dst)
        self.moveSong(dst)
        self.clear()
        print "move end"
        
    def moveFile(self,dst):
        """
            move all files set with setFile to folder 'dst'
        """  
        for file in self.file_list:
            self.__moveSingleFile(file,dst)
            
    def moveFolder(self,dst):
        """
            move all folders set with setFolder to folder 'dst'
        """
        
        for folder in self.folder_list:
            self.__moveSingleFolder(folder,dst)
              
    def moveSong(self,dst):
        """
            move all Songs set with setSong to folder 'dst'
        """ 
        
        for song in self.song_list:
            self.__moveSingleSong(song,dst)

    def __moveSingleFile(self,src,dst):
        """ src as path to file.
            dst as path to folder
        """
        name = fileGetFileName(src)
        path = fileGetPath(src)
        
        if comparePath(path,dst):   # destination is same as source
            return ""
        if fileGetDrive(src) != fileGetDrive(dst): # cannot move over drives
            return ""
            
        new_path = os.path.join(dst,name)
        
        src_dir  = fileGetPath(src)
        
        #print "FROM: - %s"%src_dir
        #print "TO  : %d %s"%(comparePathLength(src_dir,dst), dst)
  
        #if not comparePathLength(src_dir,dst): # if dst does not start with src
        
        try:
            os.rename(src,new_path);
        except:
            return ""
        else:
            return new_path
                
        return ""
            
    def __moveSingleFolder(self,src,dst):
        """ src as path to folder.
            dst as path to folder
        """
        # get rid of the final slash in src folder
        src = src if src[-1] not in "\\/" else src[:-1]
        
        name = fileGetFileName(src)
        path = fileGetPath(src)
        
        #if comparePath(path,dst):   # destination is same as source
        #    return ""
        if fileGetDrive(src) != fileGetDrive(dst): # cannot move over drives
            return ""
            
        R = self.__getSongList(src)  # get all songs within src

        #if not comparePathLength(dst,path):
        new_path = os.path.join(dst,name)
        try:
            os.rename(src,new_path)
        except:
            return ""
        else:
            self.__updateSongList(R,path,dst)
                    
        return ""  
        
    def __moveSingleSong(self,song,dst):

        new_path = self.__moveSingleFile(song[EnumSong.PATH],dst)
        
        if new_path != "": # fails when empty string is returned
            song[EnumSong.PATH] = new_path 
       
    def renameFile(self,dst):
        
        if len(self.file_list) == 1:
            self.__renameSingleFile(self.file_list[0],dst)
            self.clear()
        else:
            raise Exception( "Cannot rename multiple files" )

    def renameFolder(self,dst):
     
        if len(self.folder_list) == 1:
            self.__renameSingleFolder(self.folder_list[0],dst)
            self.clear()
        else:
            raise Exception( "Cannot rename multiple folders" )
            
    def renameSong(self,dst):
        name = fileGetFileName(dst)
        if '$' not in name and len(self.song_list) > 1:
            # variable arguments e.g. "$art-$ttl.mp3"
            raise Exception("Rename Exception: <%s>\n Attempting to rename multiple songs and target name does not have variable arguments. "%name)
            
        for song in self.song_list:
            self.__renameSingleSong(song,dst)

        self.clear()
        
    def __renameSingleFile(self,src,dst):
        """ src as path to file.
            dst as path to folder
        """
        name = fileGetFileName(src)
        path = fileGetPath(src)

        if fileGetDrive(src) != fileGetDrive(dst): # cannot move over drives
            return ""
            
        src_dir  = fileGetPath(src)
        
        try:
            os.rename(src,dst);
        except:
            return ""
        else:
            return dst
                
        return ""
    
    def __renameSingleFolder(self,src,dst):
        """ src as path to folder.
            dst as path to folder
        """
        # get rid of the final slash in src folder
        src = src if src[-1] not in "\\/" else src[:-1]

        if fileGetDrive(src) != fileGetDrive(dst): # cannot move over drives
            return ""
            
        R = self.__getSongList(src)  # get all songs within src
   
        try:
            os.rename(src,dst)
        except:
            return ""
        else:
            self.__updateSongList(R,src,dst)
                    
        return "" 
    
    def __renameSingleSong(self,song,dst):
        name = fileGetFileName(dst)
        path = fileGetPath(dst)
        
        name = self.pattern_rename(song,name)
        
        ext = fileGetExt(song[EnumSong.PATH])
        
        if ext != fileGetExt(name):
            name += '.'+ext
        
        dst = os.path.join(path,name)

        new_path = self.__renameSingleFile(song[EnumSong.PATH],dst)

        if new_path != "": # fails when empty string is returned
            song[EnumSong.PATH] = new_path 
            
    def __getSongList(self,src):
        """
            src as directory path
            
            pull all songs in src or in subfolders and return as list
            
            check against the library
        """
        R = []
        for song in self.library:
            if comparePathLength(src,song[EnumSong.PATH]):
                R.append(song)
        return R
        
    def __updateSongList(self,slist,src,dst):   
        """
            the songs in slist have been moved by a folder
            update there file paths
        """
        # for this function, the src must have a final slash
        if src[-1] not in "\\/":
            src = os.path.join(src,"")
            
        for song in slist:
            
            path = song[EnumSong.PATH]
            if comparePathLength(src,path):
                path = os.path.join( dst , path[len(src):] )
                song[EnumSong.PATH] = path
                print ">>",path
      
    def pattern_rename(self,song,name):
        """ useing rename_dict replace $attributes with song meta data """
        # see expandExifMacro
        sigil = '$'
        s = unicode(name)
        for key,value in self.rename_dict.items():
            if value == EnumSong.SONGID:
                s = s.replace(sigil+key,unicode(song.id));
            elif value < EnumSong.STRINGTERM: # value is an array index
                s = s.replace(sigil+key,unicode(song[value]));
            elif value < EnumSong.NUMTERM:
                s = s.replace(sigil+key,"%02d"%song[value]);
        return s;
       
    def __str__(self):
        s  = "[ %s ], "%self.file_list
        s += "[ %s ], "%self.folder_list
        s += "[ %s ]"%[ song[EnumSong.PATH] for song in self.song_list ]
        return s
        
    def clear(self):
        self.file_list = []
        self.folder_list = []
        self.song_list = []
        self.library = []
        self.rename_dict = {}
        
if __name__ == "__main__":

    # ############################
    # dummy the rename function that this module
    # uses to move files, for testing
    
    def printer(src,dst):
        print "FROM: ",src
        print "TO  : ",dst
  
    os.rename = printer
    
    # ############################
    p1 = "C:\\top\\sub\\song1.mp3"
    p2 = "C:/top/alt/song2.mp3"
    
    ft = "C:\\top"
    f1 = "C:\\top\\sub\\"
    f2 = "C:/top/alt"
    f3 = "C:/temp/"
    
    s1 = Song(p1)
    s2 = Song(p2)
    s1[EnumSong.ARTIST] = "Beast"
    s1[EnumSong.TITLE]  = "Mr Hurricane"
    s1[EnumSong.ALBUM]  = "Beast"
    s2[EnumSong.ARTIST] = "Yui"
    s2[EnumSong.TITLE]  = "GoodBye-Days"
    s2[EnumSong.ALBUM]  = "CAN'T BUY MY LOVE"
    
    d = { "art":EnumSong.ARTIST, "alb":EnumSong.ALBUM, "ttl":EnumSong.TITLE}
    
    fm = Song_File_Manager()
    
    # ####################################
    
    fm.setSong( [s1,s2] )
    # ##############################################
    fm.clear()
    print "\nMoving Files to new Directory"
    
    fm.setFile(p1)
    fm.setFile(p2)
    
    fm.move("C:\\New Folder")
    
    # ##############################################
    fm.clear()
    print "\nMoving Folders to new Directory"
    
    fm.setFolder(ft)
    fm.setLibrary([s1,s2])
    fm.move("C:\\New Folder")
    
    # ##############################################
    fm.clear()
    print "\nMoving Songs to new Directory"
    
    fm.setSong(s1)
    fm.setSong(s2)
    fm.move(f3)
    
    # ##############################################
    fm.clear()
    print "\nRename Songs"
    
    fm.setSong([s1,s2])
    fm.setRenameDict(d)
    name = "$art-$alb-$ttl"
    path = fileGetPath(s1[EnumSong.PATH])
    path = os.path.join(path,name)
    fm.renameSong(path) # note lack of file extension
    
    # ##############################################
    fm.clear()
    print "\nRename File"
    fm.setFile(p1)
    name = "new_file_name.txt" # note file extension again
    path = fileGetPath(p1)
    path = os.path.join(path,name)
    fm.renameFile(path)
    
    # ##############################################
    fm.clear()
    print "\nRename Folder"
    fm.setFolder(f3)
    fm.setLibrary([s1,s2])
    name = "New Folder" # note file extension again
    path = fileGetParentDir(f3)
    path = os.path.join(path,name)
    fm.renameFolder(path)
    
        
        