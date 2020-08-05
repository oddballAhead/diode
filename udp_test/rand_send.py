##
# Sends an infinite stream of random integers
# over udp socket
#

import random
import socket
from time import sleep

HOST = '192.168.15.176'
PORT = 60000

def main() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elems = []
    for e in range(1400) :
        elems.append(e)

    print("Sending random numbers...")
    try :
        while True :
            # n = random.randint(-30, 30)
            data = bytes(str(elems), 'utf-8')
            sock.sendto(data, (HOST, PORT))
            # sleep(0.5)
    finally :
        sock.close()


# call main function
main()