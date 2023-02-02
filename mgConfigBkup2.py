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


#MG Settings 
async def cellularGatewaySettings(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    cellularGatewaySettingssConfig = {}
    cellularGatewaySettingssConfig.update(cellularGatewayConnectivityMonitoringDestinations = await aiomeraki.cellularGateway.getNetworkCellularGatewayConnectivityMonitoringDestinations(netId))
    cellularGatewaySettingssConfig.update(cellularGatewayDhcp = await aiomeraki.cellularGateway.getNetworkCellularGatewayDhcp(netId))
    cellularGatewaySettingssConfig.update(cellularGatewaySubnetPool = await aiomeraki.cellularGateway.getNetworkCellularGatewaySubnetPool(netId))
    cellularGatewaySettingssConfig.update(cellularGatewayUplink = await aiomeraki.cellularGateway.getNetworkCellularGatewayUplink(netId))

    returnPackage = {'configName':'CellularGateway-settings.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':cellularGatewaySettingssConfig}
    print(returnPackage)
    return returnPackage


 
async def writeConfigFile(filePath, fileName, fileData):
    
    if filePath.exists() != True:
            filePath.mkdir(parents=True)

    fileWrite = filePath / fileName

    with open(fileWrite, 'w+', encoding='utf-8') as f:
        json.dump(fileData, f, ensure_ascii=False, indent=4)


#MG Device Config
async def cellularDeviceConf(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str, deviceSN:str) -> Dict[str,int]:
    cellularDeviceConfig = {}
    cellularDeviceConfig[deviceSN] = await aiomeraki.devices.getDevice(deviceSN)
    print(cellularDeviceConfig)
    cellularDeviceConfig[deviceSN].update(cellularGatewayLan = await aiomeraki.cellularGateway.getDeviceCellularGatewayLan(deviceSN))
    cellularDeviceConfig[deviceSN].update(cellularGatewayPortForwardingRules = await aiomeraki.cellularGateway.getDeviceCellularGatewayPortForwardingRules(deviceSN))

    returnPackage = {'configName':'Cellular-deviceConfig.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':cellularDeviceConfig}
    print(returnPackage)
    return returnPackage



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
                if 'cellularGateway' in net['productTypes']:

                    orgName = org['name']
                    netName = net['name']

                    #acltask = await accessControlList(aiomeraki, orgId, orgName, netId, netName)
                    #print(acltask)
                    taskList.append(cellularGatewaySettings(aiomeraki, orgId, orgName, netId, netName))
                   
                    #print(taskList)

                    devices = dashboard.networks.getNetworkDevices(netId)

                    for device in devices:
                        if device['model'].startswith('MG'):
                            deviceSN = device['serial']
                            taskList.append(cellularDeviceConf(aiomeraki, orgId, orgName, netId, netName, deviceSN))
                        


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
