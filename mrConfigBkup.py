from typing import Dict,List
import asyncio
from pathlib import Path
import json

import meraki
import meraki.aio

MERAKI_PYTHON_SDK_CALLER = 'configMeraki'



dashboard = meraki.DashboardAPI()

organizations = dashboard.organizations.getOrganizations()



#networks = dashboard.organizations.getOrganizationNetworks(orgId)

#Internet Lifeguard (organization ID: 803699) 
#thePeral L_821343982041694875

#Radio Settings Per AP

wirelessIoTRadioConfig = {}
async def wirelessIoTRadioConfig(aiomeraki: meraki.aio.AsyncDashboardAPI, netId:str) -> Dict[str,int]:
    wirelessIoTRadioConfig.update(bluetooth = await aiomeraki.wireless.getNetworkWirelessBluetoothSettings(netId))
    

    print(wirelessIoTRadioConfig )
    return wirelessIoTRadioConfig


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
async def wirelessSplashPage(aiomeraki: meraki.aio.AsyncDashboardAPI, netId:str) -> Dict[str,int]:
    wirelessSplashPageConfig.update(billing = await aiomeraki.wireless.getNetworkWirelessBilling(netId))
    
    print(wirelessSplashPageConfig )
    return wirelessSplashPageConfig

wirelessRadioConfig = {}
async def wirelessRadio(aiomeraki: meraki.aio.AsyncDashboardAPI, netId:str) -> Dict[str,int]:
    wirelessRadioConfig.update(rfProfiles = await aiomeraki.wireless.getNetworkWirelessRfProfiles(netId))
    
    print(wirelessRadioConfig )
    return wirelessRadioConfig

#This includes both SSID, Access control, and Availability Pages page config
wirelessSSIDConfig = {}
async def wirelessSSID(aiomeraki: meraki.aio.AsyncDashboardAPI, netId:str) -> Dict[str,int]:
    wirelessSSIDConfig.update(ssids = await aiomeraki.wireless.getNetworkWirelessSsids(netId))
    
    print(wirelessSSIDConfig )
    return wirelessSSIDConfig

wirelessSSIDdetailsConfig = {}
# Includes Hotspot, Firewall Traffic Shapping all related details 
async def wirelessSSIDdetails(aiomeraki: meraki.aio.AsyncDashboardAPI, netId:str, ssidId:int) -> Dict[str,int]:
    wirelessSSIDdetailsConfig.update( bonjourForwarding= await aiomeraki.wireless.getNetworkWirelessSsidBonjourForwarding(netId, ssidId))
    wirelessSSIDdetailsConfig.update( deviceTypeGroupPolicies= await aiomeraki.wireless.getNetworkWirelessSsidDeviceTypeGroupPolicies(netId, ssidId))
    wirelessSSIDdetailsConfig.update( ssidEapOverride= await aiomeraki.wireless.getNetworkWirelessSsidEapOverride(netId, ssidId))
    wirelessSSIDdetailsConfig.update( ssidFirewallL3FirewallRules= await aiomeraki.wireless.getNetworkWirelessSsidFirewallL3FirewallRules(netId, ssidId))
    wirelessSSIDdetailsConfig.update( ssidFirewallL7FirewallRules= await aiomeraki.wireless.getNetworkWirelessSsidFirewallL7FirewallRules(netId, ssidId))
    wirelessSSIDdetailsConfig.update( ssidHotspot20= await aiomeraki.wireless.getNetworkWirelessSsidHotspot20(netId, ssidId))
    try:
        wirelessSSIDdetailsConfig.update( ssidIdentityPsks= await aiomeraki.wireless.getNetworkWirelessSsidIdentityPsks(netId, ssidId))
    except meraki.exceptions.AsyncAPIError as error:
       if str(error.message) not in ["{'errors': ['Unsupported for networks bound to a template']}"] :
          raise
       else:
           print("iPSKs Unsupported for networks bound to a template"+str(error.status)+str(error.message))
    wirelessSSIDdetailsConfig.update( ssidSchedules= await aiomeraki.wireless.getNetworkWirelessSsidSchedules(netId, ssidId))
    wirelessSSIDdetailsConfig.update( ssidSplashSettings= await aiomeraki.wireless.getNetworkWirelessSsidSplashSettings(netId, ssidId))
    try:
        wirelessSSIDdetailsConfig.update( ssidTrafficShapingRules= await aiomeraki.wireless.getNetworkWirelessSsidTrafficShapingRules(netId, ssidId))
    except meraki.exceptions.AsyncAPIError as error:
       if str(error.message) not in ["{'errors': ['Unsupported for networks bound to a template']}"] :
          raise
       else:
           print("TrafficShapping Unsupported for networks bound to a template"+str(error.status)+str(error.message))
    wirelessSSIDdetailsConfig.update( ssidVpn= await aiomeraki.wireless.getNetworkWirelessSsidVpn(netId, ssidId))
    
    print(wirelessSSIDdetailsConfig )
    return wirelessSSIDdetailsConfig

# Config Missing
  # HotSpot 2.0
  # "Splash Page Might be avaiaible in Splash Page API"
  #  Firewall and Trafficshapping 




async def writeConfigFile(filePath, fileName, fileData):
    
    if filePath.exists() != True:
            filePath.mkdir(parents=True)

    fileWrite = filePath / fileName

    with open(fileWrite, 'w+', encoding='utf-8') as f:
        json.dump(fileData, f, ensure_ascii=False, indent=4)



async def main():

    async with meraki.aio.AsyncDashboardAPI(
        base_url="https://api.meraki.com/api/v1",
        log_file_prefix=__file__[:-3],
        print_console=False,
    ) as aiomeraki:

        for org in organizations:
            orgId = org['id']
            networks = dashboard.organizations.getOrganizationNetworks(orgId)
            if org['api']['enabled'] == True:
                for net in networks:
                    netId = net['id']
                    if 'wireless' in net['productTypes']:

                        wirelessRadioConfig = await wirelessRadio(aiomeraki, netId)
                        wirelessSSIDConfig = await wirelessSSID(aiomeraki, netId)

                        wirelessSSIDdetailsConfig = {}
                        
                        for ssids in wirelessSSIDConfig['ssids']:

                            ssidId = ssids['number']
                            print("SSID Number")
                            print(ssidId)
                            #wirelessSSIDdetailsConfig[ssidId] = {}
                            wirelessSSIDdetailsConfig[ssidId] = await wirelessSSIDdetails(aiomeraki, netId, ssidId)
                                       
                       
                    
                        orgName = org['name']
                        netName = net['name']
                
                        filePath = Path('Org/'+orgName+'-'+orgId+'/Net/'+netName+'-'+netId+'/')

                        await writeConfigFile(filePath, "Wireless-radio.json", wirelessRadioConfig)
                        await writeConfigFile(filePath, "Wireless-ssid.json", wirelessSSIDConfig)
                        await writeConfigFile(filePath, "Wireless-ssidDetails.json", wirelessSSIDdetailsConfig)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
