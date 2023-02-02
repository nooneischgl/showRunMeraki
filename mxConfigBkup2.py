

import csv
from datetime import datetime, timedelta
import os
import asyncio
import argparse
import ipaddress
from typing import Dict,List
import sys
import certifi
import json
from time import *
from pathlib import Path

from asyncio import run_coroutine_threadsafe
from multiprocessing.context import SpawnProcess
from wsgiref.util import setup_testing_defaults
import meraki
import meraki.aio

MERAKI_PYTHON_SDK_CALLER = 'configMeraki'

#orgName = "Internet Lifeguard"
#orgId = '803699'
#netName = "thePeral"
#netId = 'L_821343982041694875'

dashboard = meraki.DashboardAPI()


#Internet Lifeguard (organization ID: 803699) 
#thePeral L_821343982041694875

mxInOAC = False
    ## Appliance / MX

        ## Adressing and VLANS
            ## Missing Mode (Route/NAT0 vs VPN Con) and Dnymaic DNS
addressingandVlansConfig = {}

async def addressingandVlans(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str ) -> Dict[str,int]:
    try:
        addressingandVlansConfig.update(applianceSettings = await aiomeraki.appliance.getNetworkApplianceSettings(netId))
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))

    vlanSettings = await aiomeraki.appliance.getNetworkApplianceVlansSettings(netId)
    print(vlanSettings)
    if vlanSettings['vlansEnabled']:
        #VLANs Enabled
        print("VLANS ENABLED")
        try:
            addressingandVlansConfig.update(vlanConfig = await aiomeraki.appliance.getNetworkApplianceVlans(netId))
        except meraki.exceptions.AsyncAPIError as error:
            if str(error.message) not in ["{'errors': ['VLANs are not enabled for this network']}"]:
                raise
            else:
                print("Blank Networks / VLANs not enabled fopr this network "+str(error.status)+str(error.message))
        try:
            addressingandVlansConfig.update(appliancePorts = await aiomeraki.appliance.getNetworkAppliancePorts(netId))
        except meraki.exceptions.AsyncAPIError as error:
            if str(error.message) not in ["{'errors': ['VLANs are not enabled for this network']}","{'errors': ['No appliance linked to this network']}"]:
                raise
            else:
                print("Blank Networks / VLANs not enabled fopr this network "+str(error.status)+str(error.message))
                
    elif 'false' in str(vlanSettings):
        #Single VLAN 
        addressingandVlansConfig.update(singleLanConfig = await aiomeraki.appliance.getNetworkApplianceSingleLan(netId))
  

    try: 
        addressingandVlansConfig.update(staticRoutes = await aiomeraki.appliance.getNetworkApplianceStaticRoutes(netId)) 
    except:
        print("unsuppoed for netowrks not in Routed Mode")
    
    try:
        addressingandVlansConfig.update(warmSpare = await aiomeraki.appliance.getNetworkApplianceWarmSpare(netId))
    except:
        print("here") 

    print(addressingandVlansConfig)

    returnPackage = {'configName':'Appliance-addressingandVlansConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':addressingandVlansConfig}
    return returnPackage

        ## DHCP
            ## Per S/N

        ## Firewall
            ## Missing IPv6 FW Rules / Polcy Objects - IP Source Address Spoofing protection - Bonjour Forwarding
firewallConfig = {}

async def firewall(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str ) -> Dict[str,int]:
    firewallConfig.update(inboundFirewall = await aiomeraki.appliance.getNetworkApplianceFirewallInboundFirewallRules(netId))
    firewallConfig.update(l3Firewall = await aiomeraki.appliance.getNetworkApplianceFirewallL3FirewallRules(netId))
    firewallConfig.update(cellularFirewall = await aiomeraki.appliance.getNetworkApplianceFirewallCellularFirewallRules(netId))
    firewallConfig.update(firewallServices = await aiomeraki.appliance.getNetworkApplianceFirewallFirewalledServices(netId))
    firewallConfig.update(l7Firewall = await aiomeraki.appliance.getNetworkApplianceFirewallL7FirewallRules(netId))
    firewallConfig.update(portForwarding = await aiomeraki.appliance.getNetworkApplianceFirewallPortForwardingRules(netId))
    firewallConfig.update(onetoOneNAT = await aiomeraki.appliance.getNetworkApplianceFirewallOneToOneNatRules(netId))
    firewallConfig.update(onetoManyNAT = await aiomeraki.appliance.getNetworkApplianceFirewallOneToManyNatRules(netId))

    print(firewallConfig)

    returnPackage = {'configName':'Appliance-firewallConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':firewallConfig}
    return returnPackage

        ## Site to Site VPN
            ##Noting 3rd Party S2S and VPN FW Rules are ORG Wide
sitetoSiteVPNConfig = {}

async def sitetoSiteVPN(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str ) -> Dict[str,int]:
    sitetoSiteVPNConfig.update(sitetoSiteVPNSettings = await aiomeraki.appliance.getNetworkApplianceVpnSiteToSiteVpn(netId))
    #Need to figureout handleing BGP
    singleLanConfig = ''
    mxInOAC = False
    print("is this the problem")
    try:
        singleLanConfig = await aiomeraki.appliance.getNetworkApplianceSingleLan(netId)
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))
    except:
        if 'Single LAN is not available for networks in passthrough mode' in singleLanConfig:
            mxInOAC = True

    try:
        sitetoSiteVPNConfig.update(vpnBGP = await aiomeraki.appliance.getNetworkApplianceVpnBgp(netId))
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))
    
    print(sitetoSiteVPNConfig)

    returnPackage = {'configName':'Appliance-sitetoSiteVPNConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':sitetoSiteVPNConfig}
    return returnPackage

        ## Client VPN

        ## Active Directory
            ## No API

        ## SD-WAN and Traffic Shaping  
            ## Missing SD-WAN Policies (Internet Traffic and VPN Traffic) and Web cache

trafficShapingConfig = {}

async def trafficShaping(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str ) -> Dict[str,int]:
    try:
        trafficShapingConfig.update(monitoringDestinations = await aiomeraki.appliance.getNetworkApplianceConnectivityMonitoringDestinations(netId))
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))

    try:
        trafficShapingConfig.update(uplinkBandwidth = await aiomeraki.appliance.getNetworkApplianceTrafficShapingUplinkBandwidth(netId))
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))
    
    try:
        trafficShapingConfig.update(uplinkSelection = await aiomeraki.appliance.getNetworkApplianceTrafficShapingUplinkSelection(netId))
    # Catching Error related to Blank Networks  
    except meraki.exceptions.AsyncAPIError as error:
        print(str(error.status)+str(error.message))

   
    try:
        trafficShapingConfig.update(trafficShapingRules = await aiomeraki.appliance.getNetworkApplianceTrafficShapingRules(netId))
    # Catching Error related to Blank Network / Non HA MX 
    except meraki.exceptions.AsyncAPIError as error:
        print("Err0r")
        print(str(error.message))
        if str(error.message) not in ["{'errors': ['Unsupported for networks without a failover capable MX']}", "{'errors': ['Unsupported for networks bound to a template']}"]:
           raise
        else:
            print("Blank Networks / Non HA MXs or Networks Bound to Template "+str(error.status)+str(error.message))
    
    
    try:
        trafficShapingConfig.update(customPerformanceClasses = await aiomeraki.appliance.getNetworkApplianceTrafficShapingCustomPerformanceClasses(netId))
    # Catching Error related to Blank Network / Non HA MX 
    except meraki.exceptions.AsyncAPIError as error:
        if str(error.message) not in ["{'errors': ['Unsupported for networks without a failover capable MX']}", "{'errors': ['Unsupported for networks bound to a template']}", "{'errors': ['Unsupported for networks without routed mode (NAT) enabled']}"]:
           raise
        else:
            print("Blank Networks / Non HA MXs or Networks Bound to Template / In OAC "+str(error.status)+str(error.message))
    
    try:
        trafficShapingConfig.update(globalTrafficShaping= await aiomeraki.appliance.getNetworkApplianceTrafficShaping(netId))
        # Catching Error related to Templated Networks  
    except meraki.exceptions.AsyncAPIError as error:
        if str(error.message) != "{'errors': ['Unsupported for networks bound to a template']}":
           raise
        else:
            print("Blank Networks / Non HA MXs "+str(error.status)+str(error.message))

    print(trafficShapingConfig)

    returnPackage = {'configName':'Appliance-trafficShapingConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':trafficShapingConfig}
    return returnPackage    

        ## Treat Protection
            ## Missing Umbrella Protction config
threatProtectionConfig = {}

async def threatProtection(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str) -> Dict[str,int]:
    threatProtectionConfig.update(securityIntrusion = await aiomeraki.appliance.getNetworkApplianceSecurityIntrusion(netId))
    threatProtectionConfig.update(securityMaleware= await aiomeraki.appliance.getNetworkApplianceSecurityMalware(netId))

    print(threatProtectionConfig)

    returnPackage = {'configName':'Appliance-threatProtectionConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':threatProtectionConfig}
    return returnPackage

        ## Content Filtering 
            ## Missing Search Filtering (Web Search and Restricted Youtube Content)
contentFilteringConfig = {}

async def contentFiltering(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, orgName:str, netId:str, netName:str ) -> Dict[str,int]:
    contentFilteringConfig.update(applianceContentFiltering = await aiomeraki.appliance.getNetworkApplianceContentFiltering(netId))

    print(contentFilteringConfig )
    returnPackage = {'configName':'Appliance-contentFilteringConfig','orgId': orgId,'orgName': orgName, 'netId': netId, 'netName': netName, 'configJson':contentFilteringConfig}
    return returnPackage
    

        ## Access Control 
            ## NO API

        ## Splash Page
             ## NO API

        ## Wireless Concentrator
             ## NO API


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

        print("Made it to the MX Config")

        start_timer = time()
        taskList = []   

        for org in organizations:
            orgId = org['id']    
            print(netTag)
            if netTag:
                networks =  dashboard.organizations.getOrganizationNetworks(orgId, tags = netTag)
                
            else:
                networks =  dashboard.organizations.getOrganizationNetworks(orgId)

            for net in networks:
                netId = net['id']
                if 'appliance' in net['productTypes']:

                    orgName = org['name']
                    netName = net['name']

                    taskList.append(addressingandVlans(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(firewall(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(sitetoSiteVPN(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(trafficShaping(aiomeraki, orgId, orgName, netId, netName))
                    taskList.append(contentFiltering(aiomeraki, orgId, orgName, netId, netName))
        
 
        responses = await asyncio.gather(*taskList)

    
        for response in responses:
            orgId = response['orgId']
            orgName = response['orgName']
            netId = response['netId']
            netName = response['netName']
                
            filePath = Path('Org/'+orgName+'-'+orgId+'/Net/'+netName+'-'+netId+'/')
            await writeConfigFile(filePath, response['configName'], response['configJson'])

    end_timer = time()
    elapsedTime = round(end_timer-start_timer,2)
    print(f"Took a total of {elapsedTime} seconds")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
