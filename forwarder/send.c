#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <unistd.h>


static int start_sending(int sock) {
    printf("TCP-sender is starting transmission of data...\n");
    /* Calls to send() */
    int i;
    char c = 'a';
    for (i = 0; i < 10; i++) {
        if (send(sock, &c, sizeof c, 0) == -1) {
            perror("send"); exit(1);
        }
        c++;
    }


}

/* End-point sender, will connect with TCP to the forwarding station
   Establish the connection, and send some data. */
int main(void) {
    int status, sock, yes = 1;
    struct addrinfo hints;
    struct addrinfo *res;

    printf("Starting endpoint send-client...\n");
    /* Setting up TCP client */
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;    // IPv4
    hints.ai_socktype = SOCK_STREAM; // tcp socket
    hints.ai_flags = AI_PASSIVE;   // fill in my IP for me (what?)

    if ((status = getaddrinfo(NULL, "3490", &hints, &res)) != 0) {
        fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(status));
        exit(1);
    }

    /* Get the socket descriptor */
    // if ((sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol)) == -1) {
    //     printf("Call to socket() failed...\n"); exit(1);
    // }
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket"); exit(1);
    }

    /* Loose socket "Address already in use error" */
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes) == -1) {
        perror("setsockopt"); exit(1);
    }

    // /* Bind socket to port */
    // if (bind(sock, res->ai_addr, res->ai_addrlen) != 0) {
    //     printf("Call to bind() failed...\n"); exit(1);
    // }
    /* Try to connect */
    if (connect(sock, res->ai_addr, res->ai_addrlen) == -1) {
        perror("connect"); exit(1);
    }

    /* Start to send data to the forwarding station */
    start_sending(sock);

    /* Free the socket */
    close(sock);
}














