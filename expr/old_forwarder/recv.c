#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <unistd.h>

#define PORT "7000"


int start_receive(int sock) {
    int i;
    char buf;
    for (i = 0; i < 10; i++) {
        if (recv(sock, &buf, sizeof buf, 0) == 0) return 0;
        printf("End station received data: %c\n", buf);
    }
}

/* End-point station, receives udp datagrams */
int main(void) {
    int sock, i, status, yes = 1;
    struct addrinfo hints, *res;

    printf("Starting endpoint udp-receive server...\n");

    /* getaddrinfo() */
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE;

    if ((status = getaddrinfo(NULL, PORT, &hints, &res)) != 0) {
        fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(status));
        exit(1);
    }

    /* Below might contain errors, verify */
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("socket"); exit(1);
    }
    /* Loose socket "Address already in use error" */
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes) == -1) {
        perror("setsockopt"); exit(1);
    }
    /* Bind socket to port */
    if (bind(sock, res->ai_addr, res->ai_addrlen) != 0) {
        perror("bind"); exit(1);
    }

    start_receive(sock);

    close(sock);
    return 0;
}