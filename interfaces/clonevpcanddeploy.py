#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import time
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

#class infraRsStpIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsQosIngressDppIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsStormctrlIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsQosEgressDppIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsMonIfInfraPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsMcpIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsMacsecIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsQosSdIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsAttEntP():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsCdpIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsL2IfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsQosDppIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsCoppIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsQosPfcIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsHIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsL2PortSecurityPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsL2PortAuthPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsLacpPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsFcIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#
#class infraRsLldpIfPol():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)

policygrouplist = (
                    "tnStpIfPolName",
                    "tnQosDppPolName",
                    "tnStormctrlIfPolName",
                    "tnMonInfraPolName",
                    "tnMcpIfPolName",
                    "tnMacsecIfPolName",
                    "tnQosSdIfPolName",
                    "tnCdpIfPolName",
                    "tnL2IfPolName",
                    "tnQosDppIfPolName",
                    "tnCoppIfPolName",
                    "tnQosPfcIfPolName",
                    "tnFabricHIfPolName",
                    "tnL2PortSecurityPolName",
                    "tnL2PortAuthPolName",
                    "tnLacpLagPolName",
                    "tnFcIfPolName",
                    "tnLldpIfPolName"
                    )

def interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic, type="Physical"):
    while True:
        print('What is the inteface epg mode?:\n\n'
              + '**Use either 1 for trunks ports and 2 for normal access ports\n\n' 
              + '1.) Trunk\n'
              + '2.) Access\n'
              + '3.) Untagged\n')
        askepgtype = custom_raw_input("Which mode? [default=1]: ") or '1'
        if askepgtype == '1':
            epg_type = 'trunk_port'
            break
        elif askepgtype == '2':
            epg_type = 'access_port'
            break
        elif askepgtype == '3':
            epg_type = 'untagged_port'
            break
        else:
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue
        
    urllist, confirmationlist =  vlan_and_url_generating(chosenepgs,choseninterfaceobjectlist, apic, epg_type)
    print('')
    print('Please Confirm deployment:\n')
    for confirm in confirmationlist:
        print('{epg} with vlan {vlan}'.format(epg=confirm[1],vlan=confirm[2]))
        for interface in confirm[0]:
            print('{}'.format(interface))
        print('')
    while True:
        verify = custom_raw_input('Continue? [y|n]: ')
        if verify == '':
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue
        elif verify[0].lower() == 'y':
            break
        elif verify[0].lower() == 'n':
            raise KeyboardInterrupt
        else:
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue    
    add_egps_to_interfaces(urllist, type, cookie)

def vlan_and_url_generating(chosenepgs,choseninterfaceobjectlist, apic, epg_type):
    urllist = []
    confirmationlist = []
    for epg in sorted(chosenepgs):
        url = """https://{apic}/api/node/mo/{}.json""".format(epg,apic=apic)
        logger.info(url)
        print("\nProvide a vlan number for epg: {}".format(epgformater(epg)))
        while True:
            try:
                vlan = custom_raw_input('vlan number [1-3899]: ')
                print('\r')
                if vlan.isdigit() and vlan.strip().lstrip() != '' and int(vlan) > 0 and int(vlan) < 4096:
                   break
                else:
                    print('Invalid vlan number')
            except ValueError:
                continue
        for interface in sorted(choseninterfaceobjectlist):
            if epg_type == 'trunk_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","instrImedcy":"immediate",\
                     "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface,vlan=vlan)
            elif epg_type == 'access_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","mode":"native","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface,vlan=vlan)
            elif epg_type == 'untagged_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","mode":"untagged","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface,vlan=vlan)
            urlmodify = namedtuple('urlmodify', ('url', 'interface', 'data'))
            urllist.append(urlmodify(url, interface, data))
        confirmationlist.append((choseninterfaceobjectlist,epg, vlan))
    return urllist, confirmationlist

def add_egps_to_interfaces(urllist, interfacetype, cookie):
    queue = Queue.Queue()
    threadlist = []
    queuelist = []
    for url in urllist:
        t = threading.Thread(target=submit_add_post_request, args=(url,interfacetype,queue, cookie))
        t.daemon = True
        #t.setDaemon(True)
        t.start()
        threadlist.append(t)
    for t in threadlist:
        t.join()
        queuelist.append(queue.get())
    for q in sorted(queuelist):
        print(q)

def submit_add_post_request(url,interfacetype,queue, cookie):
    result, error = PostandGetResponseData(url.url, url.data, cookie)
    logger.info(result)
    logger.info(error)
    shorturl = url.url[30:-5]
    if error == None and result == []:
        finalresult = 'Success! -- Added ' + shorturl + ' > ' + str(url.interface)
        queue.put(finalresult)
        logger.debug('{} modify: {}'.format(interfacetype, finalresult))
    elif result == 'invalid':
        logger.error('{} modify: {}'.format(interfacetype, error))
        interfacepath = re.search(r'\[.*\]', error)
        if 'already exists' in error:
            queue.put('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + ' > ' + url.interface.dn + '\t -- EPG already on Interface ')# + interfacepath.group())    
        else:
            queue.put('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + '\t -- ' + error)
    else:
        logger.error('{} modify: {}'.format(interfacetype, error))
        print(error)


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
                #vpcpolicy = infraAccBndlGrp['infraAccBndlGrp']['attributes']['dn']
                for policy in infraAccBndlGrp['infraAccBndlGrp']['children']:
                    #import pdb; pdb.set_trace()
                    if policy.get('infraRtAccBaseGrp'):
                        currentleafifselector = policy['infraRtAccBaseGrp']['attributes']['tDn']
            for x in result[0]['infraAccBndlGrp']['attributes'].keys():
                del result[0]['infraAccBndlGrp']['attributes'][x]
            for m in result[0]['infraAccBndlGrp']['children']:
                for t in m.keys():
                    if t == 'infraRtAccBaseGrp':
                        #del result[0]['infraAccBndlGrp']['children'][num]
                        del m[t]
                    else:
                        for x in m[t]['attributes'].keys():
                            if t == 'infraRsAttEntP':
                                if x != 'tDn':
                                    del m[t]['attributes'][x]
                            elif x not in policygrouplist:
                                del m[t]['attributes'][x]
            result[0]['infraAccBndlGrp']['children'] = filter(None, result[0]['infraAccBndlGrp']['children'])
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
#{"infraRsLacpPol":{"attributes":{"tnLacpLagPolName":"STATIC_ON"}}}
#{"infraRsLacpPol":{"attributes":{"tnLacpLagPolName":"STATIC_ON"}}}
#payload"{"infraAccBndlGrp":{"attributes":{"dn":"uni/infra/funcprof/accbundle-cat","lagT":"node","name":"cat"},"children":[{"infraRsLldpIfPol":{"attributes":{"rn":"rslldpIfPol","dn":"uni/infra/funcprof/accbundle-cat/rslldpIfPol"},"children":[]}},{"infraRsFcIfPol":{"attributes":{"rn":"rsfcIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsfcIfPol"},"children":[]}},{"infraRsLacpPol":{"attributes":{"rn":"rslacpPol","tnLacpLagPolName":"STATIC_ON","dn":"uni/infra/funcprof/accbundle-cat/rslacpPol"},"children":[]}},{"infraRsL2PortAuthPol":{"attributes":{"rn":"rsl2PortAuthPol","dn":"uni/infra/funcprof/accbundle-cat/rsl2PortAuthPol"},"children":[]}},{"infraRsL2PortSecurityPol":{"attributes":{"rn":"rsl2PortSecurityPol","dn":"uni/infra/funcprof/accbundle-cat/rsl2PortSecurityPol"},"children":[]}},{"infraRsHIfPol":{"attributes":{"rn":"rshIfPol","dn":"uni/infra/funcprof/accbundle-cat/rshIfPol"},"children":[]}},{"infraRsQosPfcIfPol":{"attributes":{"rn":"rsqosPfcIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsqosPfcIfPol"},"children":[]}},{"infraRsCoppIfPol":{"attributes":{"rn":"rscoppIfPol","dn":"uni/infra/funcprof/accbundle-cat/rscoppIfPol"},"children":[]}},{"infraRsQosDppIfPol":{"attributes":{"rn":"rsqosDppIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsqosDppIfPol"},"children":[]}},{"infraRsL2IfPol":{"attributes":{"rn":"rsl2IfPol","dn":"uni/infra/funcprof/accbundle-cat/rsl2IfPol"},"children":[]}},{"infraRsStpIfPol":{"attributes":{"rn":"rsstpIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsstpIfPol"},"children":[]}},{"infraRsQosIngressDppIfPol":{"attributes":{"rn":"rsQosIngressDppIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsQosIngressDppIfPol"},"children":[]}},{"infraRsMacsecIfPol":{"attributes":{"rn":"rsmacsecIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsmacsecIfPol"},"children":[]}},{"infraRsStormctrlIfPol":{"attributes":{"rn":"rsstormctrlIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsstormctrlIfPol"},"children":[]}},{"infraRsQosEgressDppIfPol":{"attributes":{"rn":"rsQosEgressDppIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsQosEgressDppIfPol"},"children":[]}},{"infraRsMonIfInfraPol":{"attributes":{"rn":"rsmonIfInfraPol","dn":"uni/infra/funcprof/accbundle-cat/rsmonIfInfraPol"},"children":[]}},{"infraRsMcpIfPol":{"attributes":{"rn":"rsmcpIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsmcpIfPol"},"children":[]}},{"infraRsAttEntP":{"attributes":{"rn":"rsattEntP","tDn":"uni/infra/attentp-AEP_VMM","dn":"uni/infra/funcprof/accbundle-cat/rsattEntP"},"children":[]}},{"infraRsQosSdIfPol":{"attributes":{"rn":"rsqosSdIfPol","dn":"uni/infra/funcprof/accbundle-cat/rsqosSdIfPol"},"children":[]}},{"infraRsCdpIfPol":{"attributes":{"rn":"rscdpIfPol","tnCdpIfPolName":"CDP_ON","dn":"uni/infra/funcprof/accbundle-cat/rscdpIfPol"},"children":[]}}]}}"

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
            result[0]['infraAccBndlGrp']['attributes'].update(lagT="node",name="LP_" + str(vpcname),status="created,modified")
            vpcpolicy = "uni/infra/funcprof/accbundle-LP_" + vpcname
            vpclocation = custom_raw_input("Interface(s) for new VPC? [format=x/x or x/xx]: ")
            fromCard = vpclocation.split('/')[0].replace('eth', '')
            toCard = vpclocation.split('/')[0].replace('eth', '')
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
            #import pdb; pdb.set_trace()
            #apply vpc to interface
            #url = """https://{apic}/api/node/mo/uni/infra/accportprof-Switch101-102_Profile_ifselector/hports-int-test2-typ-range.json""".format(apic=apic,leafifselector=leafifselector,aps=apsname)
            url = """https://{apic}/api/node/mo/uni/infra/{leafifselector}/hports-APS_{vpcname}-typ-range.json""".format(apic=apic,leafifselector=leafifselector,vpcname=vpcname)
            #data = """{"infraHPortS":{"attributes":{"name":"int-test","status":"created,modified"},"children":[{"infraPortBlk":{"attributes":{"fromPort":"40","toPort":"40","name":"block2","status":"created,modified"},"children":[]}},{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accbundle-TEST_VPC","status":"created,modified"},"children":[]}}]}}""" % {toPort:toPort, fromPort:fromPort, blockname:blockname, vpcpolicy=vpcpolicy}
            data = """'{{"infraHPortS":{{"attributes":{{"name":"APS_{vpcname}","status":"created,modified"}},"children":[{{"infraPortBlk":{{"attributes":{{"fromPort":"{fromPort}",\
                "toPort":"{toPort}","fromCard":"{fromCard}","toCard":"{toCard}",name":"{blockname}","status":"created,modified"}},"children":[]}}}},{{"infraRsAccBaseGrp":{{"attributes":{{"tDn":"{vpcpolicy}",\
                "status":"created,modified"}},"children":[]}}}}]}}}}'""".format(toPort=toPort, fromPort=fromPort, fromCard=fromCard, toCard=toCard, blockname=blockname, vpcname=vpcname, vpcpolicy=vpcpolicy)
            result = PostandGetResponseData(url, data, cookie)
            url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-"),eq(fabricPathEp.name,"{vpc}")))""".format(apic=apic,vpc="LP_" + vpcname)
            time.sleep(1)
            result = GetResponseData(url,cookie)
            returnedlist = []
            #import pdb; pdb.set_trace()
            logger.debug(result)
            returnedlist.append(result[0]['fabricPathEp']['attributes']['dn'])
            #import pdb; pdb.set_trace()
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