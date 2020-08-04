#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <unistd.h>

#define HOST "127.0.0.1"
#define PORT "3490"
#define NEW_PORT "7000"
#define BACKLOG 10


/* This represents a forwarding server. It shall listen to incoming TCP-connections,
   receive data on these, and then send the data forward in udp-datagrams to the end-station */
int main(void) {
    int sock, new_sock, udp_sock, i, yes = 1;
    struct addrinfo hints, *res;
    /* Storage for incoming connection */
    struct sockaddr_storage their_addr;
    socklen_t addr_size;

    printf("Starting forwarding server...\n");

    /* getaddrinfo() */
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    getaddrinfo(NULL, PORT, &hints, &res);

    /* Get tcp socket */
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket"); exit(1);
    }
    /* Get udp socket */
    if ((udp_sock = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("upd-socket"); exit(1);
    }

    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes) == -1) {
        perror("setsockopt"); exit(1);
    }
    if (setsockopt(udp_sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes) == -1) {
        perror("udp-setsockopt"); exit(1);
    }
    if (bind(sock, res->ai_addr, res->ai_addrlen) == -1) {
        perror("bind"); exit(1);
    }
    if (listen(sock, BACKLOG) == -1) {
        perror("listen"); exit(1);
    }
    if ((new_sock = accept(sock, (struct sockaddr *)&their_addr, &addr_size)) == -1) {
        perror("accept"); exit(1);
    }

    char buf;
    int status;

    struct sockaddr_in their_udp;
    their_udp.sin_family = AF_INET;
    their_udp.sin_port = htons(7000);  /* TODO: make this more generic */
    inet_aton(HOST, &(their_udp.sin_addr));
    memset(&(their_udp.sin_zero), 0, 8);
    /* Receive important messages */
    for (i = 0; i < 10; i++) {
        if ((status = recv(new_sock, &buf, sizeof(char), 0)) == -1) {
            perror("recv"); exit(1);
        } else if (status == 0) {
            /* Means that sender has stopped sending */
            // Do something relevant here
            break;
        }
        printf("Received data: %c\n", buf);

        /* TODO: fix this */
        if (sendto(udp_sock, &buf, sizeof(char), 0, (struct sockaddr *)&their_udp, sizeof(struct sockaddr_storage)) == -1) {
            perror("sendto"); exit(1);
        }
    }

    close(sock);
    close(udp_sock);
    return 0;
}