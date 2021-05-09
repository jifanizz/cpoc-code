#!/usr/bin/env python

# Load testbed and connect to device
from genie.testbed import load

testbed = load('../n540.yaml')
uut = testbed.devices['soda14']


golden_ospf_neighbors=['10.1.1.22', '10.1.1.111','10.1.1.11']

# Connect to device
uut.connect(log_stdout=False)

#Parse OSPF Command
ospf = uut.parse('show ospf vrf all-inclusive neighbor detail')
ospf_int = ospf['vrf']['default']['address_family']['ipv4']['instance']['4000']['areas']['0.0.0.127']['interfaces']

# Extract the OSPF Peer IP Addresses
peer_list=[]
for int in ospf_int:
    nbr_peer=ospf_int[int]['neighbors']
    for nbr_ip in nbr_peer:
        peer_ip=nbr_peer[nbr_ip]['neighbor_router_id']
        peer_list.append(peer_ip)

# Validate that OSPF Peer IP Addresses are in the Golden OSPF Neighbor List
for ospf_nbr_ip in golden_ospf_neighbors:
    if ospf_nbr_ip not in peer_list:
        print(f"{ospf_nbr_ip} is not in Golden IPs")
    else:
        print(f"{ospf_nbr_ip} is in Golden IPs.  SUCCESS!!")