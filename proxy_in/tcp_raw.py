##
# A raw tcp listener. Will attempt to receive a connection from
# a 104 client, and extrack datagrams.
#

import socket

# HOST = '192.168.15.176'
HOST = '127.0.0.1'
IEC_60870_5_104_DEFAULT_PORT = 2404
PORT                         = 5000
BUFSIZE = 4096

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, IEC_60870_5_104_DEFAULT_PORT))
sock.listen()

# Create udp socket
diode = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try :
    while True :
        packet_counter = 0
        partner = sock.accept()
        new_sock = partner[0]
        print('New connection with', partner[1])
        while True :
            data = new_sock.recv(BUFSIZE)
            if not data :
                break
            packet_counter += 1
            print('Received data:', data, 'sending it in udp to', (HOST, PORT))
            diode.sendto(data, (HOST, PORT))

        print('Received', packet_counter, 'packets in total')
        new_sock.close()
        print('Connection closed...')

finally :
    sock.close()
