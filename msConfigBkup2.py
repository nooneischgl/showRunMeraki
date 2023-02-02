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



dashboard = meraki.DashboardAPI()

organizations = dashboard.organizations.getOrganizations()


#Switch Routing and DHCP
async def routingDhcp(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    routingDhcpConfig = {}
    routingDhcpConfig.update(switchDhcpServerPolicy = await aiomeraki.switch.getNetworkSwitchDhcpServerPolicy(netId))
    routingDhcpConfig.update(switchDhcpServerPolicyArpInspectionTrustedServers = await aiomeraki.switch.getNetworkSwitchDhcpServerPolicyArpInspectionTrustedServers(netId))
    routingDhcpConfig.update(switchDhcpServerPolicyArpInspectionWarningsByDevice = await aiomeraki.switch.getNetworkSwitchDhcpServerPolicyArpInspectionWarningsByDevice(netId)) 
    routingDhcpConfig.update(switchRoutingMulticastRendezvousPoints = await aiomeraki.switch.getNetworkSwitchRoutingMulticastRendezvousPoints(netId))
    routingDhcpConfig.update(switchRoutingOspf = await aiomeraki.switch.getNetworkSwitchRoutingOspf(netId))
        
    returnPackage = {'configName':'Switch-routing-dhcp.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':routingDhcpConfig}
    print(returnPackage)
    return returnPackage

#Access Control Lists
accessControlListConfig = {}
async def accessControlList(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    accessControlListConfig = {}
    accessControlListConfig.update(switchAccessControlLists = await aiomeraki.switch.getNetworkSwitchAccessControlLists(netId))
    
    
    returnPackage = {'configName':'Switch-acl.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':accessControlListConfig}
    print(returnPackage)
    return returnPackage

#Access Policies
async def accessPolicies(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    accessPoliciesConfig = {}
    accessPoliciesConfig.update(switchAccessPolicies = await aiomeraki.switch.getNetworkSwitchAccessPolicies(netId))
    
    
    returnPackage = {'configName':'Switch-accessPolicies.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':accessPoliciesConfig}
    print(returnPackage)
    return returnPackage

#Port Schedules
async def portSchedules(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    portSchedulesConfig = {}
    portSchedulesConfig.update(switchPortSchedules = await aiomeraki.switch.getNetworkSwitchPortSchedules(netId))
    
    
    returnPackage = {'configName':'Switch-portSchedules.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':portSchedulesConfig}
    print(returnPackage)
    return returnPackage

#Switch AMI
async def alternateManagementInterface(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    alternateManagementInterfacesConfig = {}
    alternateManagementInterfacesConfig.update(switchAlternateManagementInterface = await aiomeraki.switch.getNetworkSwitchAlternateManagementInterface(netId))

    returnPackage = {'configName':'Switch-alternateManagementInterface.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':alternateManagementInterfacesConfig}
    print(returnPackage)
    return returnPackage

#Switch Link Aggregations
async def switchLinkAggregations(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    switchLinkAggregationsConfig = {}
    switchLinkAggregationsConfig.update(switchLinkAggregations = await aiomeraki.switch.getNetworkSwitchLinkAggregations(netId))

    returnPackage = {'configName':'Switch-linkAggregationsConfig.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':switchLinkAggregationsConfig}
    print(returnPackage)
    return returnPackage

#Switch Settings
async def switchSettings(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    switchSettingsConfig = {}
    switchSettingsConfig.update(switchSTP = await aiomeraki.switch.getNetworkSwitchStp(netId))
    switchSettingsConfig.update(switchDscpToCosMappings = await aiomeraki.switch.getNetworkSwitchDscpToCosMappings(netId))
    switchSettingsConfig.update(switchRoutingMulticast = await aiomeraki.switch.getNetworkSwitchRoutingMulticast(netId))
    switchSettingsConfig.update(switchMtu = await aiomeraki.switch.getNetworkSwitchMtu(netId))

    try:
          switchSettingsConfig.update(switchStormControl = await aiomeraki.switch.getNetworkSwitchStormControl(netId))
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))
    

    switchSettingsConfig.update(switchSettings = await aiomeraki.switch.getNetworkSwitchSettings(netId))
        
    returnPackage = {'configName':'Switch-settings.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':switchSettingsConfig}
    print(returnPackage)
    return returnPackage

switchDeviceConfig = {}
#Switch Device Config
async def switchDeviceConf(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str, deviceSN:str) -> Dict[str,int]:
    switchDeviceConfig[deviceSN] = await aiomeraki.devices.getDevice(deviceSN)
    print(switchDeviceConfig)
    switchDeviceConfig[deviceSN].update(switchPorts = await aiomeraki.switch.getDeviceSwitchPorts(deviceSN))
    switchDeviceConfig[deviceSN].update(switchRoutingInterfaces = await aiomeraki.switch.getDeviceSwitchRoutingInterfaces(deviceSN))
    
    try:
        switchDeviceConfig[deviceSN].update(switchRoutingStaticRoutes = await aiomeraki.switch.getDeviceSwitchRoutingStaticRoutes(deviceSN))
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))

    switchDeviceConfig[deviceSN].update(switchWarmSpare = await aiomeraki.switch.getDeviceSwitchWarmSpare(deviceSN))
   
    returnPackage = {'configName':'Switch-deviceConfig.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':switchDeviceConfig}
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
                if 'switch' in net['productTypes']:

                    orgName = org['name']
                    netName = net['name']

                    #acltask = await accessControlList(aiomeraki, orgId, orgName, netId, netName)
                    #print(acltask)
                    taskList.append(accessControlList(aiomeraki, orgId, orgName, netId, netName)) 
                    taskList.append(accessPolicies(aiomeraki, orgId, orgName, netId, netName)) 
                    taskList.append(alternateManagementInterface(aiomeraki, orgId, orgName, netId, netName)) 
                    taskList.append(routingDhcp(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(switchSettings(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(switchLinkAggregations(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(portSchedules(aiomeraki, orgId, orgName, netId, netName))
                    
                    #print(taskList)
                devices = dashboard.networks.getNetworkDevices(netId)

                for device in devices:
                    if device['model'].startswith('MS'):
                        deviceSN = device['serial']
                        taskList.append(switchDeviceConf(aiomeraki, orgId, orgName, netId, netName, deviceSN))
                        


        responses = await asyncio.gather(*taskList)


        #print(responses)
        for response in responses:
            orgId = response['orgId']
            orgName = response['orgName']
            netId = response['netId']
            netName = response['netName']
            
            filePath = Path('Org/'+orgName+'-'+orgId+'/Net/'+netName+'-'+netId+'/')
            print(response['configJson'])
            await writeConfigFile(filePath, response['configName'], response['configJson'])
          
            

            
        #asyncio.as_completed(taskList)
        
        
        end_timer = time()
        elapsedTime = round(end_timer-start_timer,2)
        print(f"Took a total of {elapsedTime} seconds")



if __name__ == "__main__":
    #loop = asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
