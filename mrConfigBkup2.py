from pickle import TRUE
import re
from typing import Dict,List
import asyncio
from pathlib import Path
import json
from time import *
import meraki
import meraki.aio

MERAKI_PYTHON_SDK_CALLER = 'configMeraki'

import argparse


# Handel the Args 
parser = argparse.ArgumentParser(description="SSH's and Outputs the following commands Show run-config, Show run-config commands(startup Configs), Show tech, Show mslog into files for TAC")
parser.add_argument("-netType", action="store", dest="netType")
parser.add_argument("-netTag", action="store", dest="netTag")
parser.add_argument("-orgId", action="store", dest="orgId")
args = parser.parse_args()

networkTag = [args.netTag]
orgId = args.orgId

print(f'OrgID {orgId}')



dashboard = meraki.DashboardAPI()


#Radio Settings Per AP

wirelessIoTRadioConfig = {}
async def wirelessIoTRadioConfig(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    wirelessIoTRadioConfig.update(bluetooth = await aiomeraki.wireless.getNetworkWirelessBluetoothSettings(netId))
    

    print(wirelessIoTRadioConfig )
    returnPackage = {'configName':'wirelessIoTRadioConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':wirelessIoTRadioConfig}
    return returnPackage


## Wireless AMI is configured in the Network Wide page 
"""
wirelessAltMgmtIntConfig = {}
async def wirelessAltMgmtInt(aiomeraki: meraki.aio.AsyncDashboardAPI, netId:str) -> Dict[str,int]:
    wirelessAltMgmtIntConfig.update(wirelessAMI = await aiomeraki.wireless.getNetworkWirelessAlternateManagementInterface(netId))
    

    print(wirelessAltMgmtIntConfig )
    return wirelessAltMgmtIntConfig

Wireless Settings also needs to be figured out
"""
## Billing 
wirelessSplashPageConfig = {}
async def wirelessSplashPage(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    wirelessSplashPageConfig.update(billing = await aiomeraki.wireless.getNetworkWirelessBilling(netId))
    
    print(wirelessSplashPageConfig )
    returnPackage = {'configName':'wirelessSplashPageConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':wirelessSplashPageConfig}
    return returnPackage

wirelessRadioConfig = {}
async def wirelessRadio(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    wirelessRadioConfig.update(rfProfiles = await aiomeraki.wireless.getNetworkWirelessRfProfiles(netId))
    
    print(wirelessRadioConfig )
    returnPackage = {'configName':'Wireless-radio.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':wirelessRadioConfig}
    return returnPackage

#This includes both SSID, Access control, and Availability Pages page config
wirelessSSIDConfig = {}
async def wirelessSSID(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    wirelessSSIDConfig.update(ssids = await aiomeraki.wireless.getNetworkWirelessSsids(netId))
    
    print(wirelessSSIDConfig )
    returnPackage = {'configName':'Wireless-ssid.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':wirelessSSIDConfig}
    return returnPackage

wirelessSSIDdetailsConfig = {}
# Includes Hotspot, Firewall Traffic Shapping all related details 
async def wirelessSSIDdetails(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:

    
    for ssidId in range(15): 
        wirelessSSIDdetailsConfigId = {}
        wirelessSSIDdetailsConfigId.update( bonjourForwarding = await aiomeraki.wireless.getNetworkWirelessSsidBonjourForwarding(netId, str(ssidId)))
        wirelessSSIDdetailsConfigId.update( deviceTypeGroupPolicies = await aiomeraki.wireless.getNetworkWirelessSsidDeviceTypeGroupPolicies(netId, str(ssidId)))
        wirelessSSIDdetailsConfigId.update( ssidEapOverride= await aiomeraki.wireless.getNetworkWirelessSsidEapOverride(netId, str(ssidId)))
        wirelessSSIDdetailsConfigId.update( ssidFirewallL3FirewallRules= await aiomeraki.wireless.getNetworkWirelessSsidFirewallL3FirewallRules(netId, str(ssidId)))
        wirelessSSIDdetailsConfigId.update( ssidFirewallL7FirewallRules= await aiomeraki.wireless.getNetworkWirelessSsidFirewallL7FirewallRules(netId, str(ssidId)))
        wirelessSSIDdetailsConfigId.update( ssidHotspot20= await aiomeraki.wireless.getNetworkWirelessSsidHotspot20(netId, str(ssidId)))
        try:
            wirelessSSIDdetailsConfigId.update( ssidIdentityPsks= await aiomeraki.wireless.getNetworkWirelessSsidIdentityPsks(netId, str(ssidId)))
        except meraki.exceptions.AsyncAPIError as error:
            if str(error.message) not in ["{'errors': ['Unsupported for networks bound to a template']}"] :
                raise
            else:
                print("iPSKs Unsupported for networks bound to a template"+str(error.status)+str(error.message))
        wirelessSSIDdetailsConfigId.update( ssidSchedules= await aiomeraki.wireless.getNetworkWirelessSsidSchedules(netId, str(ssidId)))
        wirelessSSIDdetailsConfigId.update( ssidSplashSettings= await aiomeraki.wireless.getNetworkWirelessSsidSplashSettings(netId, str(ssidId)))
        try:
            wirelessSSIDdetailsConfigId.update( ssidTrafficShapingRules= await aiomeraki.wireless.getNetworkWirelessSsidTrafficShapingRules(netId, str(ssidId)))
        except meraki.exceptions.AsyncAPIError as error:
            if str(error.message) not in ["{'errors': ['Unsupported for networks bound to a template']}"] :
                raise
            else:
                print("TrafficShapping Unsupported for networks bound to a template"+str(error.status)+str(error.message))
        wirelessSSIDdetailsConfigId.update( ssidVpn= await aiomeraki.wireless.getNetworkWirelessSsidVpn(netId, str(ssidId)))
        
        wirelessSSIDdetailsConfig[ssidId] = wirelessSSIDdetailsConfigId
    print(wirelessSSIDdetailsConfig )
    returnPackage = {'configName':'Wireless-ssidDetails.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':wirelessSSIDdetailsConfig}
    return returnPackage

# Config Missing
  # HotSpot 2.0
  # "Splash Page Might be avaiaible in Splash Page API"
  #  Firewall and Trafficshapping 

wirelessDeviceConfig = {}
#Camera Device Config
async def wirelessDeviceConf(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str, deviceSN:str) -> Dict[str,int]:
    wirelessDeviceConfig[deviceSN] = await aiomeraki.devices.getDevice(deviceSN)
    print(wirelessDeviceConfig)
    try:
        wirelessDeviceConfig[deviceSN].update(wirelessBluetoothSettings = await aiomeraki.wireless.getDeviceWirelessBluetoothSettings(deviceSN))
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))

    wirelessDeviceConfig[deviceSN].update(wirelessRadioSettings = await aiomeraki.wireless.getDeviceWirelessRadioSettings(deviceSN))
    
    returnPackage = {'configName':'Wireless-deviceConfig.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':wirelessDeviceConfig}
    print(returnPackage)
    return returnPackage


async def writeConfigFile(filePath, fileName, fileData):
    
    if filePath.exists() != True:
            filePath.mkdir(parents=True)

    fileWrite = filePath / fileName

    with open(fileWrite, 'w+', encoding='utf-8') as f:
        json.dump(fileData, f, ensure_ascii=False, indent=4)



async def main(orgIdfilter=False, netTag=False):

    organizations = dashboard.organizations.getOrganizations()

    if orgIdfilter:
        for org in organizations:
            if orgIdfilter == org['id']:

                 organizations = [org]

    

    async with meraki.aio.AsyncDashboardAPI(
        base_url="https://api.meraki.com/api/v1",
        log_file_prefix=__file__[:-3],
        print_console=False,
        maximum_concurrent_requests=10,
        maximum_retries= 100,
        wait_on_rate_limit=True
    ) as aiomeraki:

        start_timer = time()
        taskList = []   
 
        for org in organizations:
            orgId = org['id']    
            print(netTag)
            if netTag:
                networks =  dashboard.organizations.getOrganizationNetworks(orgId, tags = netTag)
                print("NETTAG")
            else:
                networks =  dashboard.organizations.getOrganizationNetworks(orgId)
        

            for net in networks:
                netId = net['id']
                if 'wireless' in net['productTypes']:

                    orgName = org['name']
                    netName = net['name']

                    taskList.append( wirelessRadio(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append( wirelessSSID(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append( wirelessSSIDdetails(aiomeraki, orgId, orgName, netId, netName))

                    devices = dashboard.networks.getNetworkDevices(netId)

                    for device in devices:
                        if device['model'].startswith('MR'):
                            deviceSN = device['serial']
                            taskList.append(wirelessDeviceConf(aiomeraki, orgId, orgName, netId, netName, deviceSN))
                    
                    

      
                        #taskList.append(wirelessRadioConfig)
                        #taskList.append(wirelessSSIDConfig)
                        
                        
                        #for ssidId in range(15):
                         #   taskList.append( wirelessSSIDdetails(aiomeraki, orgId, orgName, netId, netName)) 

            '''
                        for ssids in wirelessSSIDConfig['ssids']:

                            ssidId = ssids['number']
                            print("SSID Number")
                            print(ssidId)
                            #wirelessSSIDdetailsConfig[ssidId] = {}
                            wirelessSSIDdetailsConfig[ssidId] = await wirelessSSIDdetails(aiomeraki, netId, ssidId)
                            taskList.append(wirelessSSIDdetailsConfig)
                         '''

                       
                    
                       

                        #writeConfigFile(filePath, "Wireless-radio.json", wirelessRadioConfig)
                        #writeConfigFile(filePath, "Wireless-ssid.json", wirelessSSIDConfig)
                        #writeConfigFile(filePath, "Wireless-ssidDetails.json", wirelessSSIDdetailsConfig)

        responses = await asyncio.gather(*taskList)

        
        for response in responses:
            orgId = response['orgId']
            orgName = response['orgName']
            netId = response['netId']
            netName = response['netName']
            
            filePath = Path('Org/'+orgName+'-'+orgId+'/Net/'+netName+'-'+netId+'/')
            await writeConfigFile(filePath, response['configName'], response['configJson'])
          
            

            
        #asyncio.as_completed(taskList)
        
        
        end_timer = time()
        elapsedTime = round(end_timer-start_timer,2)
        print(f"Took a total of {elapsedTime} seconds")



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(orgId, networkTag))



