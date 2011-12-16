#----------------------------------------------------------
#----------------------------------------------------------
#  ConsolePlayer.py
#----------------------------------------------------------
# Info:
# Description:
#   Controls for reading/editing metadata tags in audio files
#
#----------------------------------------------------------
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.asf import ASF # *.wma
from mutagen.flac import FLAC


from SystemPathMethods import *
from SystemDateTime import DateTime
from Song_Object import *
from datatype_hex64 import *

ext_mp3  = ("mp3",)
ext_mp4  = ('m4a', 'm4b', 'm4p', 'mpeg4', 'aac')
ext_asf  = ('asf','wma')
ext_flac = ('flac',)

def id3_createSongFromPath(path):
    """ attempt to read the id3 data from the song
        if the songs format is not supported, return a blank song
        with the path set.
    """
    
    #check the extension and build a new song array from that type
    
    fext = fileGetExt(path).lower()
  
    song = Song(path)

    try :
        if fext in ext_mp3:
            id3_mp3_createSongFromPath(song)
        if fext in ext_mp4:
            id3_mp4_createSongFromPath(song)
        if fext in ext_asf:
            id3_asf_createSongFromPath(song)
        if fext in ext_flac:
            id3_flac_createSongFromPath(song)
    except Exception as e:
        print " *** Error [%s] Reading Tags for Type: %s"%(song, fext)
        for i in e:
            print "%s"%str(i)
                    
        
    song[EnumSong.FILESIZE] = fileGetSize(path)
    song[EnumSong.DATEADDED ] = DateTime.now()
    song[EnumSong.DATEADDEDS] = DateTime().currentDateTime() 

    
    if song[EnumSong.LENGTH] > 2000: # 2k seconds = 32 minutes. is that a good break point?
        song[EnumSong.LENGTH] /= 1000 # assume that th time measured was in milliseconds
        
    song.update();
    
    return song # return the blank song instead
    
def id3_mp3_createSongFromPath(song):
    audio = ID3(song[EnumSong.PATH])
    mp3 = MP3(song[EnumSong.PATH])

    getTag(song,audio,EnumSong.ALBUM ,"TALB");
    getTag(song,audio,EnumSong.ARTIST,"TPE1");
    getTag(song,audio,EnumSong.TITLE ,"TIT2");
    getTag(song,audio,EnumSong.GENRE ,"TCON");

    getTag_int(song,audio,EnumSong.SONGINDEX,"TRCK");
    getTag_int(song,audio,EnumSong.LENGTH,"TLEN");

    #print "S %d"%song[EnumSong.LENGTH]
    
    if song[EnumSong.LENGTH] == 0 or song[EnumSong.LENGTH] == 64:
        song[EnumSong.LENGTH] = int(mp3.info.length)
        
    #print "S %d"%song[EnumSong.LENGTH]  
    
    song[EnumSong.BITRATE] = mp3.info.bitrate
 
    #for i in range(len(song)):
    #    print "%d => %s"%(i,song[i]);
    
def id3_mp4_createSongFromPath(song):

    audio = MP4(song[EnumSong.PATH])

    # print all keys, but only the first 70 chars
    #for key in audio.keys():
    #    print ("%s => %s"%(key,audio[key]))[:70]

    getTag(song,audio,EnumSong.ALBUM ,"\xA9alb")
    getTag(song,audio,EnumSong.ARTIST,"\xA9ART")
    getTag(song,audio,EnumSong.TITLE ,"\xA9nam")
    getTag(song,audio,EnumSong.GENRE ,"\xA9gen")
    
    getTag_TupleOfInt(song,audio,EnumSong.SONGINDEX ,"trkn")

    song[EnumSong.LENGTH]  = int(audio.info.length)
    song[EnumSong.BITRATE] = int(audio.info.bitrate)

    #for i in range(len(song)):
    #    print "%d => %s"%(i,song[i]);
    
def id3_asf_createSongFromPath(song):

    audio = ASF(song[EnumSong.PATH])

    # print all keys, but only the first 70 chars

    #for key in audio.keys():
    #    print ("%s => %s"%(key,audio[key]))[:70]

    getTag(song,audio,EnumSong.ALBUM ,"WM/AlbumTitle")
    getTag(song,audio,EnumSong.ARTIST,"WM/AlbumArtist")
    getTag(song,audio,EnumSong.TITLE ,"Title")
    getTag(song,audio,EnumSong.GENRE ,"WM/Genre")
    
    getTag_int(song,audio,EnumSong.SONGINDEX ,"WM/TrackNumber")
    
    song[EnumSong.LENGTH]  = int(audio.info.length)
    song[EnumSong.BITRATE] = int(audio.info.bitrate)

    #for i in range(len(song)):
    #    print "%d => %s"%(i,song[i]);
    
def id3_flac_createSongFromPath(song):

    audio = FLAC(song[EnumSong.PATH])

    # print all keys, but only the first 70 chars

    #for key in audio.keys():
    #    print ("%s => %s"%(key,audio[key]))[:70]

    getTag(song,audio,EnumSong.ALBUM ,"album")
    getTag(song,audio,EnumSong.ARTIST,"artist")
    getTag(song,audio,EnumSong.TITLE ,"title")
    getTag(song,audio,EnumSong.GENRE ,"genre")
    
    getTag_int(song,audio,EnumSong.SONGINDEX ,"tracknumber")

    song[EnumSong.LENGTH]  = int(audio.info.length)
    song[EnumSong.BITRATE] = int(audio.info.sample_rate)

    #for i in range(len(song)):
    #    print "%d => %s"%(i,song[i]);

def id3_updateSongInfo( song ):
    
  
    test = id3_createSongFromPath(song[EnumSong.PATH])
    fext = fileGetExt(song[EnumSong.PATH]).lower()
    
    #r = False;
    r =      ( song[EnumSong.ARTIST]  == test[EnumSong.ARTIST] )
    r = r or ( song[EnumSong.TITLE]   == test[EnumSong.TITLE ] )
    r = r or ( song[EnumSong.ALBUM]   == test[EnumSong.ALBUM ] )
    r = r or ( song[EnumSong.LENGTH]  == test[EnumSong.LENGTH] )
    #
    # if at least one tag does not match update
    if r == False:
        try :
            if fext in ext_mp3:
                debug("Updateing Song - %s"%song);
                id3_mp3_updateSongInfo(song)
    #       if fext in ext_mp4:
    #           print "mp4 saving... %s"%song
    #       if fext in ext_asf:
    #           print "asf saving... %s"%song
    #       if fext in ext_flac:
    #           print "flac saving... %s"%song
        except Exception as e:
            debug(" *** ERROR - %s"%song);
            print "%s\n%s"%(song,e.args);
    return;
    
def id3_mp3_updateSongInfo( song ):
    #'artist'
    #'title' 
    #'album'
    #'length'
    #'genre'
    try :
        audio = EasyID3(song[EnumSong.PATH])

        audio['artist']  = song[EnumSong.ARTIST]
        audio['title']  = song[EnumSong.TITLE]
        audio['album']  = song[EnumSong.ALBUM]
        audio['length'] = convertTimeToString( song[EnumSong.LENGTH] )
        
        audio.save()

        
    
    except Exception as e:
        debug(" *** ERROR - %s"%song);
        print "%s\n%s"%(song,e.args);


    
def getTag(song,audio,key,tag):
    # set song[key] = audio[tag]
    if tag in audio:
        song[key] = unicode(audio[tag][0])
def getTag_int(song,audio,key,tag):
    # set song[key] = audio[tag]
    if tag in audio:
        song[key] = atoi(audio[tag][0])
def getTag_TupleOfInt(song,audio,key,tag):
    # MP4 stores to keys as a list-of tupples of ints
    # every key in an MP4 is returned as list of values
    # so that multiple values can be recorded for each key
    # for tracknumber, this list of values could contain
    # multiple tupples, where each tupple contains 
    #   (track, count of tracks in album)

    if tag in audio:    
        song[key] = atoi(audio[tag][0][0])
    
#from MpGlobalDefines import *

#from MpScripting import *  
#from MpSort import *
#from MpSearch import *
    
    