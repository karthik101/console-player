
import os
isPosix = os.name == 'posix'

if not isPosix:
    import win32gui
    import win32con

if isPosix:
    class ScreenSaverService(object):
        originalState = False   # state when object was created
        currentState = False    # state after last change
        __error = False
            
        def enable(self):
            return False;
        def disable(self):
            return False;
        def Reset(self): 
            return False;
        def getState(self):
            return False;
        def getInitialState(self):
            return False;
        def _set_SS_State(self,newState):
            return False;
        def _get_SS_State(self):
            return False;
else:
    class ScreenSaverService(object):
        """
            Provides access to the win32 object that enables and disables the screen saver
            the state  when created is recorded so that the inital state can be returned to 
            later
        """
        originalState = False   # state when object was created
        currentState = False    # state after last change
        __error = False
        
        def __init__(self):
            #TODO return to original state?
            self.originalState = True;#self._get_SS_State()
            self.currentState  = self.originalState
            
        def enable(self):
            cstate = self._get_SS_State()
            #if cstate != self.currentState :
                # some how was changed externally to this object
            #    self.originalState = cstate
                
            self._set_SS_State(True)
            
            self.currentState = self._get_SS_State()
            
            return self.currentState
        
        def disable(self):       
            self._set_SS_State(False)
            
            # check to make sure the state change took
            self.currentState = self._get_SS_State()
            
            return self.currentState
            
        def Reset(self):
            """
                set the screen saver service to the value that
                was initially loaded when this object was created.
            """
            #if self.originalState != self.currentState:
            #    self._set_SS_State(self.originalState)
            #self.enable()
            self._set_SS_State(self.originalState)
            
        def getState(self):
            """
                use this function when checking the current state of the
                screen saver service
            """
            return self._get_SS_State()#self.currentState
            
        def getInitialState(self):
            """
                Use this function when checking the inital state of the
                screen saver service
            """
            return self.originalState
            
        def _set_SS_State(self,newState):
            """
                Win32 function call to enabled/disable the screen saver
            """
            try:
                win32gui.SystemParametersInfo(win32con.SPI_SETSCREENSAVEACTIVE,newState,win32con.SPIF_UPDATEINIFILE)
            except:
                self.__error = True
        def _get_SS_State(self):
            """
                Win32 Function call to read the whether the Screen saver is enabled or disabled
            """
            try :
                state = win32gui.SystemParametersInfo(win32con.SPI_GETSCREENSAVEACTIVE)
                return state
            except:
                self.__error = True
                return False
