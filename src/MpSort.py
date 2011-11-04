


def sortKey(index):
    """
        returns a lambda expression to be used as
        a key for sorting a list
    """
    if index == MpMusic.PATH:
        return lambda song: __sort_parameter_path__(song)
    elif index <= MpMusic.STRINGTERM:
        return lambda song: sort_parameter_str(song,index)
    elif index == MpMusic.FREQUENCY:
        return lambda song: __sort_parameter_freq__(song)
    elif index == MpMusic.SONGID:
        return lambda song: song.id
        
    return lambda song : song[index] 
    
def sort_parameter_str(song,index):
    """
        when searching by string parameters
        check to see if the string starts with certain words,
        and remove them
    """
    s = unicode(song[index])
    if s.lower()[0:4] == "the ":
        return s[4:]
    return s
    
def __sort_parameter_path__(song):
    """
        when searching by string parameters
        check to see if the string starts with certain words,
        and remove them
    """
    #s = unicode()
    return song[MpMusic.PATH].lower().replace('\\','/')
     
def __sort_parameter_freq__(song):
    """
        when searching by Frequency
        zero is considered infinity
    """
    if song[MpMusic.FREQUENCY] == 0:
        return 9999 #~27 years a long enough time to consider 'max'?
    return song[MpMusic.FREQUENCY]
       
def sortLibrary(index,r=False):
    # the lambda expression returns the element to compare in a song
    # current implementation returns the sorted form of the library
    
    g = sortKey(index)
        
    return sorted(MpGlobal.Player.library, key = g, reverse=r )
def sortLibraryInplace(index,r=False):
    """
        Sort the Library List inplace
    """
    ico = MpGlobal.icon_Clear
    if index in (MpMusic.ARTIST, MpMusic.TITLE,MpMusic.ALBUM):
        ico = MpGlobal.icon_Check if r else MpGlobal.icon_Clear
    else:
        ico = MpGlobal.icon_Clear if r else MpGlobal.icon_Check
    MpGlobal.Window.act_sfl_reverse.setIcon( ico )
    
    g = sortKey(index)
    #s = datetime.datetime.now()

    MpGlobal.Player.library.sort(key = g, reverse=r )

    if (MpGlobal.Player.lastSortType == index):
        MpGlobal.Player.lastSortType = -index # to maintain value for reference, cehck if less than zero then set positive
    else:
        MpGlobal.Player.lastSortType = index
     
    setSortActionIcons(index)
    #e = datetime.datetime.now()
    #print e-s
    return
def sortList(R,index,r=False):
    """
        sort an arbitrary song list inplace
    """
    g = sortKey(index)
    R.sort(key = g, reverse=r )

    
def ShuffleList(R):
    """
        Shuffle an entire list
    """
    ShufflePartition(R,0,len(R))
def ShufflePartition(R,s,e):
    """
        Shuffle a list inplace
        shuffle only the elements starting with 's'
        and ending at element 'e'
        
        prevent similar artists from appearing next to each other
        if possible
    """
    l = e-s#len(R)
    if l <= 1: # nothing to shuffle
        return 
        
    for x in range(s,e):
        # collisions are more likely at the end of a data set. 
        # and are unavoidable, so speed up the process by reducing the attempts
        for i in range(1+e-x):  # range is at least 3
            n = random.randrange(x,e)
            if x > 0 and R[x-1][MpMusic.ARTIST] != R[n][MpMusic.ARTIST] and n != x:
                break;
        # swap
        (R[x],R[n]) = (R[n],R[x])
    
    
def setSortActionIcons(index):
    MpGlobal.Window.act_sfl_artist   .setIcon( MpGlobal.icon_Check if index == MpMusic.ARTIST    else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_title    .setIcon( MpGlobal.icon_Check if index == MpMusic.TITLE     else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_album    .setIcon( MpGlobal.icon_Check if index == MpMusic.ALBUM     else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_playcount.setIcon( MpGlobal.icon_Check if index == MpMusic.PLAYCOUNT else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_rating   .setIcon( MpGlobal.icon_Check if index == MpMusic.RATING    else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_freq     .setIcon( MpGlobal.icon_Check if index == MpMusic.FREQUENCY else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_datestamp.setIcon( MpGlobal.icon_Check if index == MpMusic.DATESTAMP else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_path     .setIcon( MpGlobal.icon_Check if index == MpMusic.PATH      else MpGlobal.icon_Clear )
    
    MpGlobal.Window.act_sfl_length   .setIcon( MpGlobal.icon_Check if index == MpMusic.LENGTH    else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_skipcount.setIcon( MpGlobal.icon_Check if index == MpMusic.SKIPCOUNT else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_fsize    .setIcon( MpGlobal.icon_Check if index == MpMusic.FILESIZE  else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_genre    .setIcon( MpGlobal.icon_Check if index == MpMusic.GENRE     else MpGlobal.icon_Clear )

 



from calendar import timegm
import os
import time
import datetime
import random
import re
import subprocess
import ctypes
   
   
from StringQuoter import *    
from MpGlobalDefines import *
from MpSong import Song
from datatype_hex64 import *
from MpFileAccess import *
from SystemPathMethods import * 
from MpScripting import *