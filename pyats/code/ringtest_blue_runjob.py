import os
from ats.easypy import run


# pyats run job code/ringtest_blue_runjob.py --testbed n540.yaml 

def main():
    # Find the location of the script in relation to the job file
    blue_ring = os.path.join('code/ringtest.py')

    # Execute the testscript
    run(testscript=blue_ring)