from typing import Dict,List
import asyncio
from pathlib import Path
import json

import meraki
import meraki.aio

MERAKI_PYTHON_SDK_CALLER = 'configMeraki'



dashboard = meraki.DashboardAPI()

#networks = dashboard.organizations.getOrganizationNetworks(orgId)

#Internet Lifeguard (organization ID: 803699) 
#thePeral L_821343982041694875

orgSettingsConfig = {}
async def orgSettings(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    orgSettingsConfig.update(orgLoginSecuirty = await aiomeraki.organizations.getOrganizationLoginSecurity(orgId))
    orgSettingsConfig.update(orgSaml = await aiomeraki.organizations.getOrganizationSaml(orgId))
    orgSettingsConfig.update(orgAlerts = await aiomeraki.organizations.getOrganizationAlertsProfiles(orgId))
    orgSettingsConfig.update(orgSnmp = await aiomeraki.organizations.getOrganizationSnmp(orgId))
   

    print(orgSettingsConfig )
    return orgSettingsConfig

administratorsConfig = {}
async def administrators(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    administratorsConfig.update(admins = await aiomeraki.organizations.getOrganizationAdmins(orgId))
    administratorsConfig.update(samlRoles = await aiomeraki.organizations.getOrganizationSamlRoles(orgId))

    print(administratorsConfig )
    return administratorsConfig

licenseConfig = {}
async def licenses(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    ##PDL is NOT Supported
    
    try:
        licenseConfig.update(licenses = await aiomeraki.organizations.getOrganizationLicenses(orgId))
    except meraki.exceptions.AsyncAPIError as error:
        if "does not support per-device licensing" not in str(error.message) :
           raise
        else:
            print("PDL Not Supported"+str(error.status)+str(error.message))

    print(licenseConfig)
    return licenseConfig

inventoryConfig = {}
async def inventory(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    inventoryConfig.update(devices = await aiomeraki.organizations.getOrganizationDevices(orgId))

    print(inventoryConfig)
    return inventoryConfig

configTemplatesConfig = {}
async def configTemplates(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    configTemplatesConfig.update(configTemplates = await aiomeraki.organizations.getOrganizationConfigTemplates(orgId))

    print(configTemplatesConfig)
    return configTemplatesConfig

networkConfig = {}
async def orgNetworks(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    networkConfig.update(orgNetworks = await aiomeraki.organizations.getOrganizationNetworks(orgId))

    print(networkConfig)
    return networkConfig

brandingConfig = {}
async def orgBranding(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    try: 
        brandingConfig.update(orgBranding = await aiomeraki.organizations.getOrganizationBrandingPolicies(orgId))
    except meraki.exceptions.AsyncAPIError as error:
       if int(error.status) != 400:
          raise
       else:
           print("Branding Not Supported in this Org"+str(error.status)+str(error.message))
    

    print(brandingConfig)
    return brandingConfig

adaptivePolicyConfig = {}
async def adaptivePolicy(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str) -> Dict[str,int]:
    aiomeraki.organizations.getOrganizationAdaptivePolicyAcls
    adaptivePolicyConfig.update(adaptivePolicyAclsConfig = await aiomeraki.organizations.getOrganizationAdaptivePolicyAcls(orgId))
    adaptivePolicyConfig.update(adaptivePolicyGroupsConfig = await aiomeraki.organizations.getOrganizationAdaptivePolicyGroups(orgId))
    adaptivePolicyConfig.update(adaptivePolicyPoliciesConfig = await aiomeraki.organizations.getOrganizationAdaptivePolicyPolicies(orgId))
    adaptivePolicyConfig.update(adaptivePolicySettingsConfig = await aiomeraki.organizations.getOrganizationAdaptivePolicySettings(orgId))

    print(adaptivePolicyConfig )
    return adaptivePolicyConfig





async def writeConfigFile(filePath, fileName, fileData):
    
    if filePath.exists() != True:
            filePath.mkdir(parents=True)

    fileWrite = filePath / fileName

    with open(fileWrite, 'w+', encoding='utf-8') as f:
        json.dump(fileData, f, ensure_ascii=False, indent=4)



async def main(orgIdfilter=False):

    organizations = dashboard.organizations.getOrganizations()
     
     
    if orgIdfilter:
        for org in organizations:
            if orgIdfilter == org['id']:
                 orgName = org['name']

    async with meraki.aio.AsyncDashboardAPI(
        base_url="https://api.meraki.com/api/v1",
        log_path= "Log",
        #log_file_prefix=__file__[:-3],
        print_console=False,
    ) as aiomeraki:
        if orgIdfilter:
            orgId = orgIdfilter
            
            if org['api']['enabled'] == True:
                adaptivePolicyConfig = await adaptivePolicy(aiomeraki, orgId)
                orgSettingsConfig = await orgSettings(aiomeraki, orgId)
                administratorsConfig = await administrators(aiomeraki, orgId)
                licenseConfig = await licenses(aiomeraki, orgId) 
                inventoryConfig = await inventory(aiomeraki, orgId)
                configTemplatesConfig = await configTemplates(aiomeraki, orgId)
                networkConfig = await orgNetworks(aiomeraki, orgId)
                brandingConfig = await orgBranding(aiomeraki, orgId)
                
        else: 
            for org in organizations:
                orgId = org['id']
                orgName = org['name']
                if org['api']['enabled'] == True:
                    adaptivePolicyConfig = await adaptivePolicy(aiomeraki, orgId)
                    orgSettingsConfig = await orgSettings(aiomeraki, orgId)
                    administratorsConfig = await administrators(aiomeraki, orgId)
                    licenseConfig = await licenses(aiomeraki, orgId) 
                    inventoryConfig = await inventory(aiomeraki, orgId)
                    configTemplatesConfig = await configTemplates(aiomeraki, orgId)
                    networkConfig = await orgNetworks(aiomeraki, orgId)
                    brandingConfig = await orgBranding(aiomeraki, orgId)

            
        

        filePath = Path('Org/'+orgName+'-'+orgId+'/')

        await writeConfigFile(filePath, "Organization-adaptivepolicy.json", adaptivePolicyConfig)
        await writeConfigFile(filePath, "Organization-settings.json", orgSettingsConfig)
        await writeConfigFile(filePath, "Organization-administrator.json", administratorsConfig)
        await writeConfigFile(filePath, "Organization-licenses.json", licenseConfig)  
        await writeConfigFile(filePath, "Organization-inventory.json", inventoryConfig)
        await writeConfigFile(filePath, "Organization-configtemplates.json", configTemplatesConfig)
        await writeConfigFile(filePath, "Organization-networks.json", networkConfig)
        await writeConfigFile(filePath, "Organization-networks.json", brandingConfig)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
