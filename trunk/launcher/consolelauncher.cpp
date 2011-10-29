//Main.cpp
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include "Socket.h"

typedef struct session_t {
	int proc;
	int port;
	char * fname[256];
	char * fpath[1024];
} Session;

int get_session_lock(Session * s, const char * lockpath);
int IsProcessRunning(DWORD pid);

int main(int argc, char **argv)
{

	Session s;
	int success;
    char args[1024];//* args = (char *) malloc(1024);
    char msg[1024];//* msg  = (char *) malloc(1024); // todo why couldnt i reuse args
	

	ExpandEnvironmentStrings("%APPDATA%",msg,256);

	sprintf(msg,"%s\\ConsolePlayer\\session.lock",msg);
	
	
	printf("hey\r\n");
	success = get_session_lock(&s,".\\user\\session.lock");
	printf("hey\r\n");
	if (!success) {
		success = get_session_lock(&s,msg);
	}
	
	//return 0;
	
	if ( get_session_lock(&s,"D:\\Dropbox\\ConsolePlayer\\user\\session.lock") ) {
	
		//printf("%d\r\n",s.proc);
		//printf("%d\r\n",s.port);
		//printf("%s\r\n",s.fname);
		//printf("%s\r\n",s.fpath);
		
		if (IsProcessRunning(s.proc) && argc > 1) {
			
        
			// collect all arguments into a single string
			sprintf(args,"%s",argv[1]);			
			for (int i=2;i < argc;i++){
				sprintf(args,"%s %s",args,argv[i]);
			}
			// create the message to send
			sprintf(msg,"[%d]%s\r\n",strlen(args),args);
        
			// connect to the server and send the message.
			Socket sock;
			sock.ConnectToServer( "127.0.0.1", s.port );
			sock.SendData(msg);
			sock.CloseConnection();	
			
			exit(0);
			
		} else {
		
			ShellExecute(NULL, "open", (char *)(s.fpath), "", "c:\\", 0);
		
		}
		
		
		
	}
	
	ShellExecute(NULL, "open", "./ConsolePlayer.exe", "a b c d", "c:\\", 0);

}

int get_session_lock(Session * s, const char * lockpath) {
	/*
		return information from the session.lock file found at lockpath
	*/
	FILE * rf;
	
	rf = fopen(lockpath,"r");
	if (rf!=NULL) {
		fscanf(rf,"%d\r\n",&(s->proc));
		fscanf(rf,"%d\r\n",&(s->port));
		fscanf(rf,"%s\r\n",&(s->fname));
		fscanf(rf,"%s\r\n",&(s->fpath));
		fclose(rf);
		return 1;
	}
	return 0;
}


int IsProcessRunning(DWORD pid)
{
    HANDLE process = OpenProcess(SYNCHRONIZE, FALSE, pid);
    DWORD ret = WaitForSingleObject(process, 0);
    CloseHandle(process);
    return ret == WAIT_TIMEOUT;
}




