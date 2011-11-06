# #########################################################
# #########################################################
# File: ReadableDictionary_FileFormat
# Description:
#   this file provides 2 methods for saving/loading data
# from any object to a text file that can easily be read
# and modified by anyone.
# it uses the __dict__ value of an object to save all variables
# to the text file using a "type_VARIABLE=VALUE" format.
# by giving the type anyone can quickly identify the kind of
# legal values, and aids in reading back the values
#
# This file is used to save Global Settings for the ConsolePlayer application
#
# limitations:
#   any lists must be of uniform type,
#       i.e. lists of all integers or all string values 
#       ( no floats supported currently)
#   strings are always read back as unicode objects
# #########################################################
import os
import sys

from SystemPathMethods import *

isPosix = os.name == 'posix'

#TODO: rename these functions and then send this file to ./modules/
# this is generic enough to be used anywhere
         
def ReadableDict_Save(file, object):
    """
        using the data found in D, a dictionary
        store that data in a file in the format:
        key:value
        sort the keys for readability
        the format intent of a Settings dictionary is as follows:
        keys are in the form of 'type_Attribute'
        values are of type 'type'
        example 
            int_Width:600
            str_Title:MP3Player
        This way parseing and forming of the dictionary can be automatic  
    """
    
    
    
    typeDict = {str(int):'int',
            str(long):'int',
            str(str):'str',
            str(unicode):'str',
            str(bool):'bin',
            str(list):'csv'} # and lst for integer values

    # from the settings dictionary build a typed dictionary i a human readable save format.
    D = {} # dictionary of key values to save
    for key,value in object.__dict__.items():

        newKey = "%s_%s"%(typeDict.get(str(type(value)),'???'),key)

        if (type(value) == list):
            if len(value) > 0: # don't save if it's empty?
                if type(value[0]) != str and type(value[0]) != unicode: # convert non-string types to string
                    D["lst_%s"%key] = unicode(','.join( str(x) for x in value )).encode('unicode-escape')
                else:
                    D[newKey] = unicode(','.join( value )).encode('unicode-escape')
            else:
                D[newKey] = ""
        else:
            D[newKey] = value
            
    # create a sorted 2d list of values
    
    R = sorted(D.items(), key = lambda x: x[0])
    wf = open(file,"w")
    for key,value in R:
        wf.write( "%s:%s\n"%(key,value) )
    wf.close()

def ReadableDict_Load(file, object):
    """
        read in and set the data from the settings file
        D is the dictionary of values to set
        the intent is to create a default dictionary
        then check if the settings file exists
        if it does override the entry in the dictionary
        with the value in the dictionary
    """
    # dictionary of values to returns
    #file = MpGlobal.FILEPATH_SETTINGS
    if os.path.exists(file):
    
        rf = open(file,"r")
        line = True 

        while line:
            line = rf.readline().strip()
            if line != "":
            
                i = line.index(":") # first index of a colon
                
                key,value = ( line[:i], line[i+1:])
                
                dim = key[:3]
                key = key[4:]
               
                # check if the key exists in the object
                # therefore deprecaed values are not loaded, and user fat finger values are not laoded
                if key in object.__dict__:
                    # load the setting only if it passes basic type checking, only load ints into ints
                    # this way a user cannot attempt to change the basic data type
                    # bad values will still make it crash (string in int) and should be fixed.
                    if dim == u"int" and (type(object.__dict__[key]) == int or type(object.__dict__[key]) == long):
                        temp = 0;
                        try:
                            temp = int(value)
                        except:
                            print "Not Integral Value: %s_%s = %s"%(dim,key,value)
                        else:
                            object.__dict__[key] = temp
                    elif dim == u"bin" and type(object.__dict__[key]) == bool:
                        object.__dict__[key] = (value.strip() == "True")
                        
                    elif dim == u"lst" and type(object.__dict__[key]) == list:
                        object.__dict__[key] = value.split(',')
                        i=0;
                        while i < len(object.__dict__[key]): # remove empty array indices
                            if len(object.__dict__[key][i]) == 0:
                                object.__dict__[key].pop(i);
                            else:
                                object.__dict__[key][i] = atoi(object.__dict__[key][i])
                                i += 1;
                    elif dim == u"csv" and type(object.__dict__[key]) == list:
                        object.__dict__[key] = unicode(value,'unicode-escape').split(',')
                        i=0;
                        while i < len(object.__dict__[key]): # remove empty array indices
                            if len(object.__dict__[key][i]) == 0:
                                object.__dict__[key].pop(i);
                            else:
                                object.__dict__[key][i] = object.__dict__[key][i].strip()
                                i += 1;
                        
                    elif dim == u"str" and type(object.__dict__[key]) == str or type(object.__dict__[key]) == unicode:
                        object.__dict__[key] = unicode(value)
                    else:
                        print "Error Loading Setting: %s_%s = %s"%(dim,key,value)
                else:
                    print "No Setting Named: %s_%s = %s"%(dim,key,value)
            
        rf.close()

        #for k,v in D.items():
        #    print k,"=>",v
    return;
    

