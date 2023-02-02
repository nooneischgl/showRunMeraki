

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
from pathlib import Path

from asyncio import run_coroutine_threadsafe
from multiprocessing.context import SpawnProcess
from wsgiref.util import setup_testing_defaults
import meraki
import meraki.aio

MERAKI_PYTHON_SDK_CALLER = 'configMeraki'

orgName = "Internet Lifeguard"
orgId = '803699'
netName = "thePeral"
netId = 'L_821343982041694875'

dashboard = meraki.DashboardAPI()


#Internet Lifeguard (organization ID: 803699) 
#thePeral L_821343982041694875

mxInOAC = False
    ## Appliance / MX

        ## Adressing and VLANS
            ## Missing Mode (Route/NAT0 vs VPN Con) and Dnymaic DNS
addressingandVlansConfig = {}

async def addressingandVlans(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, netId:str ) -> Dict[str,int]:
    addressingandVlansConfig.update(applianceSettings = await aiomeraki.appliance.getNetworkApplianceSettings(netId))

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
    addressingandVlansConfig.update(warmSpare = await aiomeraki.appliance.getNetworkApplianceWarmSpare(netId)) 
    
    print(addressingandVlansConfig)
    return addressingandVlansConfig

        ## DHCP
            ## Per S/N

        ## Firewall
            ## Missing IPv6 FW Rules / Polcy Objects - IP Source Address Spoofing protection - Bonjour Forwarding
firewallConfig = {}

async def firewall(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, netId:str ) -> Dict[str,int]:
    firewallConfig.update(inboundFirewall = await aiomeraki.appliance.getNetworkApplianceFirewallInboundFirewallRules(netId))
    firewallConfig.update(l3Firewall = await aiomeraki.appliance.getNetworkApplianceFirewallL3FirewallRules(netId))
    firewallConfig.update(cellularFirewall = await aiomeraki.appliance.getNetworkApplianceFirewallCellularFirewallRules(netId))
    firewallConfig.update(firewallServices = await aiomeraki.appliance.getNetworkApplianceFirewallFirewalledServices(netId))
    firewallConfig.update(l7Firewall = await aiomeraki.appliance.getNetworkApplianceFirewallL7FirewallRules(netId))
    firewallConfig.update(portForwarding = await aiomeraki.appliance.getNetworkApplianceFirewallPortForwardingRules(netId))
    firewallConfig.update(onetoOneNAT = await aiomeraki.appliance.getNetworkApplianceFirewallOneToOneNatRules(netId))
    firewallConfig.update(onetoManyNAT = await aiomeraki.appliance.getNetworkApplianceFirewallOneToManyNatRules(netId))

    print(firewallConfig)
    return firewallConfig

        ## Site to Site VPN
            ##Noting 3rd Party S2S and VPN FW Rules are ORG Wide
sitetoSiteVPNConfig = {}

async def sitetoSiteVPN(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, netId:str ) -> Dict[str,int]:
    sitetoSiteVPNConfig.update(sitetoSiteVPNSettings = await aiomeraki.appliance.getNetworkApplianceVpnSiteToSiteVpn(netId))
    #Need to figureout handleing BGP
    singleLanConfig = ''
    mxInOAC = False
    print("is this the problem")
    try:
        singleLanConfig = await aiomeraki.appliance.getNetworkApplianceSingleLan(netId)
    except:
        if 'Single LAN is not available for networks in passthrough mode' in singleLanConfig:
            mxInOAC = True

    if mxInOAC:
        sitetoSiteVPNConfig.update(vpnBGP = await aiomeraki.appliance.getNetworkApplianceVpnBgp(netId))
    
    print(sitetoSiteVPNConfig)
    return sitetoSiteVPNConfig

        ## Client VPN

        ## Active Directory
            ## No API

        ## SD-WAN and Traffic Shaping  
            ## Missing SD-WAN Policies (Internet Traffic and VPN Traffic) and Web cache

trafficShapingConfig = {}

async def trafficShaping(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, netId:str ) -> Dict[str,int]:
    trafficShapingConfig.update(monitoringDestinations = await aiomeraki.appliance.getNetworkApplianceConnectivityMonitoringDestinations(netId))
    trafficShapingConfig.update(uplinkBandwidth = await aiomeraki.appliance.getNetworkApplianceTrafficShapingUplinkBandwidth(netId))
    
    try:
        trafficShapingConfig.update(uplinkSelection = await aiomeraki.appliance.getNetworkApplianceTrafficShapingUplinkSelection(netId))
    # Catching Error related to Blank Networks  
    except meraki.exceptions.AsyncAPIError as error:
        if str(error.message) != "{'errors': ['Unsupported for networks without a failover capable MX']}":
           raise
        else:
            print("Blank Networks / Non HA MXs "+str(error.status)+str(error.message))

   
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
    return trafficShapingConfig

        ## Treat Protection
            ## Missing Umbrella Protction config
threatProtectionConfig = {}

async def threatProtection(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, netId:str ) -> Dict[str,int]:
    threatProtectionConfig.update(securityIntrusion = await aiomeraki.appliance.getNetworkApplianceSecurityIntrusion(netId))
    threatProtectionConfig.update(securityMaleware= await aiomeraki.appliance.getNetworkApplianceSecurityMalware(netId))

    print(threatProtectionConfig)
    return threatProtectionConfig

        ## Content Filtering 
            ## Missing Search Filtering (Web Search and Restricted Youtube Content)
contentFilteringConfig = {}

async def contentFiltering(aiomeraki: meraki.aio.AsyncDashboardAPI, orgId:str, netId:str ) -> Dict[str,int]:
    contentFilteringConfig.update(applianceContentFiltering = await aiomeraki.appliance.getNetworkApplianceContentFiltering(netId))

    print(contentFilteringConfig )
    return contentFilteringConfig

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
    orgId = orgIdfilter

    if orgIdfilter:
        for org in organizations:
            if orgIdfilter == org['id']:
                 orgName = org['name']
                 orgId = orgIdfilter

    
    networks = dashboard.organizations.getOrganizationNetworks(orgId)
    async with meraki.aio.AsyncDashboardAPI(
        base_url="https://api.meraki.com/api/v1",
        log_path= "./Log/",
        #log_file_prefix=__file__[:-3],
        print_console=False,
    ) as aiomeraki:
        for net in networks:
            netId = net['id']
            if 'appliance' in net['productTypes']:
                if netTag: 
                    if netTag in net['tags']:
                        addressingandVlansConfig = await addressingandVlans(aiomeraki, orgId, netId)
                        firewallConfg = await firewall(aiomeraki, orgId, netId)
                        sitetoSiteVPNConfig = await sitetoSiteVPN(aiomeraki, orgId, netId)
                        trafficShapingConfg = await trafficShaping(aiomeraki, orgId, netId)
                        contentFilteringConfig = await contentFiltering(aiomeraki, orgId, netId)
                else:
                    addressingandVlansConfig = await addressingandVlans(aiomeraki, orgId, netId)
                    firewallConfg = await firewall(aiomeraki, orgId, netId)
                    sitetoSiteVPNConfig = await sitetoSiteVPN(aiomeraki, orgId, netId)
                    trafficShapingConfg = await trafficShaping(aiomeraki, orgId, netId)
                    contentFilteringConfig = await contentFiltering(aiomeraki, orgId, netId)
            
            netName = net['name']

        
            filePath = Path('Org/'+orgName+'-'+orgId+'/Net/'+netName+'-'+netId+'/')

            await writeConfigFile(filePath, "Appliance-addressingandVlans.json", addressingandVlansConfig)
            await writeConfigFile(filePath, "Appliance-firewall.json", firewallConfg)
            await writeConfigFile(filePath, "Appliance-sitetoSiteVPN.json", sitetoSiteVPNConfig)
            await writeConfigFile(filePath, "Appliance-trafficShaping.json", trafficShapingConfg)
            await writeConfigFile(filePath, "Appliance-contentFiltering.json", contentFilteringConfig)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
