#TODO - the XML "works" - but PyQt supplies objects for parsing XML - use those

ufr = lambda FILE:  unicode( FILE.readline().strip() ,"utf-8");

def xml_open(file):

    D={}
    lol=[]
    
    with open(file,"r") as FILE:
        # first line of an xml file is:
        # <?xml version="1.0" encoding="UTF-8"?>
            
        xml_format = xml_read_until_line_startswith(FILE,"<?xml");
        
        print xml_format
        xml_read_until_line_startswith(FILE,"<dict>");
        xml_read_until_line_startswith(FILE,"<key>Tracks");
        FILE.readline(); # = dict
        song = True
        
        while song != None:
            id,song,valid = xml_itunes_read_song(FILE)
            if song != None:
                temp = xml_itunes_create_song(song);
                if temp != None:
                    D[id] = temp;
        print len(D);    
        xml_read_until_line_startswith(FILE,"<key>Playlists");
        
        FILE.readline(); # == array
        valid=True
        
         # list of lists
        while valid==True:
            name,newList,valid = xml_itunes_read_playlist(FILE);
            if valid and len(newList) > 0:
                lol.append( [name,newList] )
                print name.encode("unicode-escape"),"-",len(name),"-",len(newList)
        # playlists follow here, starting with <dict>
        
    xml_itunes_save_playlists(D,lol);    
    
    R = [None]*len(D);
    i=0;
    for id,song in D.items():
        R[i] = song
        i += 1;
        
    return R;
    
def xml_itunes_create_song(D):

    #<key>Name</key><string>From Yesterday</string>
    #<key>Artist</key><string>30 Seconds to Mars</string>
    #<key>Album</key><string>A Beautiful Lie</string>
    #<key>Genre</key><string>Indie Rock</string>
    #<key>Size</key><integer>4010037</integer>
    #<key>Total Time</key><integer>250007</integer>
    #<key>Track Number</key><integer>14</integer>
    #<key>Bit Rate</key><integer>128</integer>
    #<key>Location</key><string>file://localhost/C:/Users/Ryan/Music/iTunes/iTunes%20Music/30%20Seconds%20to%20Mars/A%20Beautiful%20Lie/14%20From%20Yesterday.m4a</string>
    
    path = D.get("Location","")
    
    if path == "":
        print "not a path"
        return None;
        
    if path.startswith("file://localhost/"):
        path = path.replace("file://localhost/","")
        
    path = urllib.unquote(path)
    
    if not os.path.exists(path):
        print "not an thing"
        return None;

    song = id3_createSongFromPath(path);
        
    # so we have a song but it is not reliable    
    return song;
    
def xml_itunes_save_playlists(songDict,playListList):
    # pass a song Dictionary where an itunes id number corresponds to a song.
    # and a list of playlists, with name,list, and each item is an id to a song.
    # create the playlist as a list of songs, and then save as a real playlist
    
    for name,list in playListList:

        R=[]
        for item in list:
            temp = songDict.get(item,None)
            if temp != None:
                R.append(temp)

        print name.encode("unicode-escape"),len(R)
        name=  OS_FileName_Correct ( name.encode("unicode-escape") )
        
        fullpath=os.path.join(MpGlobal.installPath,"playlist","itunes_%s.playlist"%(name))
        playListSave( fullpath, R )
        # save list to playlist folder using itunes_name.encode("unicode-escape")     
    return            
  
def xml_read_until_line_startswith(FILE,string):

    line = ufr(FILE);
    while line.startswith(string) == False and line :
        line = ufr(FILE);
    return line;
  
def xml_split_keyval(string):
    """
        given a string return a tuple with the first key value pair
        
        <key>KEYNAME</key><TYPE>TYPEVALUE</TYPE>
        type is integer, string, etc
    """
    key = u"None"
    val = None
    typ = u"None" # type of the value
    ind = 0  # ending index in the str.
    
    R = string.strip().split("<");
    # R = ['', 'key>key', '/key>', 'value>value', '/value>']
    if len(R) > 1:
        _a,key = R[1].split(">")
        if len(R) > 3:
            typ,val = R[3].split(">")
        
        
        return (key,val,typ);
    return ("","","");
def xml_itunes_read_song(FILE):
    
    line = ufr(FILE)
    
    if line == u"</dict>": # end of songs section
        return (0,None,False)
        
    _id = xml_split_keyval( line  )[0] 
    
    FILE.readline() # should equal <dict>
    line = ufr(FILE)
    
    song = {};
    
    # song key value pairs
    while line != u"</dict>":
        key,val,typ = xml_split_keyval(line)
        song[key] = val;
        line = ufr(FILE)

    valid = True;    # if item is a valid song file
        
    return (_id,song,valid);

def xml_itunes_read_playlist(FILE):

    line = FILE.readline().strip(); # read the word <dict>,   start of a playlist
    if line != "<dict>":
        return "",[],False;
    
    header = {};
    R = [];
    
    
    # read the playlist header, extract the Name
    line = ufr(FILE);
    while line != u"<array>":
        if line.startswith(u"<key>"):
            k,v,t = xml_split_keyval(line);
            header[k] = v;
        line = ufr(FILE);

        
        
    line = ufr(FILE)

    # read the playlist index values
    while line != u"</array>":
        line = FILE.readline().strip(); 
        k,v,t = xml_split_keyval(line); # TRACKID, IDNUMBER, integer
        R.append(v)
        FILE.readline() # skip </dict>
        line = ufr(FILE)
        
    FILE.readline() # skip </dict>
    
    valid = True;
    
    return header.get(u"Name",u"NONE"),R,valid
    

