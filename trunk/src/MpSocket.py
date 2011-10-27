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

isPosix = os.name=="posix"

if not isPosix:
    from win32com.client import GetObject

class SystemPID(object):
    """
        object for using the current platform's PID
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
    def __init__(self,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", port))
        self.sock.settimeout(2.0);
        
    def send(self,msg):
        self.sock.send("Hello friend\n")
        try:
            msg = self.sock.recv(1024);
        except:
            msg = ""
        else:
            print msg # msg == "accept"
            
    def close():
        self.sock.close();
        
class LocalSocket_listen(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
        self.sock.bind( ('localhost',0) ) # bind a new socket, to a random unused port.
        self.sock.listen(5)               # set number of messages to queue.
        self.sock.settimeout(2.0);
        print "accept"
        self.conn, addr = self.sock.accept()
        print "conn"
        self.conn.setblocking(0)
        
        self.addr,self.port = self.sock.getsockname() # == 127.0.0.1 and a random port number
        print "Socket: %s - %d"%(self.addr,self.port)
        """
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind( ('localhost',0) )
            sock.listen(5)  
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
            msg = self.conn.recv(4096);
        except: 
            msg = "";
        else:
            self.conn.send("<accept>")
            
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
                sock.send(input+"\n")
                msg = sock.recv();
            
    else:
        # create copy one
        print "Creating Primary Socket"
        sock = LocalSocket_listen()
        print "NEW PORT: %d"%sock.getport() 
        session_create_lock( sock.getport() )
        
        msg = ""
        while msg != "quit":
            msg = sock.recv();
            if msg != "":
                print msg
            time.sleep(1)
else:
    # all the normal imports
    from MpGlobalDefines import *