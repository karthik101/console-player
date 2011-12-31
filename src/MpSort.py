
import os
import random
import re
import subprocess
import ctypes
   
   
from StringQuoter import *    
from datatype_hex64 import *


from SystemPathMethods import * 
from Song_Object import Song,EnumSong

def sortKey(index):
    """
        returns a lambda expression to be used as
        a key for sorting a list
    """
    if index == EnumSong.PATH:
        return lambda song: __sort_parameter_path__(song)
    elif index < EnumSong.STRINGTERM:
        return lambda song: sort_parameter_str(song,index)
    elif index == EnumSong.FREQUENCY:
        return lambda song: __sort_parameter_freq__(song)
    elif index == EnumSong.SONGID:
        return lambda song: song.id
        
    return lambda song : song[index] 
    
def sort_parameter_str(song,index):
    """
        when searching by string parameters
        check to see if the string starts with certain words,
        and remove them
    """
    s = song[index]
    if s.lower().startswith("the "):
        return s[4:]
    return s
    
def __sort_parameter_path__(song):
    """
        when searching by string parameters
        check to see if the string starts with certain words,
        and remove them
    """
    #s = unicode()
    return song[EnumSong.PATH].lower().replace('\\','/')
     
def __sort_parameter_freq__(song):
    """
        when searching by Frequency
        zero is considered infinity
    """
    if song[EnumSong.FREQUENCY] == 0:
        return 9999 #~27 years a long enough time to consider 'max'?
    return song[EnumSong.FREQUENCY]
       
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
    
    if index in (EnumSong.ARTIST, EnumSong.TITLE,EnumSong.ALBUM):
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
            if x > 0 and R[x-1][EnumSong.ARTIST] != R[n][EnumSong.ARTIST] and n != x:
                break;
        # swap
        (R[x],R[n]) = (R[n],R[x])
      
def setSortActionIcons(index):
    MpGlobal.Window.act_sfl_artist   .setIcon( MpGlobal.icon_Check if index == EnumSong.ARTIST    else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_title    .setIcon( MpGlobal.icon_Check if index == EnumSong.TITLE     else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_album    .setIcon( MpGlobal.icon_Check if index == EnumSong.ALBUM     else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_playcount.setIcon( MpGlobal.icon_Check if index == EnumSong.PLAYCOUNT else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_rating   .setIcon( MpGlobal.icon_Check if index == EnumSong.RATING    else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_freq     .setIcon( MpGlobal.icon_Check if index == EnumSong.FREQUENCY else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_datestamp.setIcon( MpGlobal.icon_Check if index == EnumSong.DATESTAMP else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_path     .setIcon( MpGlobal.icon_Check if index == EnumSong.PATH      else MpGlobal.icon_Clear )
    
    MpGlobal.Window.act_sfl_length   .setIcon( MpGlobal.icon_Check if index == EnumSong.LENGTH    else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_skipcount.setIcon( MpGlobal.icon_Check if index == EnumSong.SKIPCOUNT else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_fsize    .setIcon( MpGlobal.icon_Check if index == EnumSong.FILESIZE  else MpGlobal.icon_Clear )
    MpGlobal.Window.act_sfl_genre    .setIcon( MpGlobal.icon_Check if index == EnumSong.GENRE     else MpGlobal.icon_Clear )

from MpGlobalDefines import *
from MpScripting import *