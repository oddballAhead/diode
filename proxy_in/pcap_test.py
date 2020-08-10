


from pylibpcap.pcap import sniff
from pylibpcap import get_iface_list

print(get_iface_list())

for plen, t, buf in sniff("enp0s25", filters="port 53", count=3, promisc=1, out_file="pcap.pcap"):
    print('foobar')
    print("[+]: Payload len=", plen)
    print("[+]: Time", t)
    print("[+]: Payload", buf)