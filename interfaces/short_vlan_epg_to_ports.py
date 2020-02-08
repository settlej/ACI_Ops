#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import json
import ssl
import trace
import logging
import os
import time
import itertools
import threading
import Queue
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


class interfaceProperties():
    def __init__(self, name, etype, epgs):
        self.name = name
        self.etype = etype
        self.epgs = epgs
    def __repr__(self):
        return self.name

class epgobj():
    def __init__(self, epg):
        self.epg = epg
        self.encapvlans = []
        self.internalvlans = []
    def __repr__(self):
        return self.epg

class l2BD():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        if self.name != '':
            return self.name
        else:
            return self.dn
#class l1PhysIf():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#        self.ethpmPhysIf = []
#    def __repr__(self):
#        if self.name != '':
#            return self.dn
class ethpmPhysIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.allowedVlans
class pcAggrMbrIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.operSt

def shortenrange(lista):
    isactiverange = False
    foundrangestart = None
    foundrangeend = None
    foundrange = []
    for num,current_item in enumerate(lista):
        #import pdb; pdb.set_trace()
        if current_item == lista[-1]:
            if not isactiverange:
                foundrange.append(str(current_item))
            if isactiverange:
                foundrange.append(str(foundrangestart) + '-' + str(current_item))
        elif isactiverange and int(current_item) + 1 != lista[num + 1]:
            foundrange.append(str(foundrangestart) + '-' + str(current_item))
            isactiverange = False
            foundrangestart = None
            foundrangeend = None
        elif not isactiverange and not int(current_item) + 1 == lista[num + 1]:
            foundrange.append(str(current_item))
            foundrangestart = None
            foundrangeend = None
        elif int(current_item) + 1 == lista[num + 1]:
            if not foundrangestart:
                isactiverange = True
                foundrangestart = current_item
            foundrangeend = current_item
            #foundrange.append(current_item+1)
           # import pdb; pdb.set_trace()
        else:
            if foundrangestart:
                foundrangeend = current_item

    return foundrange
def parseandreturnsingelist(liststring):
    try:
        rangelist = []
        singlelist = []
        seperated_list = liststring.split(',')
        for x in seperated_list:
            if '-' in x:
                rangelist.append(x)
            else:
                singlelist.append(int(x))
        if len(rangelist) >= 1:
            for foundrange in rangelist:
                tempsplit = foundrange.split('-')
                for i in xrange(int(tempsplit[0]), int(tempsplit[1])+1):
                    singlelist.append(int(i))
        return singlelist
    except:

        pass

def compare_allowedvlans_and_opervlans(opervlanstringlist, allowedvlansstringlist):
    list1 = parseandreturnsingelist(allowedvlansstringlist)
    list2 = parseandreturnsingelist(opervlanstringlist)
    #import pdb; pdb.set_trace()
    combinedlist = set(list1) - set(list2)
    return shortenrange(sorted(list(combinedlist)))


def pull_interface_with_vlaninfo(apic, cookie, leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l1PhysIf.json?rsp-subtree=children&rsp-subtree-class=pcAggrMbrIf,ethpmPhysIf&order-by=l1PhysIf.id|asc""".format(apic=apic, leaf=leaf)
    result = GetResponseData(url, cookie)
    logger.info(url)
    l1PhysIflist = []
    for x in result:
        l1PhysIfobj = l1PhysIf(**x['l1PhysIf']['attributes'])
        if x['l1PhysIf'].get('children'):
            for y in x['l1PhysIf']['children']:
                if y.get('ethpmPhysIf'):
                    l1PhysIfobj.children.append(ethpmPhysIf(**y['ethpmPhysIf']['attributes']))
                if y.get('pcAggrMbrIf'):
                    l1PhysIfobj.add_portchannel(pcAggrMbrIf(**y['pcAggrMbrIf']['attributes']))
        l1PhysIflist.append(l1PhysIfobj)
    print('\n')
    print('{:12} {:12} {:32}   {:32}  {}'.format('Interface', 'Status', 'Configured Vlans', 'Working Vlans', 'Down Vlans'))
    print('-' * 110)
    #shortenrangea = parseandreturnsingelist('1-3,5,7-9,11-15,17-21,23,24-28,34-35')
    #shortenrangeb = parseandreturnsingelist('1-3,5,9,12,20-21,23,25,27-28,34-35')
    #mm = set(shortenrangea) - set(shortenrangeb)
    #mm = shortenrange(sorted(list(mm)))
    #print(mm)
    for x in l1PhysIflist:
        #import pdb; pdb.set_trace()
        if x.adminSt == 'up' and (x.children[0].operStQual == 'sfp-missing' or x.children[0].operStQual == 'link-failure'):
            status = 'down/down'
        elif x.adminSt == 'down':
            status = 'admin-down'
        elif x.children[0].operStQual == 'suspended-due-to-no-lacp-pdus':
            status = 'down/down'
        else:
            status = 'up/up'
        operVlans = None
        #import pdb; pdb.set_trace()
        if x.children[0].operVlans != '' and x.children[0].allowedVlans != '':
            missingvlans = ','.join(compare_allowedvlans_and_opervlans(x.children[0].operVlans, x.children[0].allowedVlans))
        elif x.children[0].operVlans == '' and x.children[0].allowedVlans != '':
            missingvlans = x.children[0].allowedVlans
        else:
            missingvlans = ''
        if len(x.children[0].allowedVlans.split(',')) > 8:
          #  for num in range(10):
            for num in range((len(x.children[0].operVlans.split(',')) // 8) + 1):
                if operVlans:
                   # import pdb; pdb.set_trace() 
                    operVlans = operVlans[8:]
                    allowedVlans = allowedVlans[8:]
          #          import pdb; pdb.set_trace()
                    if len(operVlans) > 9:
                        print('{:12} {:12} {:32}   \x1b[1;33;40m{:<32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format('', '', ','.join(allowedVlans[:8]) + ',',','.join(operVlans[:8]) + ',', missingvlans))
                    else:
                        print('{:12} {:12} {:32}   \x1b[1;33;40m{:<32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format('', '', ','.join(allowedVlans[:8]),','.join(operVlans[:8]),  missingvlans))
    
                else:
                    operVlans =  x.children[0].operVlans.split(',')
                    allowedVlans = x.children[0].allowedVlans.split(',')
                    if len(operVlans) > 8:
                        print('{:12} {:12} {:32}   \x1b[1;33;40m{:32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format(x.id, status, ','.join(allowedVlans[:8]) + ',',','.join(operVlans[:8]) + ',', missingvlans))
                    else:
                       # import pdb; pdb.set_trace()
                        print('{:12} {:12} {:32}   \x1b[1;33;40m{:32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format(x.id, status, ','.join(allowedVlans[:8]),','.join(operVlans[:8]), missingvlans))

        else:
            if x.layer == 'Layer3' and status == 'up/up':
                print('{:12} {:12} {:^32}   \x1b[1;32;40m{:32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format(x.id, status, '','Layer3',  ''))
            elif x.layer == 'Layer3' and status != 'up/up':
                print('{:12} {:12} {:^32}   \x1b[1;32;40m{:32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format(x.id, status, '','','Layer3'))
            elif x.children[0].operVlans == '' and x.children[0].allowedVlans == '':
                        #elif x.children[0].operVlans == '' and x.children[0].allowedVlans == '':
                    print('{:12} {:12} {:^32}   \x1b[1;33;40m{:<32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format(x.id, status, '',x.children[0].operVlans, ''))
            #missingvlans = ''
            else:
               # import pdb; pdb.set_trace()
                print('{:12} {:12} {:32}   \x1b[1;33;40m{:<32}\x1b[0m  \x1b[1;31;40m{:32}\x1b[0m'.format(x.id, status, x.children[0].allowedVlans,x.children[0].operVlans, missingvlans))



            
#def pull_vlan_info_for_leaf(apic, cookie, leaf):
#    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/vlanCktEp.json""".format(apic=apic, leaf=leaf)
#    logger.info(url)
#    result = GetResponseData(url, cookie)
#    vlanlist = [vlanCktEp(**x['vlanCktEp']['attributes']) for x in result]
#    return vlanlist

def pull_bd_info_for_leaf(apic, cookie, leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l2BD.json""".format(apic=apic, leaf=leaf)
    logger.info(url)
    result = GetResponseData(url, cookie)
    bdlist = [l2BD(**x['l2BD']['attributes']) for x in result]
    return bdlist


def pull_each_vlan(apic, leaf, vlan, q):
    url = """https://{apic}/api/mo/{vlan}.json?query-target=children&target-subtree-class=l2RsPathDomAtt""".format(apic=apic, vlan=vlan.dn)
    logger.info(url)
    result = GetResponseData(url, cookie)
    q.put((vlan,result))

class interfacetoEpg():
    def __init__(self, interface):
        self.vlan = []
        self.interface = interface

def interface_epg_pull(apic,cookie, epgvlanlist, selectedleaf):
    leaf = selectedleaf
    #str(chosendestinterfaceobject[0]).replace('paths','nodes')
    #clear_screen()
    q = Queue.Queue()
    #leafs = leaf_selection(get_All_leafs(apic, cookie))
    threadlist = []
    leafinterfacelist = []
    interfacedictwithegps = {}
    for epgvlan in epgvlanlist:
        t = threading.Thread(target=pull_each_vlan, args=[apic, leaf, epgvlan, q])
        t.start()
        threadlist.append(t)
    resultlist = []
    for thread in threadlist:
        thread.join()
        resultlist.append(q.get())
    allinterfacesfound = set()
    interfaces_per_vlan = []
    vlanwith_allinterfacesfound = []
    for result in resultlist:
        for x in result[1]:
            if x.get('l2RsPathDomAtt'):
                allinterfacesfound.add(x['l2RsPathDomAtt']['attributes']['tDn'])
                interfaces_per_vlan.append(x['l2RsPathDomAtt']['attributes']['tDn'])
        vlanwith_allinterfacesfound.append((result[0], interfaces_per_vlan))
        interfaces_per_vlan = []
    interfacewith_allvlans = []
    addvlans = []
    for z in allinterfacesfound:
        for x in vlanwith_allinterfacesfound:
            #print(z,x)
           # print('\n\n')
            if z in x[1]:
                addvlans.append(x[0])
        interfacewith_allvlans.append((z, addvlans))
        addvlans = []
    #import pdb; pdb.set_trace()
    eth_interfaces = [x for x in interfacewith_allvlans if x[0].count('/') != 7 and 'eth' in x[0]]
    fex_interfaces = [x for x in interfacewith_allvlans if x[0].count('/') == 7 and 'eth' in x[0]]
    po_interfaces = [x for x in interfacewith_allvlans if not 'eth' in x[0]]
    for k in sorted(eth_interfaces, key=lambda x: int(x[0].split('/')[-1][:-1])):
        leftlocation = k[0].find('[')
        print(k[0][leftlocation:])
        for m in k[1]:
            print('\t\t{:10}  | {}'.format(m.encap, m))
        print('\r')
    for k in sorted(fex_interfaces, key=lambda x: int(x[0].split('/')[-1][:-1])):
        leftlocation = k[0].find('[')
        print(k[0][leftlocation:])
        for m in k[1]:
            print('\t\t{:10}  | {}'.format(m.encap, m))
        print('\r')


    for k in sorted(po_interfaces, key=lambda x: int(x[0].split('[po')[-1][:-1])):
        leftlocation = k[0].find('[')
        print(k[0][leftlocation:])
        for m in k[1]:
            print('\t{:10}  | {}'.format( m.encap, m))
        print('\r')


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    while True:
        clear_screen()
        location_banner('Show EPGs to interface')
        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print('\nSelect leaf(s): ')
        print('\r')
#        desiredleaf = custom_custom_raw_input("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
       
        #print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")
        chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
        display_vlan_operations(chosenleafs)
        ask = custom_raw_input("Continue... ") 
        #if ask != '' and ask[0].lower() == 'y':
        #    clear_screen()
        #    location_banner('Show EPGs to interface')
        #    continue
        #else:
        #    break

        
        
def display_vlan_operations(leafs):
        for leaf in leafs:
            switchpreviewutil.main(apic,cookie,[leaf], purpose='port_switching')
            print('\n')
            bdlist = pull_bd_info_for_leaf(apic, cookie, leaf)
            #import pdb; pdb.set_trace()
            vlanlist = pull_vlan_info_for_leaf(apic, cookie, leaf)
            bdandvlanlist = bdlist + vlanlist
            finalbdandvlanlistforsorting = []
            for x in sorted(bdandvlanlist, key=lambda x : int(x.id)):
                if hasattr(x, 'encap'):
                    finalbdandvlanlistforsorting.append(('EPG', x.id, x.encap, x))
                else:
                    finalbdandvlanlistforsorting.append(('BD', x.id, x.name))
            print("{:5} | {:10} | {:10}  | {}".format('Type', "Internal #", "Encap", "Name"))
            print('-' * 80)
            for x in sorted(finalbdandvlanlistforsorting, key=lambda x: (x[0], int(x[1]))):
                if len(x) > 3 and 'LDevInst' in x[3].app(x):
                    #import pdb; pdb.set_trace()
                    print("{:5} | {:^10} | {:11} | {}:{}".format(x[0], x[1], x[2], x[3].tenant, x[3].app(x[3])))
                elif len(x) > 3:
                    print("{:5} | {:^10} | {:11} | {}:{}:{}".format(x[0], x[1], x[2], x[3].tenant, x[3].app(x[3]), x[3].epg))
                else:
                    print("{:5} | {:^10} | {:11} | {}".format(x[0], x[1], '', x[2]))
                
            pull_interface_with_vlaninfo(apic, cookie, leaf)
    
            print('\n')
        
           ######works need to move to new script       epgvlanlist = [x.dn for x in vlanlist]
           ######works need to move to new script       interface_epg_pull(apic, leaf, vlanlist, leaf)
               #   interfacelist = [x['l1PhysIf']['attributes']['id'] for x in result]
               #   interfacelist = interface_vlan_to_epg(apic, cookie, leaf, interfacelist)
               #   #mport pdb; pdb.set_trace()
               #   for interface in interfacelist:
               #       for vlan in vlanlist:
               #           #import pdb; pdb.set_trace()
               #           if interface.epgs != []:
               #               for epg in interface.epgs:
               #                   if epg.epg == vlan.epgDn:
               #                       #import pdb; pdb.set_trace()
               #                       epg.encapvlans.append(vlan.encap)
               #                       epg.internalvlans.append(vlan.fabEncap)
               #   import pdb; pdb.set_trace()
                       #  x,y = interfacelist
                       #  if y != None:
                       #  #import pdb; pdb.set_trace()
                       #      if y == vlan.epgDn:
                       #          pass
                              #for z in y:
                              #   if z == vlan.epgDn:
                              #        print('yes')
          
               #   for interface in sorted(interfacedictwithegps, key=lambda x: (x.split('/')[0],int(x.split('/')[-1]))):
               #       print(interface)
               #       #import pdb; pdb.set_trace()
               #      # if interfacedictwithegps[interface][1]
               #       x,y = interfacedictwithegps[interface]
               #       if y == None:
               #           print('\t{} {}'.format(x,y))
               #       else:
               #           #print('\t{}'.format(x))
               #           for yy in sorted(y):
               #               pass
               #               #print('\t\t{} | {} | {}'.format(yy[0],yy[1],yy[2]))
       # custom_raw_input('Continue...')


#def pull_each_interface(leaf, interface, apic, q):
#    #url = """https://{apic}/api/node-{leaf}/class/l1PhysIf.json""".format(leaf=leaf,apic=apic)
#    epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf),apic=apic)
##url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
#    #import pdb; pdb.set_trace()
#    logger.info(epgurl)
#    #print(interface)
#    epgresult = GetResponseData(epgurl, cookie)
#    #print(epgresult)
#    logger.debug(epgresult)
#    #result = GetResponseData(url, cookie)
#    logger.info('complete')
#    q.put(epgresult)

#def displayepgs(result):
#
#    if result[0]['l1PhysIf']['attributes']['layer'] == 'Layer3':
#        #print(' L3 Interface\n')
#        return 'L3', None
#    if result[0]['l1PhysIf'].get('children'):
#        for int in result[0]['l1PhysIf']['children']:
#            interfaceepglist = []
#            for epgs in int['pconsCtrlrDeployCtx']['children']:
#                if 'LDevInst' in epgs['pconsResourceCtx']['attributes']['ctxDn']:
#                    return 'redirect', None
#                    #print(epgs['pconsResourceCtx']['attributes']['ctxDn'])
#                else:
#                    epgpath = epgs['pconsResourceCtx']['attributes']['ctxDn']#.split('/')
#                #print(epgpath)
#                   # tenant = epgpath[1][3:]
#                   # app = epgpath[2][3:]
#                   # epg = epgpath[3][4:]
#                interfaceepglist.append(epgpath)
#            #import pdb; pdb.set_trace()
#            #return 'L2', (interfaceepglist)
#            return 'L2', interfaceepglist
#                    #print('\t{:10}{:15}{}'.format(tenant,app,epg))
#    else:
#        return 'L2', None

    #allinterfacesfound = list(allinterfacesfound)
   # import pdb; pdb.set_trace()
   # for x in allinterfacesfound:
   #     print(x, resultlist)
       # for v in resultlist:
       #     #print(x, v[1])
       #     if x in v[1].dn:
       #         print(x, v[0])
    #print(result[0].epgDn)
       # for x in result[1]:
       #     if x.get('l2RsPathDomAtt'):
       #         print(x['l2RsPathDomAtt']['attributes']['tDn'])
        #print('\n')
        #print(result[0]['l1PhysIf']['attributes']['id'])
     #   types, epgs = displayepgs(result)
     #   #print(epgs)
     #   if epgs == None:
     #       ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=[])
     #   else:
     #       epgslist = [epgobj(x) for x in epgs]
     #       ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=epgslist)
     #   leafinterfacelist.append(ee)
     #   #print(ee.__dict__)
     #   #interfacedictwithegps[result[0]['l1PhysIf']['attributes']['id']] = (types, epgs)

    #return leafinterfacelist

#def interface_epg_pull(import_apic,import_cookie, selectedleaf, interfacelist):
#    authcounter = 0
#    leaf = selectedleaf
#    #str(chosendestinterfaceobject[0]).replace('paths','nodes')
#    #clear_screen()
#    q = Queue.Queue()
#    #leafs = leaf_selection(get_All_leafs(apic, cookie))
#    threadlist = []
#    leafinterfacelist = []
#    interfacedictwithegps = {}
#    for interface in interfacelist:
#        t = threading.Thread(target=pull_each_interface, args=[leaf, interface, apic, q])
#        t.start()
#        threadlist.append(t)
#    resultlist = []
#    for thread in threadlist:
#        thread.join()
#        resultlist.append(q.get())
#    for result in resultlist:
#        #print('\n')
#        #print(result[0]['l1PhysIf']['attributes']['id'])
#        types, epgs = displayepgs(result)
#        #print(epgs)
#        if epgs == None:
#            ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=[])
#        else:
#            epgslist = [epgobj(x) for x in epgs]
#            ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=epgslist)
#        leafinterfacelist.append(ee)
#        #print(ee.__dict__)
#        #interfacedictwithegps[result[0]['l1PhysIf']['attributes']['id']] = (types, epgs)
#
#    return leafinterfacelist








