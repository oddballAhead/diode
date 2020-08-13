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




##### raw sockets code ########

# sock_recv = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
# sock_recv.bind(('enp0s25', ))  # TODO: finish this
# sock_recv.bind((SELF_IP, int(RECEIVE_PORT)))

# Trying to receive data on a pure udp-socket, this might not work depending on how data is sent
# data = sock_recv.recvfrom(int(RECEIVE_PORT))

# res = sniff("enp0s25", filters="port 60000", count=1, promisc=1, out_file="pcap.pcap")
# print(res)
# sleep(3)












