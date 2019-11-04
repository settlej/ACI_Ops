#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import json
import ssl
import os
import datetime
import itertools
#import trace
#import pdb
import random
import threading
import Queue
from collections import namedtuple
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define logging handler for file and console logging.  Console logging can be desplayed during
# program run time, similar to print.  Program can display or write to log file if more debug 
# info needed.  DEBUG is lowest and will display all logging messages in program.  
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.CRITICAL)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers.  This creates custom logging format such as timestamp,
# module running, function, debug level, and custom text info (message) like print.
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the parent custom logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

class infraRsStpIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsQosIngressDppIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsStormctrlIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsQosEgressDppIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsMonIfInfraPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsMcpIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsMacsecIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsQosSdIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsAttEntP():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsCdpIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsL2IfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsQosDppIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsCoppIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsQosPfcIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsHIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsL2PortSecurityPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsL2PortAuthPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsLacpPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsFcIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class infraRsLldpIfPol():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


#get vpcs list
def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        allepglist = get_All_EGPs(apic,cookie)
        allpclist = get_All_PCs(apic,cookie)
        allvpclist = get_All_vPCs(apic,cookie)
        clear_screen()
        location_banner('Clone Interface and Deploy')
        selection = interface_menu()
#select vpcs
        if selection == '1':
            chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
            switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_switching')
            returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)

            #returnedlist = physical_selection(all_leaflist, apic, cookie)
            #import pdb; pdb.set_trace()
            chosenepgs, choseninterfaceobjectlist = display_and_select_epgs(returnedlist, allepglist)
            #import pdb; pdb.set_trace()
            interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic)
            print('\r')
            custom_raw_input('#Press enter to continue...')
        elif selection == '2':
            while True:
                returnedlist = port_channel_selection(allpclist)
                if len(returnedlist) > 1:
                    print("\nPlease select on item\n")
                    continue
                else:
                    break
            chosenepgs, choseninterfaceobjectlist = display_and_select_epgs(returnedlist, allepglist)
            interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic, type="Port-Channel")
            #port_channel_selection(allpclist,allepglist)
            print('\r')
            custom_raw_input('#Press enter to continue...')
        elif selection == '3':
            while True:
                returnedlist = port_channel_selection(allvpclist)
                if len(returnedlist) > 1:
                    print("\nPlease select on item\n")
                    continue
                else:
                    break
            url = """https://{apic}/api/node/class/infraAccBndlGrp.json?query-target-filter=eq(infraAccBndlGrp.name, "{vpcname}")&rsp-subtree=full""".format(apic=apic,vpcname=returnedlist[0].name)
            logger.info(url)
            result = GetResponseData(url,cookie)
            for infraAccBndlGrp in result:
               #import pdb; pdb.set_trace()
                vpcpolicy = infraAccBndlGrp['infraAccBndlGrp']['attributes']['dn']
                for policy in infraAccBndlGrp['infraAccBndlGrp']['children']:
                    #import pdb; pdb.set_trace()
                    if policy.get('infraRtAccBaseGrp'):
                        currentleafifselector = policy['infraRtAccBaseGrp']['attributes']['tDn']
            for x in result[0]['infraAccBndlGrp']['attributes'].keys():
                del result[0]['infraAccBndlGrp']['attributes'][x]
            for m in result[0]['infraAccBndlGrp']['children']:
                for t in m:
                    for x in m[t]['attributes'].keys():
                        if x != 'tDn':
                            del m[t]['attributes'][x]
            import pdb; pdb.set_trace()
                   # for m in k['infraAccBndlGrp']['children']:
                   #     for policy in m:
                   # if policy == 'infraRsStpIfPol':
                   #     a = infraRsStpIfPol(**policy['infraRsStpIfPol']['attributes'])
                   # elif policy == 'infraRsQosIngressDppIfPol':
                   #     b  = infraRsQosIngressDppIfPol(**policy['infraRsQosIngressDppIfPol']['attributes'])
                   # elif policy == 'infraRsStormctrlIfPol':
                   #     c  = infraRsStormctrlIfPol(**policy['infraRsStormctrlIfPol']['attributes'])
                   # elif policy == 'infraRsQosEgressDppIfPol':
                   #     d  = infraRsQosEgressDppIfPol(**policy['infraRsQosEgressDppIfPol']['attributes'])
                   # elif policy == 'infraRsMonIfInfraPol':
                   #     e  = infraRsMonIfInfraPol(**policy['infraRsMonIfInfraPol']['attributes'])
                   # elif policy == 'infraRsMcpIfPol':
                   #     f  = infraRsMcpIfPol(**policy['infraRsMcpIfPol']['attributes'])
                   # elif policy == 'infraRsMacsecIfPol':
                   #     g  = infraRsMacsecIfPol(**policy['infraRsMacsecIfPol']['attributes'])
                   # elif policy == 'infraRsQosSdIfPol':
                   #     h  = infraRsQosSdIfPol(**policy['infraRsQosSdIfPol']['attributes'])
                   # elif policy == 'infraRsAttEntP':
                   #     i  = infraRsCdpIfPol(**policy['infraRsCdpIfPol']['attributes'])
                   # elif policy == 'infraRsCdpIfPol':
                   #     j  = infraRsCdpIfPol(**policy['infraRsCdpIfPol']['attributes'])
                   # elif policy == 'infraRsL2IfPol':
                   #     k  = infraRsL2IfPol(**policy['infraRsL2IfPol']['attributes'])
                   # elif policy == 'infraRsQosDppIfPol':
                   #     m  = infraRsQosDppIfPol(**policy['infraRsQosDppIfPol']['attributes'])
                   # elif policy == 'infraRsCoppIfPol':
                   #     n  = infraRsCoppIfPol(**policy['infraRsCoppIfPol']['attributes'])
                   # elif policy == 'infraRsQosPfcIfPol':
                   #     o  = infraRsQosPfcIfPol(**policy['infraRsQosPfcIfPol']['attributes'])
                   # elif policy == 'infraRsHIfPol':
                   #     p  = infraRsHIfPol(**policy['infraRsHIfPol']['attributes'])
                   # elif policy == 'infraRsL2PortSecurityPol':
                   #     q  = infraRsL2PortSecurityPol(**policy['infraRsL2PortSecurityPol']['attributes'])
                   # elif policy == 'infraRsL2PortAuthPol':
                   #     r  = infraRsL2PortAuthPol(**policy['infraRsL2PortAuthPol']['attributes'])
                   # elif policy == 'infraRsLacpPol':
                   #     s  = infraRsLacpPol(**policy['infraRsLacpPol']['attributes'])
                   # elif policy == 'infraRsFcIfPol':
                   #     t  = infraRsFcIfPol(**policy['infraRsFcIfPol']['attributes'])
                   # elif policy == 'infraRsLldpIfPol':
                   #     u  = infraRsLldpIfPol(**policy['infraRsLldpIfPol']['attributes'])



            while True:
                useifselector = custom_raw_input("Use Selected VPC's current leaf interface selector? [y=default|n]: ") or 'y'
                if useifselector.lower().strip().lstrip() == 'y':
                    leafifselector = currentleafifselector.split('/')[2]
                    break
                elif useifselector.lower().strip().lstrip() == 'n':
                    continue
                else:
                    print('\n Invalid Option, try again...\n')
                    continue
            vpcname = custom_raw_input("Name for new VPC: ")
            result[0]['infraAccBndlGrp']['attributes'].update(lagT="node",name="LP_" + str(vpcname))
            vpclocation = custom_raw_input("Interface(s) for new VPC? [format=x/x or x/xx]: ")
            fromCard = vpclocation.split('/')[0]
            toCard = vpclocation.split('/')[0]
            toPort = vpclocation.split('/')[1]
            fromPort = vpclocation.split('/')[1]
            blockname = 'block-' + str(random.randrange(0, 9999))
            #method: POST
#url: https://192.168.255.2/api/node/mo/uni/infra/funcprof/accbundle-deleteme.json
#payload{"infraAccBndlGrp":{"attributes":{"dn":"uni/infra/funcprof/accbundle-deleteme","lagT":"node","name":"deleteme","rn":"accbundle-deleteme","status":"created"},"children":[{"infraRsCdpIfPol":{"attributes":{"tnCdpIfPolName":"CDP_ON","status":"created,modified"},"children":[]}}]}}
            ##https://192.168.255.2/api/node/mo/uni/infra/funcprof/accbundle-Host8.json?rsp-subtree=full
            url = """https://{apic}/api/node/mo/uni/infra/funcprof/accbundle-{vpc}.json""".format(apic=apic,vpc="LP_" + str(vpcname))
            data = json.dumps(result[0])
            result = PostandGetResponseData(url, data, cookie)
            import pdb; pdb.set_trace()
            #apply vpc to interface
            #url = """https://{apic}/api/node/mo/uni/infra/accportprof-Switch101-102_Profile_ifselector/hports-int-test2-typ-range.json""".format(apic=apic,leafifselector=leafifselector,aps=apsname)
            url = """https://{apic}/api/node/mo/uni/infra/{leafifselector}/hports-APS_{vpcname}-typ-range.json""".format(apic=apic,leafifselector=leafifselector,vpcname=vpcname)
            #data = """{"infraHPortS":{"attributes":{"name":"int-test","status":"created,modified"},"children":[{"infraPortBlk":{"attributes":{"fromPort":"40","toPort":"40","name":"block2","status":"created,modified"},"children":[]}},{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accbundle-TEST_VPC","status":"created,modified"},"children":[]}}]}}""" % {toPort:toPort, fromPort:fromPort, blockname:blockname, vpcpolicy=vpcpolicy}
            data = """'{{"infraHPortS":{{"attributes":{{"name":"APS_{vpcname}","status":"created,modified"}},"children":[{{"infraPortBlk":{{"attributes":{{"fromPort":"{fromPort}",\
                "toPort":"{toPort}","fromCard":"{fromCard}","toCard":"{toCard}",name":"{blockname}","status":"created,modified"}},"children":[]}}}},{{"infraRsAccBaseGrp":{{"attributes":{{"tDn":"{vpcpolicy}",\
                "status":"created,modified"}},"children":[]}}}}]}}}}'""".format(toPort=toPort, fromPort=fromPort, fromCard=fromCard, toCard=toCard, blockname=blockname, vpcname=vpcname, vpcpolicy=vpcpolicy)
            result = PostandGetResponseData(url, data, cookie)
            import pdb; pdb.set_trace()
            chosenepgs, choseninterfaceobjectlist = display_and_select_epgs(returnedlist, allepglist)
            interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic, type="vPort-Channel")
            print('\r')
            custom_raw_input('#Press enter to continue...')
#query vpc with name

#get infraRtAccBaseGrp in response and all the relationships to policy groups
#
#display would you like to use same vPC leaf pair.
#    if not
#        which leaf ifselector
#        what is the name of VPC
#    else continue cloning vpc
#        ask what is the name of VPC