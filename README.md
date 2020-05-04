# ACI Ops
[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/settlej/ACI_Ops)
<p>
Tools to enhance CLI experience replacing slower ACI show commands with additional information.

<strong>WARNING</strong>: Sandbox (sandboxapicdc.cisco.com) for APIC doesn't fully work with ACI Ops, this is due to the fact that the APICs and Fabric are virtual and don't have all the API object returns relating to real equipment.


Tested in 4.0(3d), 4.1(2m), 4.2(1j), 4.2(3l) APIC
This program fully supports Python2 and will be updated to Python3 when ACI's internal platform migrates from Python2.


The entire program uses Python2 Standard Library!  
<strong>No 3rd party modules to import and update!</strong></br>
Program can run on Windows, Mac, and Linux.
Can be ran on local computer or on APIC itself. 
If on the APIC you can store the program in your home directory.
</p>

# New Features!
<p>
1.) Picture showing interfaces like available in GUI with colors reflecting interface status, role, errors
2.) Show recent ports down
3.) Show all endpoints on interface
4.) Auto create span to server session
5.) Option to select EGPs to remove from interfaces
6.) Option to tag or untag EPGs added to interfaces
7.) Show all static routes 
8.) Endpoint Search display physical location if endpoint resides on VPC/PC
9.) Clone access, trunk, or VPC/PC to new interfaces ::Admin state, EPGs (selection possible), Same Leaf selector
10.) Deploy Access, Trunk, or VPC/PC (EPGs, physical, AEP) in single flow
11.) Interface Description and EPG update ::CSV
12.) Show BD > EPG relationships
13.) Troubleshooting tools
</p>

# Features in Development!
1.) Display every contract between EPGs (vrf contracts, Taboo, and Normal EPGs) and filters in detail; in both directions</br>

# Limitations:
 <p>Python2 
 Single Pod-1 deployment
 Only 1u Leafs supported 
 Some features like log pull may not be limited to single pod or 1u leaf.
 </p>

# Setup
<p>
 No requriments besides python 2.7 and ssh
 ACI_Ops can be run on APIC or on local computer
 Recommend location on APIC for ACI_Ops: home folder for user
 Local computer needs to have "ssh" in cmd or bash to use tools module in ACI_Ops
 If running lower than 2.7 ipaddress library will be needed
</p>
<p>
 [OPTIONAL] 
 If you want to run ACI_Ops in a virtualenv for python2.

 (linux) <strong>sudo pip install virtualenv</strong>
 (windows/admin) <strong>pip install virtualenv</strong>
     
 <strong>python -m virtualenv .</strong>
      or
 <strong>python -m virtualenv </strong><em><path/to/virtual/location></em>

 If python2 and python3 on same machine you may need to specify:
 <strong>python2 -m virtualenv .</strong>
 <strong>cd Scripts<br></strong>
 (linux) <strong>source activate</strong>
 (windows) <strong>activate</strong>
 </p>
 
# Installation
<p> git clone https://github.com/settlej/ACI_Ops.git</br>
 </strong>cd ACI_Ops</strong></br>
 <strong>python</strong> or <strong>python2 main_menu.py</strong>
 
If you want to run on APIC copy all files to the user home directory, via SCP/SFTP.
Then run:  <strong>python main_menu.py</strong>
</p>

# Enviroment Variables
 <p>If using running ACI_Ops on local computer, for quick login use these three variables:
 1.) apic
 2.) user
 3.) password
 apic = [ip/hostname]</p>
 
 
# Screen Shots:
![Image of Main Menu](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/Menu.JPG)</br></br>
# Important Fault Summary
![Image of fault_summary](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/fault_summary_example.JPG)</br></br>
# Show vlans per interface
![Image of vlans](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/operationalepgs.png)</br>
![Image of vlan2](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/vlantag.JPG)</br>
# Add EPGs to Multiple Interfaces
![Image of add epgs](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/add_vlans.JPG)</br></br>
# Remove EPGs from Multiple Interfaces
![Image of remove_epgs](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/remove_epgs.JPG)</br></br>
# Better 'show interface status'
![Image of showinterfaces](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/show%20interfaces.JPG)</br></br>
# Find Endpoints with Additional Information
![Image of ip search](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/ipsearch.PNG)</br></br>
# Find Endpoints even when Powered Off
![Image of poweroff](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/vm_poweredoff.PNG)</br></br>
# Gather all logs in timeframe
![Image of time](https://github.com/settlej/Better_ACI_CLI_Tools/blob/master/images/time_example.JPG)
</br>Original Auther: Settlej
