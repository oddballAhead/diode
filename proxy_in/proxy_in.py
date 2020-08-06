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
import numpy                        # For getting proper arrays


# Port number for sending on diode
PORT = '60000'

# Specifying a unix file path here, so this will not work on windows...
CONFIG_PATH = '../config/config.ini'


def main() :
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    # Check if this program was started as root.
    # If yes: will attempt to add arp table entry
    if os.geteuid() != 0 :
        print('You are not root. Cannot add static arp entry. Program will continue, assuming you have already done so')
    else :
        set_arp_entry(config['address']['proxy_out_ip'], config['address']['proxy_out_mac_address'])

    TARGET_IP = config['address']['proxy_out_ip']
    SELF_IP = config['address']['self_ip_address']
    RECEIVE_PORT = config['address']['port_number']
    SEND_PORT = PORT

    # Create lookup table
    TABLE = create_lookup_table(config)

    sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recv.bind((SELF_IP, int(RECEIVE_PORT)))
    sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Starting the main server loop:
    try :
        while True :
            # Trying to receive data on a pure udp-socket, this might not work depending on how data is sent
            data = sock_recv.recvfrom(int(RECEIVE_PORT))
            print(str(data))
            # forward data into diode
            if valid(data, TABLE) :
                sock_send.sendto(data, (TARGET_IP, int(SEND_PORT)))

    finally :
        print("closing sockets, do not interrupt ...")
        sock_recv.close()
        sock_send.close()
        print("finished ...")

# Read allowed ASDUs from config and create access-lookup array
def create_lookup_table(config) :
    table = numpy.full(255, False, dtype=bool)
    for asdu in config['whitelist'] :
        num = get_asdu_id(asdu)
        table[num] = True
    return table

def get_asdu_id(s) :
    start = '('
    end = ')'
    val = ((s.split(start))[1].split(end)[0])
    return int(val)


# Call shell command to add arp entry
# Warning: Linux-specific code
def set_arp_entry(target_ip, target_mac) :
    print(target_ip, type(target_ip))
    print(target_mac, type(target_mac))  # these were successfully passed as strings

    arp_command = 'arp -s ' + target_ip + ' ' + target_mac
    print(arp_command)

    # execute shell command
    os.system(arp_command)

def valid(apdu, TABLE) :
    if apdu[0] != 0x68 :
        return False
    if apdu[1] > 6 : # means there is an asdu
        return TABLE[apdu[6]]
    else :
        # TODO: Add validation checks for apci's with no asdu
        return True



if __name__ == '__main__' :
    main()