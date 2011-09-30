from MpGlobalDefines import *
#from MpScripting import *
#from PyQt4.QtCore import *
import os
isPosix = os.name == 'posix'

if not isPosix:
    import pythoncom, pyHook
#else:
#    import mmkeys

HOOK_SET = False

def hook_event_Keyboard_Debug(event):
    print 'MessageName:',event.MessageName
    print 'Message:',event.Message
    print 'Time:',event.Time
    print 'Window:',event.Window
    print 'WindowName:',event.WindowName
    print 'Ascii:', event.Ascii, chr(event.Ascii)
    print 'Key:', event.Key
    print 'KeyID:', event.KeyID
    print 'ScanCode:', event.ScanCode
    print 'Extended:', event.Extended
    print 'Injected:', event.Injected
    print 'Alt', event.Alt
    print 'Transition', event.Transition
    print '---'
    # return true to allow the keypress to go thru
    # return false to prevent the key event from happening
    return True

def hook_event_KeyPress(event):
    
    #print event.KeyID
    
    if event.KeyID == Settings.KEYBOARD_PLAYPAUSE :
        MpGlobal.Player.playPause()
        return False
    elif event.KeyID == Settings.KEYBOARD_STOP :
        MpGlobal.Player.cont()
        return False
    elif event.KeyID == Settings.KEYBOARD_PREV :
        MpGlobal.Player.prev()
        return False
    elif event.KeyID == Settings.KEYBOARD_NEXT :
        MpGlobal.Player.fadeNext()
        return False
    elif MpGlobal.DIAG_KEYBOARD:
        if event.Ascii > 0x20 or event.Ascii == 0xD:#any char or \n
            MpGlobal.Window.debugMsg("%s"%chr(event.Ascii)),
        else:
            MpGlobal.Window.debugMsg("{%02X}"%event.KeyID)
        return True
    #elif event.KeyID == Settings.KEYBOARD_LAUNCHMEDIA :
    #    return True
    
    #elif event.KeyID == KEYBOARD_INSERT and Settings.DEVMODE: # insert
        #MpGlobal.Window.activateWindow()
        
    #    MpGlobal.Window.txt_main.setFocus()
    #    MpGlobal.Window.tabMain.setCurrentIndex(0)
    #    
    #   return False
        
    return True
    

if isPosix:
    def initHook():
        """
            initialize the ability of a keyboard hook
        """
        return False
else:
    def initHook():
        """
            Enable the keyboard hook if has not yet been enabled
            
        """
        
        global HOOK_SET
        
        if MpGlobal.HookManager == None:
            MpGlobal.HookManager = pyHook.HookManager();
            #MpGlobal.HookManager.KeyDown = hook_event_Keyboard_Debug
            MpGlobal.HookManager.KeyDown = hook_event_KeyPress
            MpGlobal.HookManager.HookKeyboard()
            HOOK_SET = True
        elif not HOOK_SET :
            MpGlobal.HookManager.HookKeyboard()
            HOOK_SET = True


if isPosix:
    def disableHook():
            return False        
else:
    def disableHook():
        """
            if the hook has been set temporarily disable it
            
        """
        
        global HOOK_SET 
        
        if MpGlobal.HookManager != None: 
            if HOOK_SET : 
                MpGlobal.HookManager.UnhookKeyboard()
                HOOK_SET = False
        
#MpGlobal.HookManager.KeyDown = hook_event_Keyboard_Debug

# possibly need this line
# if hooking does not occur, 
#    this will create a thread waiting for Hook Events
#pythoncom.PumpMessages()