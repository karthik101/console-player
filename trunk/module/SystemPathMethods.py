
# #########################################################
# #########################################################
# File: MpThreading
# Description:
#       this file provides several methods that are often used when working with file paths
#       the goal of this file is to work on any file system, windwos, mac, linux
# #########################################################

import os
import sys

isPosix = os.name == 'posix'

import ctypes

import urllib
import re
if not isPosix:
    import win32file
    import win32con

    
    
def fileGetExt(file):
    """ return the extension part of the file"""
    file = unicode(file)
    return file[file.rfind(".")+1:]

def fileGetFileName(file):
    """ return the name + . + ext of the file"""
    file = unicode(file)
    # allow for both types of slashes in path uris
    return file[max(file.rfind("/"),file.rfind("\\"))+1:]
    
def fileGetName(file):
    """ return only the name part of the file"""
    fname = fileGetFileName(file)
    return fname[:fname.rfind(".")]
    
def fileGetPath(file):
    """ return the path, WITH the final slash"""
    file = unicode(file)
    # allow for both types of slashes in path uris
    return file[:max(file.rfind("/"),file.rfind("\\"))+1]  

def fileSetExt(file,new_ext):
    """ change the extension of file to new_ext
        if new_ext is an empty string the extension will be removed
    """
    if len(new_ext) > 0:
        if new_ext[0] != '.':
            new_ext = '.' + new_ext
    fname = fileGetName(file)

    return os.path.join(fileGetPath(file),fname+new_ext)
    
def dirGetParentDirName(path):
    """ path with or without final backslash, and not a file path
        must be dir path
        return the name of the parent directory, or drive name
        
    """
    t = path[:]
    if path[-1] == "\\" or path[-1] == "/":
        t = path[:-1]
        
    name = fileGetFileName(t) # i think this makes me a cheater
    
    if name == "" :
        if isPosix:
            return opath[:1+opath.find('/',1)];
        else:
            return opath[:3] # return the drive only
    
    return name
            
def fileGetParentDir(path):
    """ return the path, with the final slash"""
    #path = fileGetPath(file)
    
    path = unicode(path)
    
    opath = path[:]
    if path[-1] == "\\" or path[-1]=="/" :
        path = path[:-1] # remove any trailing slashes as well
    
    i = max(path.rfind("/"),path.rfind("\\")) + 1
    
    if i<1:
        if isPosix:
            return opath[:1+opath.find('/',1)];
        else:
            return opath[:3] # return the drive only
    else:
        return path[:i] # remove the final back slash
    
def fileGetSize(path):
    return (os.path.getsize(path) / 1024)
    
def pathIsUnicodeFree(path):
    path = unicode(path)
    return all(ord(c) < 256 for c in path)

def comparePath(p1,p2,len=0):
    """
        i have been having issues with comparing paths
        the slashes could either be foward or backwards depending on the OS
        or the user types them. I myself have song mixmatching paths in a single string
        easiest thing to do is strip all slashes, send to lowercase then compare
        first test, using Explorer, revealed that all issues with K-On Singles were
        resolved
        
    """
    
    p1 = unicode(p1).lower()
    p2 = unicode(p2).lower()
    # set all slashes to be the same
    p1 = p1.replace("\\","/")
    p2 = p2.replace("\\","/")
        
    return p1 == p2
    
def comparePartInPath(path,part,len=0):
    """
        i have been having issues with comparing paths
        the slashes could either be foward or backwards depending on the OS
        or the user types them. I myself have song mixmatching paths in a single string
        easiest thing to do is strip all slashes, send to lowercase then compare
        first test, using Explorer, revealed that all issues with K-On Singles were
        resolved
        
    """
    
    path = unicode(path).lower()
    part = unicode(part).lower()
    # set all slashes to be the same
    path = path.replace("\\","/")
    part = part.replace("\\","/")
        
    return path.find(part) >= 0
    
def comparePathLength(p1,p2,l = 0):
    
    p1 = unicode(p1).lower()
    p2 = unicode(p2).lower()
    
    p1 = p1.replace("\\","/")
    p2 = p2.replace("\\","/")
        
    if l == 0:
        l = len(p1)
        
    return p1[:l] == p2[:l]
    
def pathMatchExt(path) :
    """check if the file at path contains a song extension that is usable by the player"""
    fext = fileGetExt(path).lower()
    file_list = ( 'mp3',
                  'm4a', 'm4b', 'm4p', 'mpeg4', 'aac',
                  'asf','wma',
                  'flac',
                )
    return fext in file_list;    
    
def copyPlayListToDirectory(dir,list):

    # force all slashes the same direction

    dir = dir.replace("\\","/")
    # make sure the given directory terminates with a back slash
    if dir[-1] != "/":
        dir += "/"
        
    for song in list:
        validPath = song.shortPath()
        
        testMiniPathExists(dir, validPath)
        
        newPath = dir + validPath
        
        # if the file does not exist copy it
        if os.path.exists(newPath) == False:
            copy(song[MpMusic.PATH],newPath)       
            
def testMiniPathExists( dir, mpath ):
    """ test that the calculated minpath exists
        if it does not, create it
    """
    # generate a list of all folders in the path name
    R = mpath.split("\\")[:-1] # cut the file name out of the folder list

    path = dir
    
    for p in R:
        os.path.join(path,p,"")
        if os.path.exists(path) == False :
            os.mkdir(path)

def createDirStructure(path):
    """ test that a structure in a given path exists
        if any sub folder in path does not exist
        create it
    """
    opath = path.replace("\\","/")
    R = opath.split("/")
    if not os.path.isdir(path):
        R = R[0:len(R)-1] # cut the file name out of the folder list
    
    if isPosix:
        path = '/'+R[0]+'/';    #TODO check top level path or assume it is /media/ or /home/
    else:
        path = R[0]+"\\"
    # C:\folder\folder2\file.mp3
    # C: folder folder2 file
    # for range : folder folder2
    for x in range(1,len(R)):
        path = os.path.join(path,R[x],"")
        if os.path.exists(path) == False :
            os.mkdir(path)   
            
def pathCreateURI(path):
    path = path.replace("\\","/");
    # undefined results with quote when string is not UTF-8
    # setting utf-8 here is easier than forcing
    # the whole application to use utf-8
    path = unicode(path).encode('utf-8')
    
    string = str("file:///"+urllib.quote(path));
    return string;
    
def URICreatePath(path):
    path = path.replace("file:///","");
    return urllib.unquote(path);

def OS_FileName_Correct(filename):
    """
        filename as filename, from output fileGetName
        so, no extension and no complete path. e.g. for the file C:\File.txt
        filename should equal "File"
        
        this function will make sure that that no illegal characters are in the name
        example '/' wil be removed

        unicode is allowed under certain locales of isalpha
        that may pose problems for some systems
        
    """
    
    white = " +=-_.()[]{}`~@#$%^&"
    
    s = unicode(filename)
    #print "".join([x for x in s if x.isalpha() or x.isdigit() or x in "+=-_.()[]{}`~@#$%^&"])
    return "".join([x for x in s if x.isalpha() or x.isdigit() or x in white])

def UnixPathCorrect(path):
    """
        If the path is not found, assume there is a case error
        if there is this function will return the corrected case
        assuming there are no alternate case collisions
        if for any other reason the path is wrong an empty 
        string will be returned
    """
    R = path.split('/');
    
    if R[0] == '~':
        newpath = '~/'
    else:
        newpath = '/'+R[0]
    
    for i in range(1,len(R)):
    
        testpath = os.path.join(newpath,R[i])
        
        if os.path.exists(testpath):
            newpath = testpath;
        else:
            S = os.listdir(newpath)
            #print S
            temp = R[i].lower();
            for item in S:
                if item.lower() == temp:
                    newpath = os.path.join(newpath,item)
                    break;
            else:
                print 'UnixPathCorrect %s not found'%temp
                return ''
        
    return newpath
    
def stripDriveFromPath(driveList,filepath):
    """
       Check the filepath to see if it starts with a dive from the drive list
       and remove the drive.    
    """
    filepath = unicode(filepath)
    for drive in driveList:
        if filepath.startswith(drive):
            filepath = filepath[len(drive): ]
            break;
    # huge errors on linux when the resulting path starts with a slash
    if filepath[0] == '/' or filepath[0] == '\\':
        return filepath[1:]
    return filepath
  
def atoi(a):
    """
        converts string to int by taking only the first integer
        in the string.
        
        int fails on "12A" when i sometimes want it to be 12.
    """
    i = "";
    R = ('0','1','2','3','4','5','6','7','8','9');
    #a = str(a)
    if isinstance(a,(long,int)):
        return a
    if isinstance(a,(float,)):
        return int(a)
    for j in range(len(a)):
        if a[j] in R:
            i += a[j];
        else:
            break;
    try:
        return int(i);
    except:
        return 0;
  
  
if isPosix: # def explorerOpen
    def explorerOpen(filepath): # filepath or directory
        print "TODO: implement os.startfile on linux"
        return;
else:
    def explorerOpen(filepath): # filepath or directory
        os.startfile(filepath);
  
if isPosix: # def fileGetDrive
    def fileGetDrive(filepath):
        R = filepath.split('/')
        if len(R) == 0:
            return '/'
        elif R[0] == 'media' and len(R) == 1:
            return '/media/'
        elif R[0] == 'media' and len(R) > 1:
            return '/'+R[0]+'/'+R[1]+'/'
        else:
            return  '/'+R[0]+'/'
else:
    def fileGetDrive(filepath):
        return unicode(filepath)[0].upper() + u":\\"  

if isPosix: # def driveGetFreeSpace
    def driveGetFreeSpace(path):
        return (0,0,0,0); #TODO return freespace of given device /media/device/<dont care/
else: 
    def driveGetFreeSpace(path):
        drive = unicode(path)[0] + u":\\"

        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(drive), None, None, ctypes.pointer(free_bytes))

        bytes = free_bytes.value
        kbytes = bytes/1024
        mbytes = kbytes/1024
        gbytes = mbytes/1024

        return (bytes,kbytes,mbytes,gbytes)        
        
if isPosix: # def dirCheckAttribNormal
    def dirCheckAttribNormal(path):
        """ return if the path is a directory, and not hidden, system or other
        """
        return 0; #TODO return file attributes    
else:
    def dirCheckAttribNormal(path):
        """ return if the path is a directory, and not hidden, system or other
        """
        return (win32file.GetFileAttributes(path) == win32con.FILE_ATTRIBUTE_DIRECTORY)     

if isPosix: # def systemDriveList
    """
        there are no 'drives' in linux/Ubuntu
        i will therefore return a list of mounted devices found in media
        this will unfortunatley list umounted devices as well.
        
        # extraLocations = Settings.DRIVE_ALTERNATE_LOCATIONS
    """
    def systemDriveList():
        R = os.listdir('/media/');
        S = [];
        for path in R:
            fpath = os.path.join('/media',path,''); # full file path to drive list
            if os.path.isdir(fpath):
                S.append(fpath);    
        return S + ['/home/Music/','/']
else:
    def systemDriveList():
        return  ['%s:\\' % d for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists('%s:' % d)]

        
                
                
                
        