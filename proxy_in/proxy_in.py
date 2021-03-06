##
# Program running on proxy_in.
# Simply receives datagrams on a udp socket, and forwards them
# through the diode
#
# Needs to be run as sudo, or many of the system calls will not work
#
# Reads a .ini file as a config upon startup.
#

import sys, getopt                  # cmd args
import configparser                 # for reading ini file
import socket                       # for udp networking
import os                           # for creating arp-table entry
import numpy                        # For getting proper arrays
import pylibpcap                    # For easy access to link layer frames
from pylibpcap.pcap import sniff    # packet sniffing
from time import sleep

# NOTE: There are 2 different modules that are both called pylibpcap!
#       One was last updated in 2013 (but that version has the entire api), the
#       version used here is newer (last update 2020), but is very limited.

# import pcapy # Better than pylibpcab, although slightly more cumbersome to use

# Obviously you need to have the various modules installed for the sudo in order
# to run the program. Consult the webpages for the relevant modules for
# installation instructions (remember to install as sudo!)

# Port number for sending on diode
PORT = '60000'

# Specifying a unix file path here, so this will not work on windows...
CONFIG_PATH = '../config/config.ini'

def main() :
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    WITH_UDP_TEST = False
    if len(sys.argv) > 1 :
        if sys.argv[1] == '--udp' :
            WITH_UDP_TEST = True
    print('WITH_UDP_TEST =', WITH_UDP_TEST)

    # Check if this program was started as root.
    # If yes: will attempt to add arp table entry
    if os.geteuid() != 0 :
        print('You are not root. Program will not work, exiting...')
        exit(1)
    else :
        pass
        # set_arp_entry(config['address']['proxy_out_ip'], config['address']['proxy_out_mac_address'])

    TARGET_IP = config['address']['proxy_out_ip']
    SELF_IP = config['address']['self_ip_address']
    RECEIVE_PORT = config['address']['port_number']
    SEND_PORT = PORT

    # Create lookup table
    TABLE = create_lookup_table(config)
    # Create sending socket
    sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Starting the main server loop:
    try :
        # sniff() returns a generator object, this can be iterated like a loop
        # TODO: local ethernet interface cannot be hardcoded!
        for plen, t, data in sniff("enp3s0", filters="port 60000", count=10, promisc=1, out_file="pcap.pcap"):
            # print('len type:', type(plen))
            # print('time type:', type(t))
            # print('data (payload) type:', type(data))
            print("[+]: Payload len=", plen)
            print("[+]: Time", t)
            print("[+]: Payload:", '0x ' + data.hex(), end='\n\n')

            # Add code to extract APDU here
            print('APDU extraction:')
            apdu = extract_apdu(data, WITH_UDP_TEST)

            if WITH_UDP_TEST :
                # convert apdu to list of integers
                data_received = str(apdu)
                print('Length of data received:', len(data_received))
                print('data received:', data_received, end='\n\n\n')
                continue
            # forward data into diode
            if valid(apdu, TABLE) :
                print('Apdu valid, re-transmitting...')
                sock_send.sendto(apdu, (TARGET_IP, int(SEND_PORT)))

    finally :
        print("closing sockets, do not interrupt ...")
        # sock_recv.close()
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


# Parse the entire ethernet frame, extract asdu payload and return
# WARNING: Assuming that only ethernet frames are received,
#          if another frame type is received, the behavior is unspecified
def extract_apdu(data, WITH_UDP_TEST) :
    # step 1: strip ethernet header
    eth_stripped = strip_ethernet_frame(data)
    print('ether stripped:', eth_stripped.hex())
    print('len:', len(eth_stripped))

    # step 2: strip ip header
    ip_stripped = strip_ip_header(eth_stripped)
    print('ip stripped:', ip_stripped.hex())
    print('len', len(ip_stripped))

    # step 3: strip tcp/udp header
    if WITH_UDP_TEST :
        apdu = strip_udp_header(ip_stripped)
        print('udp stripped:', apdu.hex())
        print('len', len(apdu))
        return apdu

    apdu = strip_tcp_header(ip_stripped)
    return apdu

# Give an ethernet frame, returns a copy with header removed
def strip_ethernet_frame(frame) :
    MAC_LEN = 6                             # length of a mac address in bytes
    ethertype = frame[12:14]                # extract the ethertype from header
    ethertype = int.from_bytes(ethertype, byteorder='big', signed=False) # check efficiency of this, and if 'big' is correct
    print('ethertype expected: 2048, actual:', ethertype)
    Q = 0x8100   # 802.1Q tag
    AD = 0x88a8  # 802.1ad tag
    if ethertype == Q or ethertype == AD:
        #TODO: Add support for these tags
        print('Error, tags not supported!')
        exit(1)
    elif ethertype > 1535 :
        payload_start = 2 * MAC_LEN + 2
    else :
        #TODO: Add support for embedded frame size
        print('Error: Unsupported ethernet frame format!')
        exit(1)
    return frame[payload_start:]   # TODO: remove the trailing checksum here as well maybe?? (doesn't appear to be one)

# get ip packet and return a copy with ip-header removed
def strip_ip_header(packet) :
    # ip header has variable length, first calculate the length
    first_byte = packet[0]
    IHL = first_byte & 0b1111
    if IHL > 15 :
        print('Error: IHL-field in ip-header is to large')
        exit(1)
    elif IHL >= 5 :
        ip_len = IHL * 4
    else :
        print('Error: impossibly small ip-header')
        exit(1)
    return packet[ip_len:]

# udp headers have a fixed length of 8 byte
def strip_udp_header(dgram) :
    return dgram[8:]

# tcp headers have variable length
def strip_tcp_header(segment) :
    length = (segment[12] >> 4) & 0b1111

    if length > 15 :
        print('Error: length field in tcp-header to big')
        exit(1)
    elif length >= 5 :
        tcp_hdr_size = length * 4
    else :
        print('Error: tcp-header too small')
        exit(1)
    return segment[tcp_hdr_size:]


if __name__ == '__main__' :
    main()




# List of issues:
"""
Some of the received packets contain a bunch of trailing null-bytes.

There is no check for the ethernet frame type. This means that if the packet has a non-ethernet frame,
the program will behave in an unspecified manner. Also, non-standard ethernet headers, such as jumbo frames,
are not currently supported, but it should be relatively easy to extend the program to allow support for these.

Important: Since the ip protocol can cause fragmentation (and maybe tcp can as well), a single package may
not correspond to a single ethernet frame. The proram currently assumes that 1 frame = 1 package. This is
not good, and will cause breakage when this is not the case. For 104 protocol, this is not a problem, as the
total frame size is never close to the limit

A similar idea might be possible to use for the ICCP protocol. However, this will be much more complicated
as the ICCP protocol has a much bigger protocol stack, and it is not as easy to find the header structures
for these protocols, and if they even have any

Data sent/received is not converted to network byte order. I do not yet know if the sniff() function does
automatic convertion to host byte order, or if I have to do this manually in the program.
"""