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
                self.failed("Router does not have 2 OSPF neighbors")
            else:
                pass

class Verify_MPLS_Neighbor_count(aetest.Testcase):
    @aetest.setup
    def setup(self):
        devices = self.parent.parameters['dev']
        aetest.loop.mark(self.mpls_neighbor_count, device=devices)

    @aetest.test
    def mpls_neighbor_count(self,device):
        """
        Validate that each node has 2 OSPF neighbors in FULL
        """
        if device.os == 'iosxr':
        
            ldp_nbr_cnt = 0
            ldp_peer=device.parse('show mpls ldp neighbor brief')['peer']
            for ldp_cnt in ldp_peer:
                ldp_nbr_cnt += 1
            
            if ldp_nbr_cnt != 2:
                self.failed("Router does not have 2 MPLS LDP Neighbors")
                print(f"router has {ldp_nbr_cnt} LDP neighbors")
            else:
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))
