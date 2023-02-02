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


#SM General Settings 
async def smSettings(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    smSettingsConfig = {}
    smSettingsConfig.update(smProfiles = await aiomeraki.sm.getNetworkSmProfiles(netId))
    smSettingsConfig.update(smTargetGroups = await aiomeraki.sm.getNetworkSmTargetGroups(netId))
    smSettingsConfig.update(smUsers = await aiomeraki.sm.getNetworkSmUsers(netId))

    returnPackage = {'configName':'SystemsManager-settings.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':smSettingsConfig}

    return returnPackage

#SM Devices Settings 
async def smDeviceSettings(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    smDeviceSettingsConfig = {}
    smDeviceSettingsConfig.update(smDevices = await aiomeraki.sm.getNetworkSmDevices(netId))

    returnPackage = {'configName':'SystemsManager-deviceSettings.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':smDeviceSettingsConfig}

    return returnPackage

#SM Trusted Access
async def smTrustedAccessSettings(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    smTrustedAccessSettingsConfig = {}
    smTrustedAccessSettingsConfig.update(smTrustedAccessConfigs = await aiomeraki.sm.getNetworkSmTrustedAccessConfigs(netId))
    smTrustedAccessSettingsConfig.update(smUserAccessDevices = await aiomeraki.sm.getNetworkSmUserAccessDevices(netId))

    returnPackage = {'configName':'SystemsManager-TrustedAccessSettings.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':smTrustedAccessSettingsConfig}

    return returnPackage
 
async def writeConfigFile(filePath, fileName, fileData):
    
    if filePath.exists() != True:
            filePath.mkdir(parents=True)

    fileWrite = filePath / fileName

    with open(fileWrite, 'w+', encoding='utf-8') as f:
        json.dump(fileData, f, ensure_ascii=False, indent=4)


sensorDeviceConfig = {}
#MG Device Config
async def sensorDeviceConf(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str, deviceSN:str) -> Dict[str,int]:
    
    sensorDeviceConfig[deviceSN] = await aiomeraki.devices.getDevice(deviceSN)
    #sensorDeviceConfig[deviceSN].update(cellularGatewayLan = await aiomeraki.sensor.furuteGets(deviceSN))
   
    returnPackage = {'configName':'Sensor-deviceConfig.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':sensorDeviceConfig}
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
            if netTag:
                networks =  dashboard.organizations.getOrganizationNetworks(orgId, tags = netTag)
            else:
                networks =  dashboard.organizations.getOrganizationNetworks(orgId)
        
            for net in networks:
                netId = net['id']
                if 'systemsManager' in net['productTypes']:

                    orgName = org['name']
                    netName = net['name']

                   
                    taskList.append(smSettings(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(smDeviceSettings(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(smTrustedAccessSettings(aiomeraki, orgId, orgName, netId, netName))


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

        end_timer = time()
        elapsedTime = round(end_timer-start_timer,2)
        print(f"Took a total of {elapsedTime} seconds")



if __name__ == "__main__":
    #loop = asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
