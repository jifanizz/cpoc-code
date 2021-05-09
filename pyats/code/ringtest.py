#!/usr/bin/env python

# To get a logger for the script
import logging

# Import of PyATS library
from pyats import aetest
from pyats.log.utils import banner

# Genie Imports
from genie.conf import Genie

# To handle errors with connections to devices
from unicon.core import errors

import argparse
from pyats.topology import loader

# Get your logger for your script
global log
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################




class common_setup(aetest.CommonSetup):
    """
    Connect to the devices listed in the testbed.
    """
    @aetest.subsection
    def establish_connections(self, testbed):
        # Load testbed file which is passed as command-line argument
        genie_testbed = Genie.init(testbed)
        self.parent.parameters['testbed'] = genie_testbed
        device_list = []
        # Load all devices from testbed file and try to connect to them
        for device in genie_testbed.devices.values():
            log.info(banner(f"Connect to device '{device.name}'"))
            try:
                device.connect(log_stdout=False)
            except errors.ConnectionError:
                self.failed(f"Failed to establish "
                            f"connection to '{device.name}'")
            device_list.append(device)
        # Pass list of devices to testcases
        self.parent.parameters.update(dev=device_list)


###################################################################
#                     TESTCASES SECTION                           #
###################################################################

class Verify_OSFP_Neighbor_count(aetest.Testcase):
    @aetest.setup
    def setup(self):
        devices = self.parent.parameters['dev']
        aetest.loop.mark(self.ospf_neighbor_count, device=devices)

    @aetest.test
    def ospf_neighbor_count(self,device):
        """
        Validate that each node has 2 OSPF neighbors in FULL
        """
        if device.os == 'iosxr':
        
            ospf_nbr=device.parse('show ospf vrf all-inclusive')
            ospf_nbr_cnt=ospf_nbr['vrf']['default']['address_family']['ipv4']['instance']['4000']['adjacency_stagger']['nbrs_full']

            if ospf_nbr_cnt != 2:
                self.failed(f"Router does not have 2 OSPF neighbors. Router {device} has {ospf_nbr_cnt} neighbors")
            else:
                pass

class Verify_Golden_OSPF_Neighbor_Peer(aetest.Testcase):
    @aetest.setup
    def setup(self):
        devices = self.parent.parameters['dev']
        aetest.loop.mark(self.ospf_neighbor_list, device=devices)
    
    @aetest.test
    def ospf_neighbor_list(self,device):
        """
        Validate that only OSPF neighbors defined in golden_ospf_neighbors are active
        """
        #Definde Blue Ring OSPF Neighbors
        golden_ospf_neighbors=['10.1.1.111', '10.1.1.1','10.1.1.2', '10.1.1.3', '10.1.1.4', '10.1.1.5', '10.1.1.102']

        ospf_nbr_det = device.parse('show ospf vrf all-inclusive neighbor detail')
        ospf_int = ospf_nbr_det['vrf']['default']['address_family']['ipv4']['instance']['4000']['areas']['0.0.0.127']['interfaces']

        # Extract the OSPF Peer IP Addresses
        peer_list=[]
        for int in ospf_int:
            nbr_peer=ospf_int[int]['neighbors']
            for nbr_ip in nbr_peer:
                peer_ip=nbr_peer[nbr_ip]['neighbor_router_id']
                print(peer_ip)
                peer_list.append(peer_ip)
                
        
        print(peer_list)
        # Validate that OSPF Peer IP Addresses are in the Golden OSPF Neighbor List
        for ospf_nbr_ip in peer_list:
            if ospf_nbr_ip not in golden_ospf_neighbors:
                self.failed(f"{ospf_nbr_ip} not found")
            else:
                pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))
