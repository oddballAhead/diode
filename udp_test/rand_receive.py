##
# Receive random numbers from udp sender
#

import socket

HOST = '192.168.15.176'
PORT = 60000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

try :
    while True :
        data = sock.recvfrom(PORT)
        print(str(data))

finally :
    print("closing socket, do not interrupt ...")
    sock.close()
    print("finished ...")


