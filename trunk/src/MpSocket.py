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

import os
import sys

isPosix = os.name=="posix"

if isPosix:
    from win32com.client import GetObject



from MpGlobalDefines import *

class SystemPID(object):
    """
        object for using the current platform's PID
    """
    def getPID():
        return os.getpid();
        
    if isPosix:    
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
            
    def check_pis_isActive(test_pid):
        """
            get the pid list.
            find all pid that match MY executable name
            
            test_pid is the pid we are looking to see if it is active
        """
        s = lambda s: s[s.rfind('/')+1:]
        myname = s(sys.executable.replace("\\",'/'))
        mypid = os.getpid();
        
        pidlist = getPIDlist();
        
        for pid,name in pidlist:
            if name == myname:
                if pid == test_pid:
                    return True;
        return False;
        
def session_lock_exists():
    """
        return whether the contents of the current session lock are still valid
        when they are return true, false otherwise
    """
    lock_path = os.path.join(MpGlobal.installPath,"session.lock");
    
    if os.path.exists(lock_path)
        with open(lock_path,"r") as FILE:
            pid  = FILE.readLine();
            port = File.readLine();
        
    
    
    return False;