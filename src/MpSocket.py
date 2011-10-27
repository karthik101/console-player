# #########################################################
# #########################################################
# File: MpSocket
# Description:
#  Implement a Session lock using a text file and os.getpid()
#  Use a socket to communicate between 
# #########################################################


# the session lock should save to ~/session.lock
# it should save the current process id on the first line
# and the current listning port on the second line.

# a message consists of:
# the word "COMMAND:"
# followed by a valid command.
# everything following the colon is of the same format as would be typed in the console.

import os
import sys
import socket

from PyQt4.QtCore import *

isPosix = os.name=="posix"

if not isPosix:
    from win32com.client import GetObject

class SystemPID(object):
    """
        wrapper object for using the current platform's PID
        
        provides three methods
        getPID - returns the current PID
        getPIDlist - returns a list of PID,NAME for all running processes, volatile
        check_pid_isActive - checks a pid against getPIDlist, returns true if it exists and is of the sae executable type
    """
    @staticmethod
    def getPID():
        return os.getpid();
        
    if isPosix:    
        @staticmethod
        def getPIDlist():
            """
                Return the list of process ID's available
                
                this function returns a list of tuples.
                each tuple contains:
                    (pid,name)
            """
            s=lambda s: s[:s.find("\x00")]
            
            R = [];
            pids= [int(pid) for pid in os.listdir('/proc') if pid.isdigit()]
            
            for pid in pids:
                proc = proc
                cmd = s(open("/proc/%d/cmdline"%pid,"r").read())
                cmd = cmd[cmd.rfind("/")+1:]
                # cmd is now the name of an executable, 
                R.append( (pid,cmd) );
            return R;
    else:
        @staticmethod
        def getPIDlist():
            """
                Return the list of process ID's available
                
                this function returns a list of tuples.
                each tuple contains:
                    (pid,name)
            """
            WMI = GetObject('winmgmts:')
            processes = WMI.InstancesOf('Win32_Process')
            process_list = [(p.Properties_("ProcessID").Value, p.Properties_("Name").Value) for p in processes]
            return process_list;
     
    @staticmethod     
    def check_pid_isActive(test_pid):
        """
            get the pid list.
            find all pid that match MY executable name
            
            test_pid is the pid we are looking to see if it is active
        """
        s = lambda s: s[s.rfind('/')+1:]
        myname = s(sys.executable.replace("\\",'/'))
        mypid = os.getpid();
        
        pidlist = SystemPID.getPIDlist();
        
        for pid,name in pidlist:
            if name == myname:
                if pid == test_pid:
                    return True;
        return False;
 
class LocalSocket_send(object):
    """
        provides a way of sending messages to a given port on localhost
    """
    def __init__(self,port):
        
        self.port = port;
        
    def send(self,msg):
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", self.port))
        package = "[%d]%s\n"%(len(msg)+1,msg)
        print self.sock.send(package), "bytes sent"
        
        #try:
        #    msg = self.sock.recv(1024);
        #except:
        #    msg = ""
        #else:
        #    # we could test msg here, if it is not <accept> the other side had an issue.
        #    pass
            
        self.sock.close();
        return 
        
class LocalSocket_listen(object):
    """
        create a listener object.
        
        use recv to see if there is a connection, and return data on that connection
    """
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
        self.sock.bind( ('localhost',0) ) # bind a new socket, to a random unused port.
        self.sock.listen(5)               # set number of messages to queue.
        self.addr,self.port = self.sock.getsockname() # == 127.0.0.1 and a random port number
        print "Socket: %s - %d"%(self.addr,self.port)
        self.sock.settimeout(0);
        
        """
            import socket; sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.bind( ('localhost',0) ); sock.listen(5); print sock.getsockname()
            con,add = sock.accept()
        """
        return
    def getport(self):
        return self.port
        
    def recv(self):
        """
            receive
            return any message text or an empty string. 
        """
        msg = "";
        try:

            conn, addr = self.sock.accept()
            conn.settimeout(0);
            #print conn;
            
        except:
            pass
        else:

            try: 
                msg = conn.recv(4096);
            except: 
                msg = "";
            else:
                pass
                #conn.send("<accept>\n")
            
            conn.close();
            #print "close"
        
        return msg;
        
    def close(self):
        #self.sock.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        self.sock.close()
    
def session_lock_exists():
    """
        return whether the contents of the current session lock are still valid
        
        return -1 when no current session can be found
        return the port number if the session exists.
    """
    lock_path = os.path.join(MpGlobal.installPath,"session.lock");
    
    
    if os.path.exists(lock_path):
        with open(lock_path,"r") as FILE:
            pid  = int(FILE.readline());
            port = int(FILE.readline());
        
        if SystemPID.check_pid_isActive(pid):
            return port
    
    
    return -1;
    
def session_create_lock(port=-1):

    lock_path = os.path.join(MpGlobal.installPath,"session.lock");
    
    with open(lock_path,"w") as FILE:
        FILE.write("%d\n"%SystemPID.getPID());
        FILE.write("%d\n"%port)
                   
if __name__ == "__main__":
    import time
    global MpGlobal
    
    class GlobalDummy(object):
        Socket = None
        installPath = "./"
     
          
    MpGlobal = GlobalDummy()

    
    class LocalSocket_Thread_test(QThread):     
    
        def run(self):
            self.setPriority(QThread.LowestPriority);
            print "Creating Primary Socket"
            sock = LocalSocket_listen()
            print "NEW PORT: %d"%sock.getport() 
            session_create_lock( sock.getport() )
            
            msg = ""
            while msg != "quit":
                #print ">"
                msg = sock.recv();
                if msg != "":
                    print msg.strip()
                    
                QThread.msleep(125);
                
    """
        Run two copies of this script
        the first will set up a socket for listening, and then create a session lock
        the second copy will then open, see the lock, and create a socket for sending.
        
        in copy two type messages and press enter to send them.
        the first copy will quit when the message it recieves is 'quit'
        the second copy will then close when it recieves '<accept>'
    """
    
    
    port = session_lock_exists();
    print "Session Lock Port: %d"%port
    if port >= 0:
        # create copy two
        print "Creating Secondary Socket"
        sock = LocalSocket_send(port);
        msg = ""
        while msg != "accept":
            input = raw_input("Send Message:");
            if input != "":
                sock.send(input)
                #msg = sock.recv();
            
    else:
        thread = LocalSocket_Thread_test();
        thread.start();
        x = raw_input();
        # create copy one
        
            #time.sleep(1/8)
else:
    # all the normal imports
    from MpGlobalDefines import *
    from MpCommands import *
    from MpScripting import session_receive_argument
    class LocalSocket_Thread(QThread):     
    
        def run(self):
        
            self.setPriority(QThread.LowestPriority);

            sock = LocalSocket_listen()
            
            print "creating session lock. PID: %d PORT: %d"%(SystemPID.getPID(),sock.getport())
            session_create_lock( sock.getport() )
            
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
                