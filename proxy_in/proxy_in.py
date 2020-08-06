##
# Program running on proxy_in.
# Simply receives datagrams on a udp socket, and forwards them
# through the diode
#
# Reads a .ini file as a config upon startup.
#

import configparser                 #
import socket                       #
import os                           # for creating arp-table entry

HOST = '192.168.15.176'
PORT = 60000


# Specifying a unix file path here, so this will probably not work on windows...
CONFIG_PATH = '../config/config.ini'


def main() :
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    # for e in config['whitelist'] :
    #     print(e)

    # Check if this program was started as root.
    # If yes: will attempt to add arp table entry
    if os.geteuid() != 0 :
        print('You are not root. Cannot add static arp entry. Program will continue, assuming you have already done so')
    else :
        set_arp_entry(config['address']['proxy_out_ip'], config['address']['proxy_out_mac_address'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    try :
        while True :
            data = sock.recvfrom(PORT)
            # forward data into diode
            print(str(data))


    finally :
        print("closing socket, do not interrupt ...")
        sock.close()
        print("finished ...")


# Call shell command to add arp entry
# Warning: Linux-specific code
def set_arp_entry(target_ip, target_mac) :
    print(target_ip, type(target_ip))
    print(target_mac, type(target_mac))  # these were successfully passed as strings

    arp_command = 'arp -s ' + target_ip + ' ' + target_mac
    print(arp_command)

    # execute shell command
    os.system(arp_command)



if __name__ == '__main__' :
    main()