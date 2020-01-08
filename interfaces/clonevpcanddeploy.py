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
import fabric_access

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


def retrieve_leafprofiles(apic, cookie):
    url = """https://{apic}/api/node/class/infraAccPortP.json""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    return result

def retrieve_fexprofiles(apic, cookie):
    url = """https://{apic}/api/node/class/infraFexP.json""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    return result

def retrieve_clone_portchannel_master(apic, cookie, returnedlist):
    url = """https://{apic}/api/node/class/infraAccBndlGrp.json?query-target-filter=eq(infraAccBndlGrp.name,"{vpcname}")&rsp-subtree=full""".format(apic=apic,vpcname=returnedlist[0].name)
    logger.info(url)
    leafselectorresult = GetResponseData(url,cookie)
    for infraAccBndlGrp in leafselectorresult:
        for policy in infraAccBndlGrp['infraAccBndlGrp']['children']:
            if policy.get('infraRtAccBaseGrp'):
                try:
                    currentleafifselector = policy['infraRtAccBaseGrp']['attributes']['tDn']
                except Exception as e:
                    print(e)
    for x in leafselectorresult[0]['infraAccBndlGrp']['attributes'].keys():
        del leafselectorresult[0]['infraAccBndlGrp']['attributes'][x]
    for m in leafselectorresult[0]['infraAccBndlGrp']['children']:
        for t in m.keys():
            if t == 'infraRtAccBaseGrp':
                del m[t]
            else:
                for x in m[t]['attributes'].keys():
                    if t == 'infraRsAttEntP':
                        if x != 'tDn':
                            del m[t]['attributes'][x]
                    elif x not in policygrouplist:
                        del m[t]['attributes'][x]
    leafselectorresult[0]['infraAccBndlGrp']['children'] = filter(None, leafselectorresult[0]['infraAccBndlGrp']['children'])
    return leafselectorresult, currentleafifselector






def portchannel_clone_and_deploy(apic, cookie, currentleafifselector, leafselectorresult, pctype='vpc'):
    while True:
        while True:
            useifselector = custom_raw_input("Use selected VPC's leaf location? [y=default|n]: ") or 'y'
            if useifselector.lower().strip().lstrip() == 'y':
                leafifselector = currentleafifselector.split('/')[2]
                print(leafifselector)
                break
            elif useifselector.lower().strip().lstrip() == 'n':
                profilelist = []
                leafp = retrieve_leafprofiles(apic, cookie)
                for lp in leafp:
                    profilelist.append(lp['infraAccPortP']['attributes']['dn'].split('/')[2])
                fexp = retrieve_fexprofiles(apic, cookie)
                for fp in fexp:
                    profilelist.append(fp['infraFexP']['attributes']['dn'].split('/')[2])
                print('\n')
                print('\t # | Leaf Profile or Fex Profile')
                print('\t------------------------------------')
                for num,profile in enumerate(profilelist,1):
                    print("\t{:2}.) {}".format(num,profile.replace("accportprof-","").replace("fexprof-", "")))
                while True:
                    selected = custom_raw_input("\nSelect interface 'desired' location: ")
                    selected = selected.strip().lstrip()
                    if selected.isdigit() and int(selected) > 0 and int(selected) <= len(profilelist):
                        break
                    else:
                        print("\nInvalid selection, Please try again...")
                        continue
                leafifselector = profilelist[int(selected)-1]
                #import pdb; pdb.set_trace()

                break
            else:
                print('\n Invalid Option, try again...\n')
                continue
        vpcname = custom_raw_input("Name for new VPC: ")
        if pctype == 'vpc':
            leafselectorresult[0]['infraAccBndlGrp']['attributes'].update(lagT="node",name="LP_" + str(vpcname),status="created,modified")
        else:
            leafselectorresult[0]['infraAccBndlGrp']['attributes'].update(lagT="link",name="LP_" + str(vpcname),status="created,modified")
        vpcpolicy = "uni/infra/funcprof/accbundle-LP_" + vpcname
        vpclocation = custom_raw_input("Interface(s) for new VPC? [format=x/x or x/xx]: ")
        fromCard = vpclocation.split('/')[0].replace('eth', '')
        toCard = vpclocation.split('/')[0].replace('eth', '')
        toPort = vpclocation.split('/')[1]
        fromPort = vpclocation.split('/')[1]
        blockname = 'block-' + str(random.randrange(0, 9999))
    #method: POST
    #url: https://192.168.255.2/api/node/mo/uni/infra/funcprof/accbundle-deleteme.json
        #   payload{"infraAccBndlGrp":{"attributes":{"dn":"uni/infra/funcprof/accbundle-deleteme","lagT":"node","name":"deleteme","rn":"accbundle-deleteme","status":"created"},"children":[{"infraRsCdpIfPol":{"attributes":{"tnCdpIfPolName":"CDP_ON","status":"created,modified"},"children":[]}}]}}
    ##https://192.168.255.2/api/node/mo/uni/infra/funcprof/accbundle-Host8.json?rsp-subtree=full
        url = """https://{apic}/api/node/mo/uni/infra/funcprof/accbundle-{vpc}.json""".format(apic=apic,vpc="LP_" + str(vpcname))
        logger.info(url)
        data = json.dumps(leafselectorresult[0])
        createvpcresult = PostandGetResponseData(url, data, cookie)
        if createvpcresult[0] == 'invalid':
            print("\n\x1b[1;37;41mFailure\x1b[0m -- " + str(createvpcresult[1]) + '\x1b[0m\n')
            del(createvpcresult)
            continue
        #import pdb; pdb.set_trace()
        #apply vpc to interface
        #url = """https://{apic}/api/node/mo/uni/infra/accportprof-Switch101-102_Profile_ifselector/hports-int-test2-typ-range.json""".format(apic=apic,leafifselector=leafifselector,aps=apsname)
        url = """https://{apic}/api/node/mo/uni/infra/{leafifselector}/hports-APS_{vpcname}-typ-range.json""".format(apic=apic,leafifselector=leafifselector,vpcname=vpcname)
        logger.info(url)
        #data = """{"infraHPortS":{"attributes":{"name":"int-test","status":"created,modified"},"children":[{"infraPortBlk":{"attributes":{"fromPort":"40","toPort":"40","name":"block2","status":"created,modified"},"children":[]}},{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accbundle-TEST_VPC","status":"created,modified"},"children":[]}}]}}""" % {toPort:toPort, fromPort:fromPort, blockname:blockname, vpcpolicy=vpcpolicy}
        data = """'{{"infraHPortS":{{"attributes":{{"name":"APS_{vpcname}","status":"created,modified"}},"children":[{{"infraPortBlk":{{"attributes":{{"fromPort":"{fromPort}",\
            "toPort":"{toPort}","fromCard":"{fromCard}","toCard":"{toCard}",name":"{blockname}","status":"created,modified"}},"children":[]}}}},{{"infraRsAccBaseGrp":{{"attributes":{{"tDn":"{vpcpolicy}",\
            "status":"created,modified"}},"children":[]}}}}]}}}}'""".format(toPort=toPort, fromPort=fromPort, fromCard=fromCard, toCard=toCard, blockname=blockname, vpcname=vpcname, vpcpolicy=vpcpolicy)
        apscreationresult = PostandGetResponseData(url, data, cookie)
        if apscreationresult[0] == 'invalid':
            print("\n\x1b[1;37;41mFailure\x1b[0m -- " + str(apscreationresult[1]) + '\x1b[0m\n')
            del(apscreationresult)
            continue
        if pctype == 'vpc':
            url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-"),eq(fabricPathEp.name,"{vpc}")))""".format(apic=apic,vpc="LP_" + vpcname)
        else:
            url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),and(eq(fabricPathEp.lagT,"link"),eq(fabricPathEp.name,"{vpc}")))""".format(apic=apic,vpc="LP_" + vpcname)
        logger.info(url)
        time.sleep(1)
        searchvpcresult = GetResponseData(url,cookie)
        logger.debug(searchvpcresult)
        try:
            if searchvpcresult[0] == 'invalid':
                print("\n\x1b[1;37;41mFailure -- " + str(searchvpcresult[1]) + '\x1b[0m\n')
                del(searchvpcresult)
                continue
        except:
            import pdb; pdb.set_trace()
        returnedlist = []
        #import pdb; pdb.set_trace()
        logger.debug(searchvpcresult)
        returnedlist.append(searchvpcresult[0]['fabricPathEp']['attributes']['dn'])
        break
    return returnedlist
        #import pdb; pdb.set_trace()



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
        all_leaflist = get_All_leafs(apic,cookie)
        clear_screen()
        location_banner('Clone Interface and Deploy')
        selection = interface_menu()
#select vpcs
        if selection == '1':
            chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
           # switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_switching')
            switchpfound, fexes = fabric_access.display_switch_to_leaf_structure.return_physical_programmed_ports_perleaf(chosenleafs[0], apic, cookie)
            interfaces_with_APS_defined = []
            fexfound = []
            for switchp in switchpfound:
               # for leafp in switchp.leafprofiles:
               # print(switchp.name)
              #  import pdb; pdb.set_trace()
                for leafp in switchp.leafprofiles:
               #     print('\t' + leafp.name)
                    interfaces_with_APS_defined.append((switchp.allleafs,leafp.allports))
                    #import pdb; pdb.set_trace()
                    for portlist in leafp.infraHPortSlist:
               #         print('\t\t' + portlist.name)
                        #print(portlist.__dict__)
                        #print('\t\t\t' + portlist.infraRsAccBaseGrp.tDn)
                        #print('\t\t\t' + portlist.infraRsAccBaseGrp.tDn)
                        #if portlist.infraRsAccBaseGrp.tDn in fexes:
                        for x in fexes:
                            if portlist.infraRsAccBaseGrp.tDn != '' and  x.dn in portlist.infraRsAccBaseGrp.tDn:
                              #  import pdb; pdb.set_trace()
                                if portlist.infraFexPlist:
                       #     print('\t\t\t' + portlist.infraRsAccBaseGrp.fexId)
                                    fexfound.append((x,portlist.infraRsAccBaseGrp.fexId))
                       # if portlist.infraRsAccBaseGrp.tCl == 'infraAccPortGrp':
                       #     print('\t\t\t' + 'individual')
                       # elif portlist.infraRsAccBaseGrp.tCl == 'infraAccBndlGrp':
                       #     print('\t\t\t' + 'Port-channel')                    
                       # elif portlist.infraRsAccBaseGrp.tCl == 'infraFexBndlGrp':
                       #     print('\t\t\t' + 'Fex-uplinks')
                       # if portlist.infraFexPlist:
                       #     print('\t\t\t' + portlist.infraRsAccBaseGrp.fexId)
                            
                            
                        
                           # for z in portlist.infraPortsBlklist:
                           #     print('\t\t\t ' + z.fromPort + ' - ' + z.toPort)
                           #     for x in range(int(z.fromPort),int(z.toPort)+1):
                           #         interfaces_with_APS_defined.append((fexes,x))
                                                    #print('\t\t\t' + portlist.infraRsAccBaseGrp.tCl)
                    #    for z in portlist.infraPortsBlklist:
                    #        print('\t\t\t ' + z.fromPort + ' - ' + z.toPort)
                    #   # if len(list(range(int(z.fromPort),int(z.toPort)+1))) > 1:
                    #   #     for x in range(range(int(z.fromPort),int(z.toPort)+1)):
                    #    
                    #            
                    #        for x in range(int(z.fromPort),int(z.toPort)+1):
                    #            interfaces_with_APS_defined.append((switchp.allleafs,x))

            for fex in fexfound:
                interfaces_with_APS_defined.append((fex[1],fex[0].allports))
            compiledports = []
            for interface in interfaces_with_APS_defined:
                if type(interface[0]) != unicode:
                   # import pdb; pdb.set_trace()
                    for leaf in interface[0]:
                        for modulenum, ports in interface[1].items():
                            for port in ports:  
                                compiledports.append(('eth' + str(modulenum) + '/' + str(port)))
                        #import pdb; pdb.set_trace()
                else:
                    for modulenum, ports in interface[1].items():
                        for port in ports:
                            compiledports.append(('eth' + str(interface[0]) + '/' + str(modulenum) + '/' + str(port)))
            compiledports = list(set(compiledports))
            #import custom_utils
            newlist = []
            for x in compiledports:
                newlist.append(l1PhysIf(id = x, shortnum = x.split('/')[-1][0]))
           # import pdb; pdb.set_trace()
            switchpreviewutil.main(apic,cookie,chosenleafs, interfacelist=compiledports, purpose='custom')
            #print(compiledports)
            import pdb; pdb.set_trace()
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
            leafselectorresult, currentleafifselector = retrieve_clone_portchannel_master(apic, cookie, returnedlist)
            returnedlist = portchannel_clone_and_deploy(apic, cookie, currentleafifselector, leafselectorresult, pctype='pc')
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
            leafselectorresult, currentleafifselector = retrieve_clone_portchannel_master(apic, cookie, returnedlist)
            returnedlist = portchannel_clone_and_deploy(apic, cookie, currentleafifselector, leafselectorresult, pctype='vpc')
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