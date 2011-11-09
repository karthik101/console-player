//Main.cpp
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include "Socket.h"

typedef struct session_t {
	int proc;
	int port;
	char fname[256];
	char fpath[1024];
} Session;

int get_session_lock(Session * s, const char * lockpath);
int IsProcessRunning(DWORD pid);
int cstr_rindex(const char * cstr, const char * fmt);

int main(int argc, char **argv)
{

	Session s;
	int success;
	int ind;
    char args[1024];
    char msg[1024];// todo why couldnt i reuse args
	char fpath[1024];
	char file[1024];

	// collect all arguments into a single string
	if (argc > 1) {
		sprintf(args," %s",argv[1]);			
		for (int i=2;i < argc;i++){
			sprintf(args,"%s %s",args,argv[i]);
		}
	}
			
	/*
		get the path to the current directory
	*/
	ind=cstr_rindex(argv[0],"\\/");
	strncpy(fpath,argv[0],ind+1);
    fpath[ind+1]='\0';
	/*
		Find a session.lock file to open
	*/
	success = get_session_lock(&s,".\\user\\session.lock");
	if (!success) {
		ExpandEnvironmentStrings("%APPDATA%",msg,1024);
		sprintf(msg,"%s\\ConsolePlayer\\session.lock",msg);
		success = get_session_lock(&s,msg);
	}

	/*
		with an open sessio.lock
		check for the process and send any argv values to the open process
	*/
	if ( success ) {
	
		//printf("%d\r\n",s.proc);
		//printf("%d\r\n",s.port);
		//printf("%s\r\n",s.fname);
		//printf("%s\r\n",s.fpath);
		
		if (IsProcessRunning(s.proc) && argc > 1) {

			// create the message to send
			sprintf(msg,"[%d]%s\r\n",strlen(args),args);
        
			// connect to the server and send the message.
			Socket sock;
			sock.ConnectToServer( "127.0.0.1", s.port );
			sock.SendData(msg);
			sock.CloseConnection();	
			
			exit(0);
			
		} 
		/*
			launch the program using the name it gave itself in the session.lock
		*/
		if (argc > 1)
			strcat(fpath,args);
		WinExec(s.fpath,SW_NORMAL);
		exit(0);

	}
	// Launch an executable in the current directory under the name ConsolePlayer
	// launch it forcing the installation in the home directory.
	if (argc > 1) {
		strcat(fpath,"ConsolePlayer.exe");
		strcat(fpath,args);
	}
	else
		strcat(fpath,"ConsolePlayer.exe --install=home");

	WinExec(fpath,SW_NORMAL);

}

int get_session_lock(Session * s, const char * lockpath) {
	/*
		return information from the session.lock file found at lockpath
	*/
	FILE * rf;
	
	rf = fopen(lockpath,"r");
	if (rf) {
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



int cstr_rindex(const char * cstr, const char * fmt){
	/*
		return the last index of character in fmt
		fmt can be a string with multiple characters
		in this case the index of the last character will be returned.
		
		-1 is returned when no values are found
		
	*/
	
	int i=0;
	int j=0;
	int index=-1;
	while (cstr[i] != '\0') {
		j=0;
		
		while (fmt[j] != '\0') {
			if (cstr[i] == fmt[j])
				index = i;
			j++;
		}

		i++;
	}
	return index;
}
