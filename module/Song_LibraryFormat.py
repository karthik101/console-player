# #########################################################
# #########################################################
# File: MpFileAccess
# Description:
#   Save/Load .libz files
#   These methods return a list of Songs, as defined in 
#       Song_Object.py
# #########################################################
import os
import sys



import struct
import urllib

from Song_Object import *

from SystemPathMethods import *
from SystemDateTime import DateTime
try:
    import pylzma
except:
    print "cannot import pylzma"
    pylzma = None
# ##############################
#  Library save formats
def musicSave_LIBZ(filepath,songList,typ=1,block_size=128):
    """
        save a new file, but first compress it using LZMA.
        
        file is saved as a binary file.
       
        HEADER:
            several 8 byte frames in a 4:4 byte pattern
            4 bytes describing the value in format 'LXXX'
            4 byte integer
         
            the header ends when the first string 'SIZE' is found
            
        Frame
            8 byte header, followed by SIZE bytes corresponding to X LZMA compressed song representations.
            Frame Header:
                4 bytes - the word 'SIZE'
                4 bytes - unsigned integer, size of frame, excluding frame header
            Frame Body:
                SIZE bytes compressed using pyLZMA.compress()
            
            
        each frame will compress
        
        HEADERS:
        LVER - VERSION    :outlines if any changes to reading will be needed (future proofing)
        LTYP - TYPE       : bitwise or combination of save settings
                          :  1 - no compression
                          :  2 - remove drie list from start of path ( multi os mode )
        LBLK - BLOCK SIZE : maximum number of songs per block, after decompression 
        LCNT - COUNT      : count of all songs saved to the file        
        LFMT - SNG FORMAT : number of lines per song record     
        
        Based off of the following two docstrings. there is no reason to store the parameters used for saving.
        
        compress(string, 
             dictionary=23, 
             fastBytes=128, 
             literalContextBits=3, 
             literalPosBits=0, 
             posBits=2, 
             algorithm=2, 
             eos=1, 
             multithreading=1, 
             matchfinder='bt4') 

            Compress the data in string using the given parameters, returning a string containing 
            the compressed data.


        decompress(data[, maxlength]) 
            Decompress the data, returning a string containing the decompressed data. 
            If the string has been compressed without an EOS marker,
            you must provide the maximum length as keyword parameter.


        decompress(data, bufsize[, maxlength])
            Decompress the data using an initial output buffer of size bufsize.
            If the string has been compressed without an EOS marker, 
            you must provide the maximum length as keyword parameter.
    """
    
    dt = DateTime();
    dt.timer_start()
    
    with open(filepath,"wb") as FILE:
        FILE.write( struct.pack("4sI","LVER",1) );             # 
        FILE.write( struct.pack("4sI","LTYP",typ|1) );           # 
        FILE.write( struct.pack("4sI","LBLK",block_size) );    # number of songs in each block
        FILE.write( struct.pack("4sI","LCNT",len(songList)) ); # 
        FILE.write( struct.pack("4sI","LFMT",Song.repr_length() ) );
        LIBZ_write_songList(FILE,songList,typ,block_size)
        
    dt.timer_end();
    print "Saved %d songs to libz container in %s"%( len(songList), DateTime.formatTimeDeltams(dt.timedelta))
    
def musicLoad_LIBZ(filepath):
    """
        load the specified .libz file and return an array of songs.
        
        #todo : read 8 bytes
        # read in : LVERABCD
        # if A== 0x3D == '=' then file is ascii format
        
        # when saving a non binary version save version as '=001' or 3D 30 30 31
        # increment the version count for new ascii file formats
        # for binary formats:
        #   LVERABCD, where A,B,C,D are a little endian 32 bit integer with A=0x00
    """
    

    if not os.path.exists(filepath):
        return [];
    
    R=[];
    drivelist = [];
    cnt = 0
    
    dt = DateTime()
    dt.timer_start();
    with open(filepath,"rb") as FILE:
        # ##################################
        # read the header
        header={};
        bin = FILE.read(8);
        key,val = struct.unpack("4sI",bin)
        while key != "SIZE" and bin:
            header[key] = val;
            bin = FILE.read(8);
            if bin:
                key,val = struct.unpack("4sI",bin)
                
        # ##################################
        # process the header dictionary
        typ = header.get("LTYP",0)      # needed for restoring file paths
        blk = header.get("LBLK",128)    # not really needed
        fmt = header.get("LFMT",Song.repr_length()) # needed to restore each song record.
        cnt = header.get("LCNT",0)
        
        if typ&2 == 2: 
            drivelist=systemDriveList(); 
            
        # ##################################
        # now  read the data from the file.         
        bin = FILE.read(val);        
        while bin:
        
            if typ&1 == 0 and pylzma != None: #compression is only used when typ&1 == 0.
                bin = pylzma.decompress(bin);
            
            R += LIBZ_process_block( bin , typ, fmt, drivelist );

            bin = FILE.read(8);
            if bin:
                key,size = struct.unpack("4sI",bin)
                bin = FILE.read(size); # read val bytes from the frame  
   
    dt.timer_end();
    print "Loaded %d/%d songs from libz container in %s"%(len(R),cnt,DateTime.formatTimeDeltams(dt.timedelta))
    return R;
      
def LIBZ_write_songList(FILE,songList,typ,block_size): 
    """
        typ: bitwise or combination of flags.
            1 - no compression
            2 - remove drive
    """
    i=0;
    l = len(songList);
    
    
    drivelist=[];
    if typ&2 == 2: 
        drivelist=systemDriveList(); # fill this with values
        print "save using drive list: %s"%drivelist
        

    while i < l:
        block=""
        for x in xrange(block_size):
            if i < l:
                block += "<Song>\n%s</Song>\n"%(songList[i].__repr__(drivelist))
                #block += "%s"%(songList[i].__repr__(drivelist))
            else: break;
            i+=1;
            
        #if typ&1 == 0 and pylzma != None: # no compression for typ|=1 
        #    # exec MpGlobal.t1=23;MpGlobal.t2=128;
        #    #dictionary=MpGlobal.t1,fastBytes=MpGlobal.t2
        #    block = pylzma.compress(block);

            
        # write a header for the block, SIZE=length of the block
        FILE.write( struct.pack("4sI","SIZE",len(block)) );
        FILE.write(block);

def LIBZ_decompress_to_file(src,dst):

    header=""
    data=""
    key =""
    H={};
    val =0
    
    with open(src,"rb") as FILE:
        # read the header
        bin = FILE.read(8);
        key,val = struct.unpack("4sI",bin)
        while key != "SIZE" and bin:
            header += "%s=%d\n"%(key,val);
            H [key] = val;
            bin = FILE.read(8);
            if bin:
                key,val = struct.unpack("4sI",bin)
        # now  read the data from the file.         
        typ = H.get("LTYP",0)      # needed to restore each song record.
        bin = FILE.read(val);        
        while bin:
        
            if typ&1 == 0 and pylzma != None:
                data += pylzma.decompress(bin);
            else:
                data += bin;
            bin = FILE.read(8);
            if bin:
                key,val = struct.unpack("4sI",bin)
                bin = FILE.read(val); # read val bytes from the frame   
        #data += FILE.read();
    
    with open(dst,"w") as FILE:
        FILE.write( header );
        FILE.write( data );
        
def LIBZ_compress_to_file(src,dst):

    header=""   #the binary form of header data
    data=""     # the binary form of text data ( may not be compressed )
    block=""    # a single block of data
    
    
    typ=0;
    blk=128;
    fmt=6;
    
    with open(src,"r") as FILE:
        line = FILE.readline()
        while line[0]=='L' and line[4] == '=': #TODO: this should never be a band name right?
            key,val= line.strip().split('=');
            header += struct.pack("4sI",key,int(val.strip()))
            if key == "LTYP": typ = int(val.strip());
            if key == "LBLK": blk = int(val.strip());
            if key == "LFMT": fmt = int(val.strip());
            line = FILE.readline()

        while line:
            # read blocks... the first line has already been read
            
            block="" # reset the block data
            i=0
            while i < blk and line:
                block += line
                line = FILE.readline()  
                if line == "</Song>":
                    i+=1;
            block += line # add the last </Song> or empty string if at end of file
            
            #print ("%s...%s"%(block[:8],block[-8:])).replace('\n','<>')
            if typ&1==0 and pylzma != None:
                block=pylzma.compress(block)
 
            data += struct.pack("4sI","SIZE",len(block) );
            data += block;

    
    with open(dst,"wb") as FILE:
        FILE.write( header );
        FILE.write( data );
   
# ###########################   
   
def LIBZ_process_block(data,typ,fmt, drivelist):
    """
        given a decompressed block of songs return a list of songs.
    """
    R = [];
    
    i=0;
    j=0;
    l = len(R);

    s=len("<Song>")+1   # +1 fr newline
    e=data.find("</Song>")
    end_tag_len=len("</Song>")
    
    while e != -1:  # this block of  code is skippped when the data only contains one song.
        repr = data[s:e-1]
        if len(repr) > 0:
            R.append( Song( repr,DRIVELIST=drivelist ) );
            
        data=data[e+end_tag_len:]
        #s=len("<Song>")
        e=data.find("</Song>")
    # restore the last song in the block.        
    
    repr = data[s:e]

    if len(repr) > 0:   
        R.append( Song( repr ) );
    
    return R;

# ###########################  
    
def musicBackup(path,songList,format=0,force = False):
    """
        save a copy of the current library to ./backup/
        only save if one has not been made today,
        delete old backups
        
        adding new music, deleting music, are good reasons to force backup
    """
    #path = os.path.join(MpGlobal.installPath,'backup')
    #songList = MpGlobal.Player.library
    
    if not os.path.exists(path):
        os.mkdir(path)
        print "backup directory created"
        
    dt = DateTime(); # create a new date time object
    date = dt.currentDate();
    hourmin = dt.currentTime();
    date = date.replace('/','-').replace('\\','-')
    
    name = 'music_backup-'
    fullname = name+date+'.libz'
    h,m = hourmin.split(':')
        
    #if (atoi(h) > 12) or force:  # save backups in the afternoon only
    
    R = []
    dir = os.listdir(path)
    for file in dir:
        if file.startswith(name) and fileGetExt(file) == "libz":
            R.append(file);
            
    newestbu = ""

    R.sort(reverse=True)
    
    if len(R) > 0:

        #remove old backups
        # while there are more than 6, 
        # and one has not been saved today
        while len(R) > 6 and R[0] != fullname: 
            delfile = R.pop()
            print "Deleting %s"%delfile
            os.remove(os.path.join(path,delfile))
            
        # record name of most recent backup, one backup per day unless forced    
        newestbu = R[0]
        
    # save a new backup 
    if force or newestbu != fullname:
        print "Saving %s"%fullname
        newbu = os.path.join(path,fullname)  
        musicSave_LIBZ(newbu,songList,format);
         
    
    
    
    