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
#   if you are worried about it.
#
#   this Module can be used in any application, even if
#   it does not use Qt for anything Else.
#
#   Warning: A QWidget can not be updated except from it's
#   parent thread. Therefore the EventManager can do
#   the processing, but any updates need to be kicked
#   backed to the main thread somehow.
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
        self.eventQueue = Queue.Queue()
        
    def start(self,priority=QThread.LowPriority):
        super(EventManager, self).start(priority)    
        
    def postEvent(self,fptr,*args):
    
        self.eventQueue.put( Event(fptr,args) )
        
        if not self.isRunning():    # restart the thread if it is no longer running
            self.start();
        
    def run(self):

        while self.eventQueue.qsize() > 0 :
            # get the oldest event from the Queue
            e = self.eventQueue.get()
            # process the event.
            e.fptr(*e.args);    # unpack the argument tuple when calling.

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