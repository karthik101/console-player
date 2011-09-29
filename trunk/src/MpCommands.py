import sys
import os

isPosix = os.name == 'posix'

from PyQt4.QtCore import *
from PyQt4.QtGui import *

#import objgraph

from StringQuoter import StringQuote
from StringParser import StringParse  

CommandList = {};              
                
def initCommandList():
    global CommandList
    CommandList = {
              "test"      : cmd_test,
              "testbench" : cmd_testbench,
              "help"      : cmd_help,
              "play"      : cmd_play,
              "pause"     : cmd_pause,
              "playpause" : cmd_playpause,
              "mnext"     : cmd_mnext,
              "fnext"     : cmd_fnext,
              "next"      : cmd_next,
              "now"       : cmd_now,
              "prev"      : cmd_prev,
              "cont"      : cmd_cont,
              "stop"      : cmd_stop,
              "state"     : cmd_state,
              "volume"    : cmd_volume,
              "vol"       : cmd_volume,

              "append"   : cmd_append,
              "backup"   : cmd_backup,
              "build"    : cmd_build,
              "clear"    : cmd_clear,
              "export"   : cmd_export,
              "find"     : cmd_find,
              "hash"     : cmd_hash,
              "keyhook"  : cmd_keyhook,
              "libsave"  : cmd_libsave,
              "libload"  : cmd_libload,
              "load"     : cmd_load, 
              "lut"      : cmd_lut,
              "plsave"   : cmd_plsave,
              "plload"   : cmd_plload,
              "save"     : cmd_save,
              "settings" : cmd_settings,
              "setsave"  : cmd_setsave,
              "setload"  : cmd_setload,
              "stat"     : cmd_stat,
              "ss"       : cmd_ss,
              "sync"     : cmd_sync,
              "theme"    : cmd_theme,
              "undo"     : cmd_undo,
              "verify"   : cmd_verify,
              "log"      : cmd_log,

              "xx"       : cmd_xx,
              "eval"     : cmd_eval,
              "exec"     : cmd_exec,
              "repl"     : cmd_repl,
              "repack"   : cmd_repack,
              "import"   : cmd_import,
              "print"    : cmd_print,
              "diag"     : cmd_diag,
              "playlist" : cmd_playlist,
              "new"      : cmd_new,
              "."        : cmd_new,
              "insert"   : cmd_insert,
              "remove"   : cmd_remove,
              }; 

def processTextInput(string):
    """
        Commands
        
        \\<font size="3" color=#FF0000\\> As of Version 0.3.4 All commands can be accessed from a context menu or from the settings.\\</font\\>
        
        Commands provide a very wuick way to manipulate the library.
        
        in general, you will only ever use two: find and new
        
        with find, you can enter a valid search to select music and add it to the play list pool.
        
        with new, you can build a new playlist from the selection pool.
        
        Quick Playlist:
            type just a number, 0 - 9, to quickly make a playlist using the indicated preset.
        
    """
    input = StringParse(string)
    switch = input.command.lower()
    value = COMMAND.UNKNOWN
    
    if switch in CommandList and len(switch) > 0:
        value = CommandList[switch](input)
        
    elif input.default=="" and MpGlobal.INPUT_PLAY_GOTO_ZERO :
        startNewPlaylist(True)
        
    elif input.number != None:
        # when user types just a number, assume it is for a quick playlist
        if input.number < 10:
            selectByNumber(input.number)
            if MpGlobal.Player.selCount > 0:
                createPlayList(MpGlobal.PLAYLIST_SIZE,clrsel = False)
                MpGlobal.INPUT_PLAY_GOTO_ZERO = True
                
    elif input.default=="":
        MpGlobal.Player.play()
    # else: finally disabled 2011-08-24 after written day 1, 2010-01-22, this is a sad day
    #     count = searchSetSelection(input.default)
    #     debug( "Search Found: %d"%count )
    
    if not isPosix:
        setFeedBackColor(value)

def processSwitch_playlist(switch):
    """
        commands in the command line follow some common patterns
        this function sets all variables associated with creating a new playlist
        from the command switches.
        
        -h (int) : hash size 
        -n (int) : set selection by number
        -t (None): no songs from today
        -s (int) : playlist size
        
    """
    if "a" in switch:
        try :
        
            MpGlobal.Player.selCount = len(Global.Player.library)   
            
            for song in MpGlobal.Player.library:

                    song[MpMusic.SELECTED] = True
                    
            UpdateStatusWidget(0,MpGlobal.Player.selCount) 
            
        except:
            pass  
            
    if "h" in switch:
        try :
            MpGlobal.PLAYLIST_ARTIST_HASH_SIZE = int(switch["h"])
            debug("Hash: %d"%MpGlobal.PLAYLIST_ARTIST_HASH_SIZE )
        except:
            pass
    
    if "s" in switch:
        try :
            MpGlobal.PLAYLIST_SIZE = int(switch["s"])
        except:
            pass  
            
    if "t" in switch:
        try :
            MpGlobal.PLAYLIST_SKIP_RECENT = True
        except:
            pass   
            
    if "n" in switch:
        try :
            num = int(switch["n"])
            
            selectByNumber(num)
        except:
            pass    
  
    if "f" in switch:   
        try :
            searchSetSelection(switch["f"])
        except:
            pass 

def printHelp(input):
    cmd = "";
    if input.hasStrVal:
        cmd = input.StrVal[0].lower();
    

    debugRetail("Console Player Help\n")

    if cmd == "":
        MpGlobal.Window.debugMsg("Command List:")

        global CommandList
        k = lambda x: x[0]
        S = sorted(CommandList.items(), key = k)
        R = []
        for name,fptr in S :
            R.append(name)

        size = int((len(R)/6) + 1 )
        line= [""]*(size)
        string = "";
        for i in range(len(R)):
            line[i%size] += " | %-9s "%R[i];
        for text in line:
            debug(text)
    else:
        if cmd in CommandList:
            doc= ReadableDocs(CommandList[cmd])
            debug( doc )
    
    debug("\n > Type 'help command' for help on that command");

    #txt = MpGlobal.Window.txt_debug
        # move the cursor to the end of the text buffer
    #txt.moveCursor(QTextCursor.Start,QTextCursor.MoveAnchor)
    return
    
def setFeedBackColor(value):
    #value as ENUM COMMAND
    time = 2;

    D = MpGlobal.Window.style_dict

    if value in D:

        setConsoleColor(D[value],time)
    #else:    
    #    
    #    setConsoleColor(D["prompt_error"],time)
    return;

#----------------------------------------------------------------- 
# Commands   
#----------------------------------------------------------------- 

#----------------------------------------------------------------- 
# test  

def cmd_test(input):
    """
        DEV
        Command: test
        Usage: test <str> 

        prints diag info for the command interface
    """
    # test the command line input 
    # current implementation, size of StrVal, or hasStrVal
    # is the only way to check how many arguments were supplied
    input.debug()
def cmd_help(input):
    """
        DEV
        Command: PLAY
        Usage: play

        prints help to the debug window
    """
    
    printHelp(input);
def cmd_testbench(input):
    """
        DEV
        Command: TESTBENCH
        Usage: testbench 

        Run regression test on certain features
        
        Tests the search feature.
        
    """
    lib = testbench_build_library();
    
    print "%d songs found in test library"%(len(lib))
    
    for song in lib:
        print "%s - %s : %4d %2d %s"%(song[MpMusic.ARTIST],song[MpMusic.TITLE],song[MpMusic.LENGTH],song[MpMusic.RATING],song[MpMusic.DATESTAMP]);
        
    testbench_search(lib)

    
#----------------------------------------------------------------- 
# Player Specific
       
def cmd_play(input):
    """
        Command: PLAY
        Usage: play

        play the current song
    """
    MpGlobal.Player.play()
    return COMMAND.VALID
def cmd_pause(input):
    """
        Command: PAUSE
        Usage: pause 

        pause the current song.
    """
    MpGlobal.Player.pause()
    return COMMAND.VALID
def cmd_playpause(input):
    """
        Command: PLAYPAUSE
        Usage: playpause 

        toggle play/pause on the current song.
    """
    MpGlobal.Player.playPause()
    return COMMAND.VALID
def cmd_mnext(input):
    """
        DEV
        Command: MNEXT
        Usage: mnext 

        go to the next song.
        
        skipcount will be incremented.
    """
    MpGlobal.Player.manualNext()
    return COMMAND.VALID
def cmd_fnext(input):
    """
        DEV
        Command: FNEXT
        Usage: fnext 

        go to the next song.
        
        playcount or skipcount will be incremented.
    """
    MpGlobal.Player.fadeNext()
def cmd_next(input):
    """
        Command: NEXT
        Usage: next [str]
        
        This is a dual use command
        if no string is provided playback of the current song ends, and continues with the next song in the playlist.
        
        If a string is provided, a matching song is searched for in the library, and then placed after the current playing song.
        
        No playcount or skipcount is incremented.
    """
    if input.string == "":
        MpGlobal.Player.next()
        return COMMAND.VALID
    else:
        so = SearchObject(input.string);
        R = so.search(MpGlobal.Player.library);
        
        if len(R) > 0:
            insertIntoPlayList([R[0],],MpGlobal.Player.CurrentIndex+1)
            return COMMAND.VALID
        else:
            return COMMAND.ERROR
def cmd_now(input):
    """
        DEV
        Command: NOW
        Usage: now
        
        print the current playing song to the debug window
    """
    if (MpGlobal.Player.CurrentSong != None):
        print "%s - %d/%d"%(MpGlobal.Player.CurrentSong,MpGlobal.Player.getTime(),MpGlobal.Player.CurrentSong[MpMusic.LENGTH])
    else:
        print "No Song to Play"
def cmd_prev(input):
    """
        Command: PREV
        Usage: prev
        
        Stop playback of the current song, start playing the previous song in the playlist.
        
        no skip count or playcount is recorded
    """
    MpGlobal.Player.prev()
    return COMMAND.VALID
def cmd_cont(input):
    """
        Command: CONT
        Usage: cont
        
        This command, short for "CONTinue then stop", will continue playback of the current song, and playback will be PAUSED before the next song is loaded.
        
        In the play pause button, this command exists as the red globe, with ">|" as a symbol.
        
    """
    MpGlobal.Player.cont()
    return COMMAND.VALID
def cmd_stop(input):
    """
        Command: STOP
        Usage: stop
        
        Stops playback.
        
        The current song will be unloaded from memory.
        
        Note that it is intentional, that there is no other way to call this
        It is suggested to use CONT instead.
        
    """
    MpGlobal.Player.stop()
    return COMMAND.VALID
def cmd_state(input):
    """
        DEV
        Command: STATE
        Usage: state
        
        display a human readable string containing the current playback state.
    """
    string = ("NOTHINGSPECIAL","OPENING","BUFFERING","PLAYING", \
        "PAUSED", "STOPPED", "ENDED", "ERROR", "UNKOWN")[MpGlobal.Player.mp.mediaState()];
    debugRetail ( "Current State: %s"%string );
    return COMMAND.VALID
def cmd_volume(input):
    """
        Command: VOLUME
        Alias:   vol
        Usage: volume [#]
        
        Set the playback volume
        No Parameter displays the current volume.
        
        volume is displayed on the status bar. 
    """
    if 0 <= input.DecVal[0] <= 100 and input.hasDecVal:
        MpGlobal.Player.setVolume(input.DecVal[0])
        MpGlobal.Window.volumeBar.setValue(input.DecVal[0])
        
    debugRetail( "Volume: %d"%Settings.PLAYER_VOLUME )
    return COMMAND.VALID

#----------------------------------------------------------------- 
# PlayList/Library   

def cmd_append(input):
    # provides the ability of a default search
    """
        DEV 
        undocumented
    """
    if input.hasStrVal:
        
        if input.StrVal[0] == "":
            MpGlobal.SEARCH_AUTOAPPEND = ""
        else:
            MpGlobal.SEARCH_AUTOAPPEND = ";"+input.StrVal[0]
        return COMMAND.VALID
    else:
        MpGlobal.SEARCH_AUTOAPPEND = "; .path !\"/japanese\""
        return COMMAND.SPECIAL
def cmd_backup(input):
    """
        Command: BACKUP
        Usage: backup [-enable|-disable]
        
        Force save a new back up tagged with todays date to:
            ./InstallPath/backup
            
        If a backup has been saved already today it will be updated.    
           
        Note that saving of backups is turned off by default. It can be enabled in the settings.
        
        Alternatively to enable:
            backup -enable
        To Disable:
            backup -disable
            
    """
    if input.hasStrVal == 1:
        if input.StrVal[0] == '-enable':
            Settings.SAVE_BACKUP = True
        if input.StrVal[0] == '-disable':
            Settings.SAVE_BACKUP = False
        debug("Backup Setting set to: %s"%Settings.SAVE_BACKUP);
    else:    
        musicBackup(True); # that was easy  
def cmd_build(input):
    """
        Command: BUILD
        Usage: build [#]
        
        rebuilds the quick select list of artists, ignoring artists that have less than # songs.
    """
    if input.hasDecVal :
        buildArtistList(input.DecVal[0])
    else:
        buildArtistList()
    return COMMAND.VALID
def cmd_clear(input):   
    """
        Command: CLEAR
        Usage: clear [all]

        Remove all songs from the selection pool.
        
        clear internal state variables
        
    """
    clearSelection()
    MpGlobal.INPUT_PLAY_GOTO_ZERO = False
    MpGlobal.PLAYLIST_ARTIST_HASH_SIZE = 0
    MpGlobal.Window.txt_main.clearHistory()
    if input.hasStrVal:
        if input.StrVal[0] == 'all':
            MpGlobal.Window.debugClear();
    return COMMAND.VALID
def cmd_export(input):
    """
        DEV
        Command: EXPORT
        Usage: export
        
        undocumented

    """
    for song in MpGlobal.Window.tbl_library.data:
        if 'l' in input.Switch:
            debug("--")
        else:
            debug("%s %d %s #%s - %s"%( \
                song.id, \
                MpMusic.DATESTAMP, \
                song[MpMusic.DATESTAMP], \
                song[MpMusic.ARTIST], \
                song[MpMusic.TITLE]))
    return COMMAND.VALID
def cmd_find(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        Command: FIND
        Usage: find <str>
        
        This command is the inverse of remove.
        
        The entered string is use to find songs. Any matching song will be added to the selection pool
        
        See the help file on searching to see how to format a search string.
    """
    count = searchSetSelection(input.string,True)
    
    debug( "Search Found: %d"%count )
    
    if count > 0:
        return COMMAND.VALID
    else:
        return COMMAND.ERROR
def cmd_hash(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """ 
        Command: HASH
        Usage: hash #
        
        Set the maximum number of songs per artist to use when the next playlist is created.
    """
    MpGlobal.PLAYLIST_ARTIST_HASH_SIZE = input.DecVal[0]
    fromGuiSetSelection()
    if MpGlobal.Player.selCount > 0:
        createPlayList(MpGlobal.PLAYLIST_SIZE,clrsel = False)
        return COMMAND.VALID
    return COMMAND.ERROR
def cmd_load(input):
    """
        Command: LOAD
        Usage: load

        reload the library and current playlist
        
    """

    # reload the library
    if os.path.exists(MpGlobal.FILEPATH_LIBRARY):
        MpGlobal.Player.library = musicLoad(MpGlobal.FILEPATH_LIBRARY);
        print  "Found %d Songs."%len(MpGlobal.Player.library)
        # trash playlist editors
        # TODO CLOSE ALL PL EDITORS
        # reload playlist
        processTextInput('plload')
        # update tables
        MpGlobal.Window.tbl_library.UpdateTable(0,MpGlobal.Player.library)
    
    #reload the playlist
    fname = MpGlobal.FILEPATH_PLAYLIST_CURRENT
    MpGlobal.Player.playList = playListLoad(fname,MpGlobal.Player.library)
    MpGlobal.Window.tbl_playlist.UpdateTable(0,MpGlobal.Player.playList)

    MpGlobal.Player.loadSong( Settings.PLAYER_LAST_INDEX );
    
    loadSettings()
    
def cmd_lut(input):
    """
        DEV
        Command: lut
        Usage: lut jstr
        
        where jstr is katakana or hiragana
        
        displays phonetic equivalent of jstr
    """
    t = Translate(input.string)
    debugRetail("Input Translates to: "+t.rstring)
    return COMMAND.VALID
def cmd_save(input):
    """
        Command: SAVE
        Usage: save

        save everything.
        
        This is done automatically each time the player is closed.
        command is provided for convenience only.
    """
    On_Close_Save_Data(True)
    return COMMAND.VALID
def cmd_stat(input):
    """
        Command: STAT
        Usage: stat

        display library statistics in the debug window
    """
    getStatistics()
    return COMMAND.VALID
def cmd_ss(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        DEV
        Command: SS
        Usage: ss [0/1 | on/off | true/false]

        Configure the screen saver service.
        
        Multiple options.
        
        0/1     Enable / Disable.
        on/off  Turn the screen saver on/off, 
                When off it will not turn on automatically after a set amount of time

        
        false/true default state of the screen saver, whether it was on or off
                   before opening the program.     
       
    """
    if input.hasDecVal:
        Settings.SCREENSAVER_ENABLE_CONTROL = (input.DecVal[0] == 1)

    o = MpGlobal.SSService
    r = "None"
    s = "None"
    if o != None:
        if input.hasStrVal == 1:
            if input.StrVal[0] == "off":
                o._set_SS_State(False)
            if input.StrVal[0] == "on":
                o._set_SS_State(True)
            if input.StrVal[0] == "true":
                o.originalState = True
            if input.StrVal[0] == "false":
                o.originalState = False
                
        r = o.getState()
        s = o.getInitialState()
        
    t = (Settings.SCREENSAVER_ENABLE_CONTROL,r,s)
    
    debugRetail("Screen Saver State: (Enabled {0,1},State {off,on},Default {false,true}): %s %s %s"%t)

    return COMMAND.VALID
def cmd_sync(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        DEV
        Command: SYNC
        Usage: sync
        
        Before using this command open an editable playlist.
        
        This command will open a dialog asking for a playlist to sync, and a folder to sync to.
        
        When the start button is pressed, the directory will be searched, songs not found in the playlist will be removed. All missing songs will then be copied over to the device.
       
        Files will be copied into the following folder structure
            <dir>\Artist\Album\filename
    """
        
    if len(MpGlobal.Window.editorTabs) > 0:
        MpGlobal.Window.syncDialogObj = dialogSync.SyncSongs(MpGlobal.Window);
        MpGlobal.Window.syncDialogObj.Renew()
        return COMMAND.VALID
    else:  
        print "Error Opening Sync Window"
        return COMMAND.ERROR
def cmd_theme(input):  
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        Command: THEME
        Usage: theme <theme name>
        
        Change the theme to the entered theme.
    """
    
    if MpGlobal.Window.setTheme(input.string):
        return COMMAND.VALID
    else:
        return COMMAND.ERROR
def cmd_undo(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        Command: UNDO
        usage: undo <type>
        
        Will reverse any action you wish to undo.
        Currently this is limited to undeleteing songs deleted in the current session
        
        \\<table\\>
        \\<b\\>Type\\</b\\>      |\\<b\\> Effect\\</b\\>
        delete    | any songs deleted this session will be restored to the library.
        \\</table\\>
        
        Examples:
            undo delete
           
    """
    if input.StrVal[0] == 'delete':
        for item in MpGlobal.Player.libDelete:
            MpGlobal.Player.library.append( item )
        debug("Restored %d songs."%len(MpGlobal.Player.libDelete) )
        MpGlobal.Player.libDelete = []   
        
    return COMMAND.VALID

def cmd_keyhook(input):
    """
        Command: KEYHOOK
        Usage: keyhook 0/1
        
        Enable/Disable the keyboard hook
       
        This allows you to use media keys to play/pause/stop music or go to next song, previous song
    """

    if (input.DecVal[0] == 1):
        initHook()
        debugRetail("KeyBoard Hook Enabled")
    else:
        disableHook()
        debugRetail("KeyBoard Hook Disabled")
    # debugRetail("KeyBoard Hook Disabled")
    return COMMAND.VALID

def cmd_verify(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        Command:  VERIFY
        Arguments: None
        Usage: verify
        
        This command extracts the files required for running the application. Missing files will be added, and files that already exist will be replaced.
    """
    verifyInstallation(MpGlobal.installPath);
    return COMMAND.VALID
def cmd_log(input):
    """
        Command: LOG
        Usage: log [str]
        
        save a copy of the debug window to a debug.log
        Optionally you can specify an alternative file name.
    """
    if input.hasStrVal:
        fname = "%s.log"%input.StrVal[0]
    else:
        fname = 'debug.log'
        
    wf = open(fname,"w"); 
    wf.write(MpGlobal.Window.txt_debug.toPlainText())
    wf.close()
    
def cmd_new(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        Command: NEW
        Alias:  .
        Arguments: -a,-f,-h,-n,-s,-t,-p
        Usage: new [-f <str>] [-n #] [-s #] [-t] [-a] [-p]
            note that arguments in square-brackets are optional.
            
        Create a new playlist. 
        The optional arguments combine features of several other functions.
        
        \\<table\\>
        \\<b\\>Argument\\</b\\>  | \\<b\\>Effect\\</b\\>
        -a        | Select all Music, default if NO arguments are given        
        -f  <str> | perform a search using the quoted string as the expression All matching songs will be selected                         
        -h  <num> | Limit the number of songs per artist in the playlist to the entered number                                         
        -n  <num> | Enter a number from 0-9, corresponding to a preset. A new playlist will be created from the numbered preset    
        -s  <num> | Enter a number 1-200. The created playlist will contain this number of songs    
        -t        | Remove all songs that were played today from the selection pool before the playlist is created                        
        -p        | After creation begin playback of the first song immediatley
        \\</table\\>
        
        \\<b\\>Examples:\\</b\\>
            
            new -s 30 -h 5 -t -p
                create a playlist with 30 songs, no more than 5 songs per artist
                and remove songs already played at least once today.
                the first song in the playlist will start playing immediatley.
    """
    # command switching:
    # -h : hash size
    # -s : size of playlist
    # -n : no songs from today
    # set the selection from the gui
    
    processSwitch_playlist(input.Switch)
    
    fromGuiSetSelection()
    
    if MpGlobal.Player.selCount == 0:
        for song in MpGlobal.Player.library:
            song[MpMusic.SELECTED] = True;
        MpGlobal.Player.selCount = len(MpGlobal.Player.library);
        UpdateStatusWidget(0,MpGlobal.Player.selCount)
        
    createPlayList(MpGlobal.PLAYLIST_SIZE,clrsel = False);
    
    if "p" in input.Switch:
        MpGlobal.Player.playSong(0)
    else:
        MpGlobal.INPUT_PLAY_GOTO_ZERO = True
    
    return COMMAND.VALID
def cmd_insert(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        Command: INSERT
        Arguments: -a,-f,-h,-n,-s,-t,-p
        Usage: new -s # [-f <str>] [-n #] [-t] [-a] [-p]
            note that arguments in square-brackets are optional.
            
        Insert a set of songs after the current playing song in the current playlist. Note that this command is similar to 'NEW'. The only difference is that the size parameter '-s' is required.
    
        Argument  | Effect   
        ----------|---------------------------------------------------------------------      
        -a        | Select all Music, default if NO arguments are given        
        -f  <str> | perform a search using the quoted string as the expression 
                  | All mathing songs will be selected                         
        -h  <num> | Limit the number of songs per artist in the playlist to    
                  | the entered number                                         
        -n  <num> | Enter a number from 0-9, corresponding to a preset.        
                  | A new playlist will be created from the numbered preset    
        -s  <num> | Enter a number 1-200.                                      
                  |  The created playlist will contain this number of songs    
        -t        | Remove all songs that were played today from the selection 
                  | pool before the playlist is created                        
        -p        | After creation begin playback of the first song immediatley

        Example:
            insert -s 15 -n 0
                insert 15 songs from preset 0
    
    """
    processSwitch_playlist(input.Switch)
        
    fromGuiSetSelection()
    
    insertSelectionIntoPlayList(MpGlobal.PLAYLIST_SIZE,MpGlobal.Player.CurrentIndex+1, "r" in input.Switch)
    MpGlobal.PLAYLIST_SIZE = Settings.PLAYLIST_SIZE_DEFAULT
    return COMMAND.VALID
def cmd_remove(input):
    # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        Command: REMOVE
        Usage: remove <str>
        
        This command is the inverse of find.
        
        The entered string is use to find songs. Any matching song will be removed from the selection pool
    """
    count = searchSetSelection(input.string,False)
    
    debug( "Search Removed: %d"%count )
    if count > 0:
        return COMMAND.VALID
    else:
        return COMMAND.ERROR

#----------------------------------------------------------------- 
# DEV   
    
def cmd_xx(input):
        # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        DEV
        Command: XX
        Usage: xx #
        
        undocumented
    """
    #temp = StringParse("Hello lost")
    #debug (temp.StrVal)
    #MpGlobal.Window.txt_debug.hide()

    if input.DecVal[0] == 1 : #xx 1
        #UpdateStatusWidget(0,"woah")
        #getStatistics()
        print RunTime_List_Operation_Int(MpGlobal.Player.libDisplay,input.DecVal[1])
        
    if input.DecVal[0] == 2 : #xx 2
        temp = Song()
        temp[MpMusic.ARTIST] = "Stone Temple Pilots"
        temp[MpMusic.ALBUM]  = "Core"
        temp[MpMusic.TITLE]  = "Crackerman"
        temp[MpMusic.LENGTH] = 194
        temp.update()
        
        print temp

    if input.DecVal[0] == 3 : #xx 3
        #MpGlobal.Window.setWindowFlags(MpGlobal.Window.windowFlags() | Qt.WindowStaysOnTopHint)
        #MpGlobal.Window.setWindowFlags(Qt.WindowStaysOnTopHint)
        print convertStringToTime("90")
        print convertStringToTime("1:30")
        print convertStringToTime("1:1:1")
        print convertStringToTime("1:1:1:1")

    if input.DecVal[0] == 4 : #xx 4
        path = r"C:\Users\Nick\Downloads\torrent\000 Music\Semisonic\All About Chemistry\01 Chemistry.wma"
        #path = r"C:\Users\Nick\Downloads\torrent\000 Music\Mark Lanegan\(1990) The Winding Sheet\01-Mockingbirds.flac"
        if os.path.exists(path):
            print "testing id3..."
            song = id3_createSongFromPath(path)
        
    if input.DecVal[0] == 5 : #xx 5
        string =  "2010/10/08 11:52"
        print getEpochTime(string)
        print getCurrentTime()
        print getNewDate()  
    
    if input.DecVal[0] == 6 : #xx 6
        string = '$art-$tit-$alb::$id'
        debug (MpMusic.expandExifMacro(string,'$',MpGlobal.Player.libDisplay[0]) )

    if input.DecVal[0] == 7 : #xx 7
        s = "Time: %d"%getSecondsFromDateFormat(input.StrVal[1],input.DecVal[2])
        debug (s)
    
    if input.DecVal[0] == 8 : #xx 8
        test = Translate(u"::sutereoponi-\u30B0")
        debug( "o: %s"%test.ostring )
        debug( "n: %s"%test.nstring )
        debug( "r: %s"%test.rstring )
        debug( test.position )
    
    if input.DecVal[0] == 9 : #xx 9
        RetailMessage("Sample Display Message")
       
    
    if input.DecVal[0] == 10 : #xx 10
        

        #test = Song("./user/test.mp3")
        #test[MpMusic.ARTIST] = "Test Artist"
        #test[MpMusic.TITLE] = "Test TITLE"
        #test[MpMusic.ALBUM] = "Test ALBUM"
        #id3_updateSongInfo(test)
        for song in MpGlobal.Player.library:
            id3_updateSongInfo(song)
            MpGlobal.Application.processEvents();
        debug("Done.");
    if input.DecVal[0] == 11 : #xx 11   
        h = helpDialog();
        h.show();
     
    if input.DecVal[0] == 12 : #xx 11   
        open_dialog_About()
        
    if input.DecVal[0] == 20: #xx 20
        if (input.hasStrVal == 3):
            MpTest.systest1(input.DecVal[1],str(input.StrVal[2]))
             
        MpGlobal.Window.txt_main.history = MpGlobal.Window.txt_main.history[1:]    
        
    if input.DecVal[0] == 21: #xx 21
    
        if (input.hasStrVal != 2):
            input.DecVal[1] = -1;

        MpTest.systest2(input.DecVal[1])
        
        MpGlobal.Window.txt_main.history = MpGlobal.Window.txt_main.history[1:]  
        
    if input.DecVal[0] == 81 : #xx 81
        for song in MpGlobal.Player.library:
            song[MpMusic.FILESIZE] = fileGetSize(song[MpMusic.PATH])
            
    if input.DecVal[0] == 99 : #xx 81
        for song in MpGlobal.Player.library:
            song.md5 = get_md5(song[MpMusic.PATH])        
            debug( "%s - %s"%(song.md5,song) )
            MpGlobal.Application.processEvents()
          
def cmd_eval(input):
        # ##----1----2----3----4----5----6----7----8----9----0----1----2----3----4----5----6
    """
        DEV
        Command: EVAL
        Usage: eval <str>
        
        evaluate and print the entered str.
        
        enter a variable name to see its contents
        
        see PRINT
    """
    try:
        local = { \
            "p":MpGlobal.Player, \
            "w":MpGlobal.Window, \
            "g":MpGlobal, \
            "lib":MpGlobal.Player.library, \
            "pl":MpGlobal.Player.playList \
            
            }
        result = unicode( eval(unicode(input.string),globals(), local) )
        debug( result  )
    except Exception as e:
        debug( "%s = "%unicode(input.string))
        debug("EVAL ERROR: %s"%e.args)
def cmd_exec(input):
    """
        DEV
        Command: EXEC
        Usage: exec <str>
        
        execute a line of python code.
        
        see IMPORT
    """
    debug( str(input.string))
    try:
        local = { \
            "p":MpGlobal.Player, \
            "w":MpGlobal.Window, \
            "g":MpGlobal, \
            "lib":MpGlobal.Player.library, \
            "pl":MpGlobal.Player.playList \
            
            }
            
        exec (str(input.string),globals(), local)

    except Exception as e:
        #debug("EXEC ERROR: %s"%e.args)
        print e.args
def cmd_repl(input):
    """
        DEV
        Command: REPL
        Usage: repl 

        This is an abuse of all things holy and good.
        
        the text debug window is now a python editor/interpretor.
        
        executes the code found in the debug window.
        save a copy of the debug log to a debug.log
        
        
    """
    text = MpGlobal.Window.txt_debug.toPlainText()
    l = "-"*80
    i = text.find('-----')
    
    if i > 0:
        text = text[:i].strip()
    text = text.replace('\t','    ')    
    try:
        MpGlobal.Window.txt_debug.setPlainText(text);
        debug( "\n%s\nREPL ignores anything after (and including) this line\n"%l)
        
        exec (text)
    except Exception as e:
        for i in e:
            debug("%s"%str(i))
def cmd_repack(input):
    """
        DEV
        Command: REPACK
        Usage: repack [1/0]
        
        move the command input line edit to the bottom of debug
        
        a value of zero moves it back
        
        the debug text window becomes editable. you can now use REPL
    """
    if input.DecVal[0]==1:
        MpGlobal.Window.spt_left.addWidget(MpGlobal.Window.txt_main)
        MpGlobal.Window.txt_debug.setReadOnly(False);
    else:
        MpGlobal.Window.vbox_playlist.insertWidget(0,MpGlobal.Window.txt_main)
        MpGlobal.Window.txt_debug.setReadOnly(True);
   
def cmd_import(input):
    """
        DEV
        Command: IMPORT
        usage: import <module>
        
        Imports the given python module found in the same folder as the executable
        Use as a way of importing extensions
        importing a second time will reload the module, if an 'unload' method is defined it will be executed before reloading.
    """
    fname = input.StrVal[0]
    
    
    if os.path.exists("./%s.py"%fname):
        try:
            
            #debug( "importing %s..."%(fname) )
            
            local = { \
                        "p":MpGlobal.Player, \
                        "w":MpGlobal.Window, \
                        "g":MpGlobal, \
                        "lib":MpGlobal.Player.library, \
                        "pl":MpGlobal.Player.playList \
                        
                        }
                        
            test = "MpGlobal.Mp_%s != None"%fname
            result = False;
            try:
                result = eval(test)
            except:
                pass
                
            if result: # module already exists
                debug( "Reloading MpGlobal.Mp_%s"%fname )
                string = "temp = MpGlobal.Mp_%s.unload();\nif temp:\n    reload(MpGlobal.Mp_%s);\nelse:\n    debug('error..');"%(fname,fname)
                
                exec (string,globals(), local)
            else:    
                string = "MpGlobal.Mp_%s = __import__(\"%s\")"%(fname,fname)
                debug(string)
                exec (string,globals(), local)
                
        except Exception as e:
            print e.args
        else:
            debug( "Module bound to MpGlobal.Mp_%s"%fname )
    else:
        debug( "No Module named %s found"%fname )
        
def cmd_print(input):
    """
        DEV
        Command: PRINT
        Usage: print <str>
        
        evaluate and print the entered str.
        
        enter a variable name to see its contents
        
        see EVAL
    """
    input.string  = "debug(" + input.string + ")"
        
    try:
        local = { \
            "p":MpGlobal.Player, \
            "w":MpGlobal.Window, \
            "g":MpGlobal, \
            "lib":MpGlobal.Player.library, \
            "pl":MpGlobal.Player.playList \
            
            }
            
        exec ( input.string,globals(), local)

    except Exception as e:
        debug( input.string )
        debug("EXEC ERROR: %s"%e.args)
def cmd_diag(input):
    """
        DEV
        Command: DIAG
        Usage: DIAG [#[,#[,#[,...]]]]
        
        toggle the numbered diagnostic.
        
        enter no number to see the current state of all diagnostics

    """
    for i in input.DecVal:
        if i == 1: MpGlobal.DIAG_PLAYBACK  = not MpGlobal.DIAG_PLAYBACK;
        if i == 2: MpGlobal.DIAG_KEYBOARD  = not MpGlobal.DIAG_KEYBOARD;
        if i == 3: MpGlobal.DIAG_SEARCH    = not MpGlobal.DIAG_SEARCH;
        if i == 4: MpGlobal.DIAG_SONGMATCH = not MpGlobal.DIAG_SONGMATCH;
    
    debug("------------------------");
    debug("1: DIAG_PLAYBACK : %s"%MpGlobal.DIAG_PLAYBACK);
    debug("2: DIAG_KEYBOARD : %s"%MpGlobal.DIAG_KEYBOARD);
    debug("3: DIAG_SEARCH   : %s"%MpGlobal.DIAG_SEARCH);
    debug("4: DIAG_SONGMATCH: %s"%MpGlobal.DIAG_SONGMATCH);
    debug('\n\n')
    
    
def cmd_playlist(input):
    """
        DEV
        Command: PLAYLIST
        Usage: playlist
        
        undocumented
    """
    if input.hasDecVal:
        i = input.DecVal[0]
        j = input.DecVal[1]
        k = input.DecVal[2] == 0
        createFromPlayList(MpGlobal.PLAYLIST_SIZE,index = i,shuffle = k,hash = j)
def cmd_libsave(input):
    """
        DEV
        Command: LIBSAVE
        Usage: libsave
        
        save the library to the current library location
        
        The library could be saved to one of 4 locations
        
        %APPDATA%/ConsolePlayer/ on Windows
        %HOME%/ConsolePlayer/ on Unix
        ./user/
        Or in a user defined location.
        
        the location and format is dependant on several settings.
    """
    type=0;
    musicSave(MpGlobal.FILEPATH_LIBRARY,MpGlobal.Player.library,Settings.SAVE_FORMAT);
    debug( len(MpGlobal.Player.library))
    return COMMAND.VALID
def cmd_libload(input):
    """
        DEV
        Command: LIBLOAD
        Usage: libload
        
        reload the library from the current library location
        
        The library could be found in one of 4 locations
        
        %APPDATA%/ConsolePlayer/ on Windows
        %HOME%/ConsolePlayer/ on Unix
        ./user/
        Or in a user defined location.
        
        the location and format is dependant on several settings.
        
    """
    if os.path.exists(MpGlobal.FILEPATH_LIBRARY):
        MpGlobal.Player.library = musicLoad(MpGlobal.FILEPATH_LIBRARY);
        print  "Found %d Songs."%len(MpGlobal.Player.library)
        # trash playlist editors
        # TODO CLOSE ALL PL EDITORS
        # reload playlist
        processTextInput('plload')
        # update tables
        MpGlobal.Window.tbl_library.UpdateTable(0,MpGlobal.Player.library)
    
        return COMMAND.VALID
        
    return COMMAND.ERROR 
    
def cmd_plsave(input):
    """
        DEV
        Command: PLSAVE
        Usage: plsave
        
        save the current playlist to the current playlist location
        
        The playlist could be saved to one of 4 locations
        
        %APPDATA%/ConsolePlayer/ on Windows
        %HOME%/ConsolePlayer/ on Unix
        ./user/
        Or in a user defined location.
        
        the location and format is dependant on several settings.
        
    """
    playListSave(MpGlobal.FILEPATH_PLAYLIST_CURRENT,MpGlobal.Player.playList,Settings.SAVE_FORMAT,MpGlobal.Player.CurrentIndex)
    return COMMAND.VALID
def cmd_plload(input):
    """
        DEV
        Command: PLLOAD
        Usage: plload [str]
        
        load current.playlist
        
        if [str] is specified an attempt will be ade  to load that list instead
    """
    fname = MpGlobal.FILEPATH_PLAYLIST_CURRENT
    if input.hasStrVal:
        
        test = os.path.join(MpGlobal.installPath,'playlist',input.StrVal[0]+'.playlist')
        if os.path.exists(test):
            fname = test

    MpGlobal.Player.playList = playListLoad(fname,MpGlobal.Player.library)
    MpGlobal.Window.tbl_playlist.UpdateTable(0,MpGlobal.Player.playList)

    MpGlobal.Player.loadSong( Settings.PLAYER_LAST_INDEX );
    
    print "load done"
    return COMMAND.VALID
def cmd_settings(input):
    """
        DEV
        COMMAND: SETTINGS
        Usage: settings
        
        opens the settings file

    """
    
    print MpGlobal.FILEPATH_SETTINGS
    
    os.startfile(MpGlobal.FILEPATH_SETTINGS)
    
def cmd_setsave(input):
    """
        DEV
        Command: SETSAVE
        Usage: setsave
        
        undocumented
    """
    #D = settings_To_Dictionary()
    saveSettings()
    return COMMAND.VALID
def cmd_setload(input):
    """
        DEV
        Command: SETLOAD
        Usage: setload
        
        load settings from settings.ini
    """
    loadSettings()
    return COMMAND.VALID
  

initCommandList()
   
# ###################################################################
# ###################################################################
#
# Imports
#
# ###################################################################
# ###################################################################          

from calendar import timegm
import os
import sys
import time
import datetime
import random
import re
import subprocess
import ctypes

from MpGlobalDefines import *
from MpFileAccess import *
from MpID3 import *
from UnicodeTranslate import Translate
from MpEventHook import initHook,disableHook
from dialogSettings import SettingsWindow
from dialogHelp import *
from MpScreenSaver import *
from MpFirstTime import verifyInstallation
from MpScripting import *      
from MpScriptingAdvanced import *      
import dialogSync       
     
StringParse.D_StrToDec = MpMusic.D_StrToDec     
#----------------------------------------------------------------- 
# Create the Global Dictionaries   



