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

#Camera Profiles
async def cameraQualityRetentionProfiles(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    cameraQualityRetentionProfilesConfig = {}
    cameraQualityRetentionProfilesConfig.update(cameraQualityRetentionProfiles = await aiomeraki.camera.getNetworkCameraQualityRetentionProfiles(netId))

    returnPackage = {'configName':'Camera-qualityRetentionProfiles.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':cameraQualityRetentionProfilesConfig}
    print(returnPackage)
    return returnPackage

#Camera Schedules
async def cameraSchedules(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
   cameraSchedulesConfig = {}
   cameraSchedulesConfig.update(cameraQualityRetentionProfiles = await aiomeraki.camera.getNetworkCameraSchedules(netId))

   returnPackage = {'configName':'Camera-schedules.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':cameraSchedulesConfig}
   print(returnPackage)
   return returnPackage

#Camera Wireless Profiles
async def cameraWirelessProfilesorkCameraWirelessProfiles(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    cameraWirelessProfilesorkCameraWirelessProfilesConfig = {}
    cameraWirelessProfilesorkCameraWirelessProfilesConfig.update(cameraQualityRetentionProfiles = await aiomeraki.camera.getNetworkCameraWirelessProfiles(netId))

    returnPackage = {'configName':'Camera-wirelessProfile.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':cameraWirelessProfilesorkCameraWirelessProfilesConfig}
    print(returnPackage)
    return returnPackage
 
async def writeConfigFile(filePath, fileName, fileData):
    
    if filePath.exists() != True:
            filePath.mkdir(parents=True)

    fileWrite = filePath / fileName

    with open(fileWrite, 'w+', encoding='utf-8') as f:
        json.dump(fileData, f, ensure_ascii=False, indent=4)

cameraDeviceConfig = {}
#Camera Device Config
async def cameraDeviceConf(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str, deviceSN:str) -> Dict[str,int]:
    cameraDeviceConfig[deviceSN] = await aiomeraki.devices.getDevice(deviceSN)
    print(cameraDeviceConfig)
    cameraDeviceConfig[deviceSN].update(cameraCustomAnalytics = await aiomeraki.camera.getDeviceCameraCustomAnalytics(deviceSN))
    cameraDeviceConfig[deviceSN].update(cameraQualityAndRetention = await aiomeraki.camera.getDeviceCameraQualityAndRetention(deviceSN))
    cameraDeviceConfig[deviceSN].update(cameraSense = await aiomeraki.camera.getDeviceCameraSense(deviceSN))
    cameraDeviceConfig[deviceSN].update(cameraSenseObjectDetectionModels = await aiomeraki.camera.getDeviceCameraSenseObjectDetectionModels(deviceSN))
    cameraDeviceConfig[deviceSN].update(cameraVideoSettings = await aiomeraki.camera.getDeviceCameraVideoSettings(deviceSN))
    cameraDeviceConfig[deviceSN].update(cameraSenseObjectDetectionModels = await aiomeraki.camera.getDeviceCameraSenseObjectDetectionModels(deviceSN))

    returnPackage = {'configName':'Camera-deviceConfig.json','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':cameraDeviceConfig}
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
                if 'camera' in net['productTypes']:

                    orgName = org['name']
                    netName = net['name']

                    #acltask = await accessControlList(aiomeraki, orgId, orgName, netId, netName)
                    #print(acltask)
                    taskList.append(cameraQualityRetentionProfiles(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(cameraSchedules(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(cameraWirelessProfilesorkCameraWirelessProfiles(aiomeraki, orgId, orgName, netId, netName))
                    #print(taskList)

                    devices = dashboard.networks.getNetworkDevices(netId)

                    for device in devices:
                        if device['model'].startswith('MV'):
                            deviceSN = device['serial']
                            taskList.append(cameraDeviceConf(aiomeraki, orgId, orgName, netId, netName, deviceSN))
                        


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
