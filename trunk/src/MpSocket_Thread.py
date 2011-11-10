# #########################################################
# #########################################################
# File: MpSocket_Thread
# Description:
#     an idle thread that waits for input on a port
# when a message is received it is processed the same way
# a command line argument would be processed.
# #########################################################

from App_SocketController import *

class LocalSocket_Thread(QThread):     

    def run(self):
    
        self.setPriority(QThread.LowestPriority);

        sock = LocalSocket_listen()
        
        print "creating session lock. PID: %d PORT: %d"%(SystemPID.getPID(),sock.getport())
        session_create_lock( port = sock.getport() )
        
        msg = ""
        
        while QThread:
            #print ">"
            msg = sock.recv();
            if msg != "":
                msg = msg.strip();
                size = msg[1:msg.find(']')]
                body = msg[msg.find(']')+1:]
                
                size = int(size)

                session_receive_argument(body);
                
                #print "Received: %s"%msg
                
            QThread.msleep(125);
            
        print "Socket Thread Ended Unexpectedly."
        
from MpGlobalDefines import *
from MpCommands import *
from MpScripting import session_receive_argument
                