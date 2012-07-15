# #########################################################
# #########################################################
# File: MpApplication
# Description:
#       EventManager provides a way of delaying function calls
#   and moving the call to a separate thread of execution.
#   call postEvent with the function you want, then all of
#   the arguments needed. The EventManager's thread
#   will then deal with the data
#
#   A word of caution, if you pass a list the original calling
#   thread can change the data before the EventManager's thread
#   can get arround to processing. be sure to pass a copy
#   if you are worried about this.
#
#   this Module can be used in any application, even if
#   it does not use Qt for anything Else. Qt is required to
#   be installed.
#
#   Warning: A QWidget can not be updated except from it's
#   parent thread. Therefore the EventManager can do
#   the processing, but any updates need to be kicked
#   backed to the main thread somehow.
#   Note on Warning, i have been able to update QWidgets
#   research is required as i got Qpainter errors in the past.
#
# #########################################################

import Queue
from PyQt4.QtCore import *


class Event(object):
    """
        Base type for an "event"
        an event consists of a function to call.
        and a tuple of the arguments to use when calling the event.
    """
    def __init__(self,fptr,args):
        self.fptr=fptr; # pointer to function to call
        self.args=args; # as tuple of arguments for function pointer

class EventManager(QThread):

    def __init__(self,parent=None):
        super(EventManager, self).__init__(parent)
        self.eventQueue = Queue.Queue() # Queue of events to run
        self.eventDict  = {};           # dictionary of events to run when eventQueue is Empty
        
    def start(self,priority=QThread.LowPriority):
        super(EventManager, self).start(priority)    
        
    def postEvent(self,fptr,*args):
        """
            Add a new event to the Queue, then restart the Thread if needed
            An Event is a function and a tuple or arguments for the function
            stored in the variable *args.
            
            Use this function to kick a function call to a separate thread
            if its result is not important for the calling thread.
        """
        self.eventQueue.put( Event(fptr,args) )
        
        if not self.isRunning():    # restart the thread if it is no longer running
            self.start();
    
    def postEndEvent(self,fptr,*args):
        """
            Set a new function to be called when the eventQueue is empty
            
            By using a dict only one copy of each function can be added.
            
            Use this to have code run after other posted events. for example
            a clean-up script.
        """
        self.eventDict[fptr] = args;
    
    def force_clear(self):
        """ remove all events from the queue
        """
    
    def run(self):

        while self.eventQueue.qsize() > 0 :
            # get the oldest event from the Queue
            e = self.eventQueue.get()
            # process the event.
            e.fptr(*e.args);    # unpack the argument tuple when calling.
        
        for fptr,args in self.eventDict.items():
            fptr(*args)
            del self.eventDict[fptr] # remove the posted event 

if __name__ == "__main__":

    """
        Example of using the Event Manager
        
        Run this code, type in messages to have printed later
        
        type 'post' to print all queued messages.
        type 'quit' to quit'
        
    """
    def printer(input): 
        # printer function prints a atring then waits for a quarter of a second.
        print ">> %s"%input
        QThread.msleep(250);  
        
    em = EventManager();

    inputList = []  # list of stored inputs, waiting to e posted with 'post'
    
    input = raw_input(":");
    
    while input!="quit":
    
        if input == "post":
            for x in inputList:
                em.postEvent(printer,x);
            QThread.msleep(len(inputList)*250 + 500);   # wait for the messages to print back
            inputList = []
        else:
            inputList.append(input);
            
        input = raw_input(":");