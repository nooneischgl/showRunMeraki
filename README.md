# ShowRunMeraki

```Show run meraki``` is intended to be a project that backs up all your Meraki configuration into a single repository. We work to support as many possible enviroemtns and configurations as possible but please report and errors using the Issues and provice releavnt errors. 

```Show run meraki``` can be run locally as a one time back up intergratied with GitLab CI/CD for nightly backups. 

## Privacy NOTICE 
This script will back up Pre Share Keys, Shared Secrets .... in plain text, UNencrypted. 

# Backs up your Meraki Dashbard config 


File Structure 
```
    .
    ├── Org
    |   ├── <OrgName-OrgID> 
    |       ├── <Organzation-Org-WideConfigFiles.json>
    |       ├── <Net>
    |           ├── <NetworkName-NetworkID>
    |              ├── <Appliance-SDWAN&SecuirtyConfig.json>
    |              └── <Wireless-WirelessConfig.json>
```

- Org Wide
- Network Wide
- Network Specfic (API calls / configuration that are not tied to a specific Serial Number)
  - In General try to have a .json file for ever configuration page 
- Device Specific (API calls and configuration that is tied to a specific Sieral Number)

## Activate venv
#### PowerShell / Windows 
``` .venv/Scripts/Activate.ps1 ```
#### macOS / Linux
``` source .venv/bin/activate ```

## Set API Key
#### PowerShell / Windows 
``` $Env:MERAKI_DASHBOARD_API_KEY = "APIKeyHere"```

#### macOS / Linux
```export MERAKI_DASHBOARD_API_KEY=APIKeyHere```

## Run Show Run Meraki 
- With the venv active and API Key Set 
```python showRunMeraki.py ```