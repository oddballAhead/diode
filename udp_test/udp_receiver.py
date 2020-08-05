import socket
import errno
import os



# HOST = '127.0.0.1'
# HOST = '192.168.15.175'
HOST = '192.168.15.176'
# HOST = '0.0.0.0'
# HOST = '255.255.255.255'
PORT = 60000

print("hello world", "yolo", "swag", "arg")


# socket can be used with the with-statement (look it up)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(sock)
sock.bind((HOST, PORT))

packet_counter = 0
try :
    while True :
        packet_counter += 1
        data = sock.recvfrom(PORT)
        if packet_counter > 1000000 :
            packet_counter = 0
            print('yolo\n\n\n\n')
        else :
            print('Received data:', data)

finally :
    sock.close()

