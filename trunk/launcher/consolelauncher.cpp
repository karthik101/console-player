//Main.cpp
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include "Socket.h"

typedef struct session_t {
	int proc;			// last process ID (PID) of a running copy of Console Player
	int port;			// the port that process was running on
	char fname[256];	// the exe name it had
	char fpath[1024];   // the filepath to that executable, including the file name
} Session;

void cstr_strip_newline(char * cstr);
int get_session_lock(Session * s, const char * lockpath);
int IsProcessRunning(DWORD pid);
void dir_find_largest(const char * dir,char* largest);
int cstr_rindex(const char * cstr, const char * fmt);

int main(int argc, char **argv) {

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
	printf("Console Launcher\r\n");		
	printf("args: %s\r\n",args);		
	/*
		get the path to the current directory
	*/
	ind=cstr_rindex(argv[0],"\\/");
	strncpy(fpath,argv[0],ind+1);
    fpath[ind+1]='\0';
	printf("arg0: %s\r\n",argv[0]);		
	printf("fpath: %s\r\n",fpath);		
	/*
		Find a session.lock file to open
	*/
	success = get_session_lock(&s,".\\user\\session.lock");
	printf("lock: %d\r\n",success);
	if (!success) {
		success = get_session_lock(&s,".\\session.lock");
		printf("lock-local: %d\r\n",success);
	}
	// check for a session lock in the appdata folder
	if (!success) {
		ExpandEnvironmentStrings("%APPDATA%",msg,1024);
		sprintf(msg,"%s\\ConsolePlayer\\session.lock",msg);
		success = get_session_lock(&s,msg);
		printf("lock-appdata: %d\r\n",success);
	}

	/*
		with an open sessino.lock
		check for the process and send any argv values to the open process
	*/
	if ( success ) {
	
		printf("%d\r\n",s.proc);
		printf("%d\r\n",s.port);
		printf("%s\r\n",s.fname);
		printf("%s\r\n",s.fpath);
		
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
		//fscanf(rf,"%s\r\n",&(s->fname));
		//fscanf(rf,"%s\r\n",&(s->fpath));
		fgets(s->fname, 256, rf);	// fgets reads until a newline
		fgets(s->fpath, 1024, rf);
		
		fclose(rf);
		
		cstr_strip_newline( s->fname );
		cstr_strip_newline( s->fpath );

		return 1;
	}
	return 0;
}

void cstr_strip_newline(char * cstr){
	for (int i=0;cstr[i] != '\0'; i++) {
		if (cstr[i] == '\r' || cstr[i] == '\n') {
			cstr[i] = '\0';
		}
	}
}

int IsProcessRunning(DWORD pid) {
    HANDLE process = OpenProcess(SYNCHRONIZE, FALSE, pid);
    DWORD ret = WaitForSingleObject(process, 0);
    CloseHandle(process);
    return ret == WAIT_TIMEOUT;
}

void dir_find_largest(const char * dir,char* largest) {
	//set the string pointer at largest to the passivley sorted
	// largest file name in the given directory
	// e.g. : file: test_01.txt is less than test_1.txt
	// use ./*.txt to enumerate all txt files in the directory
	// use ./*.exe to enumerate all txt files in the directory
	// use ./*     to enumerate all files and folders in a directory

	// path to last file found
	char buffer[1024];// = malloc(1024*sizeof(unsigned char));
	WIN32_FIND_DATA myimage;
	HANDLE myHandle;
	
	//----------------------------------------------------
	
	myHandle=FindFirstFile(dir,&myimage);
	
	if(myHandle!=INVALID_HANDLE_VALUE) {
	
		strcpy (buffer,myimage.cFileName);
		strcpy (largest,myimage.cFileName);

		while( 1 ) {

			FindNextFile(myHandle,&myimage);

			if(strcmp(myimage.cFileName,buffer) != 0) {
				//buffer=myimage.cFileName;
				strcpy (buffer,myimage.cFileName);
				if (strcmp(buffer,largest) > 0)
					strcpy (largest,buffer);
			}
			else
				  break; //end of files reached

		}
	}
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
