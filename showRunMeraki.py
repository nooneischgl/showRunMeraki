# This is the showRunMeraki




## Take in Scoping Paramenters, these will be Network Type, ID, Org ID, Network Tag

import orgConfigBkup
import mxConfigBkup2
import mrConfigBkup2
import msConfigBkup2
import mvConfigBkup2
import mgConfigBkup2
import mtConfigBkup2
import smConfigBkup2
import miConfigBkup2

import asyncio
import argparse
from time import *


# Handel the Args 
parser = argparse.ArgumentParser(description="SSH's and Outputs the following commands Show run-config, Show run-config commands(startup Configs), Show tech, Show mslog into files for TAC")
parser.add_argument("-netType", action="store", dest="netType")
parser.add_argument("-netTag", action="store", dest="netTag")
parser.add_argument("-orgId", action="store", dest="orgId")
args = parser.parse_args()


if args.netTag:
    networkTag = [args.netTag]
else:
    networkTag = False


if args.orgId:
    orgId = args.orgId
else:
    orgId = False

print(f'OrgID {orgId}')

if __name__ == '__main__':
    start_timer = time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orgConfigBkup.main(orgId))
    loop.run_until_complete(msConfigBkup2.main(orgId, networkTag))
    loop.run_until_complete(mrConfigBkup2.main(orgId, networkTag))
    loop.run_until_complete(mvConfigBkup2.main(orgId, networkTag))
    loop.run_until_complete(mgConfigBkup2.main(orgId, networkTag))
    loop.run_until_complete(mtConfigBkup2.main(orgId, networkTag))
    loop.run_until_complete(smConfigBkup2.main(orgId, networkTag))
    loop.run_until_complete(miConfigBkup2.main(orgId, networkTag))
    print("MX is running")
    loop.run_until_complete(mxConfigBkup2.main(orgId, networkTag))

    end_timer = time()
    elapsedTime = round(end_timer-start_timer,2)
    print(f"Took a total of {elapsedTime} seconds")
