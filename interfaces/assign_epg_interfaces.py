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
import trace
import pdb
import threading
import Queue
from collections import namedtuple
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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



class fabricPathEp(object):
    def __init__(self, descr=None, dn=None,name=None, number=None):
        self.name = name
        self.descr = descr
        self.dn = dn
        self.number = number
        self.leaf =  dn.split('/')[2].replace('paths','leaf')
        self.shortname = name.replace('eth1/','')
        self.removedint = '/'.join(dn.split('/')[:-2])
        if 'extpaths' in self.dn:
            self.fex = self.dn.split('/')[3].replace('extpaths','fex')
        else:
            self.fex = ''
    def __repr__(self):
        return self.dn
    def __getitem__(self, number):
        if number in self.dn:
            return self.dn
        else:
            return None

def grouper(iterable, n, fillvalue=''):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n  # creates list * n so args is a list of iters for iterable
    return itertools.izip_longest(*args, fillvalue=fillvalue)


def parseandreturnsingelist(liststring, collectionlist):
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
   #     print(sorted(singlelist))
        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
            return 'invalid'
        return list(set(singlelist)) 
    except ValueError as v:
        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
        return 'invalid'

def parseandreturnsingelist2(liststring, collectionlist):
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
   #     print(sorted(singlelist))
        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
            return 'invalid'
        return list(set(singlelist)) 

        #1,2,4,5,10]
        #[object1,object2,object3,object4,object5,object6]

    except ValueError as v:
        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
        return 'invalid'



def goodspacing(column):
    if column.fex:
        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
    elif column.fex == '':
        return column.leaf + ' ' + str(column.name)


def vlan_and_url_generating(epgsinglelist,numepgdict,choseninterfaceobjectlist):
    urllist = []
    for epg in sorted(epgsinglelist):
        url = """https://{apic}/api/node/mo/{}.json""".format(numepgdict[epg],apic=apic)
        print("\nProvide a vlan number for epg: {}".format(numepgdict[epg]))
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
            data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface.dn,vlan=vlan)
            #print(fvRsPa)
            urlmodify = namedtuple('urlmodify', ('url', 'interface', 'data'))
            urllist.append(urlmodify(url, interface, data))
           # urldict[uniquenumber] = (url, interface.dn, fvRsPa)
    return urllist

class pcObject():
    def __init__(self, name=None, dn=None, number=None):
        self.name = name
        self.dn = dn
        self.number = number
    def __repr__(self):
        return self.dn
    def __get__(self, num):
        if num in self.number:
            return self.name
        else:
            return None

def add_egps_to_interfaces(urllist, interfacetype):
    queue = Queue.Queue()
    threadlist = []
    queuelist = []
    for url in urllist:
        t = threading.Thread(target=submit_add_post_request, args=(url,interfacetype,queue))
        t.start()
        threadlist.append(t)
    for t in threadlist:
        t.join()
        queuelist.append(queue.get())
    for q in sorted(queuelist):
        print(q)

def submit_add_post_request(url,interfacetype,queue):
    result, error = PostandGetResponseData(url.url, url.data,cookie)
    shorturl = url.url[30:-5]
    if error == None and result == []:
        finalresult = 'Success for ' + shorturl + ' > ' + str(url.interface)
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


def port_channel_selection(allpclist,allepglist):
    pcobjectlist = []
    for pc in allpclist:
        pcobjectlist.append(pcObject(name = pc['fabricPathEp']['attributes']['name'],
                                     dn = pc['fabricPathEp']['attributes']['dn'] ))
    print("\n{:>4} |  {}".format("#","Port-Channel Name"))
    print("-"* 65)
    for num,pc in enumerate(sorted(pcobjectlist),1):
        print("{:>4}.) {}".format(num,pc.name))
        pc.number = num
    while True:
        try:
            askpcnum = custom_raw_input("\nWhich number(s)?: ")
            print('\r')
            if askpcnum.strip().lstrip() == '':
                continue
            pcsinglelist = parseandreturnsingelist2(askpcnum,pcobjectlist)
            if pcsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = filter(lambda x: x.number in pcsinglelist, pcobjectlist)
            break
        except ValueError as v:
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
            
    numepgdict = {}

    print("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG"))
    print("-"* 65)
    for num,epg in enumerate(sorted(allepglist),1):
        numepgdict[num] = epg
        egpslit = epg.split('/')[1:]
        print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
    while True:
        try:
            askepgnum = custom_raw_input("\nWhich number(s)?: ")
            print('\r')
            if askepgnum.strip().lstrip() == '':
                continue
            epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
            if epgsinglelist == 'invalid':
                continue
            break
        except ValueError as v:
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    urllist =  vlan_and_url_generating(epgsinglelist,numepgdict,choseninterfaceobjectlist)
    add_egps_to_interfaces(urllist, 'Port-Channel')
#        result, error = PostandGetResponseData(url.url, url.data, cookie)
#        shorturl = url.url[30:-5]
#        if error == None and result == []:
#            finalresult = 'Success for ' + shorturl + ' > ' + str(url.interface)
#            print(finalresult)
#            logger.debug('Port-Channel modify: ' + finalresult)
#        elif result == 'invalid':
#            logger.debug(error)
#            interfacepath = re.search(r'\[.*\]', error)
#            if 'already exists' in error:
#                print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + str(url.interface) + ' -- EPG already on Interface ' )    
#            elif 'AttrBased EPG' in error:
#                print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + str(url.interface) + ' -- Attribute EPGs need special static attirbutes')    
#            else:
#                print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + '\t -- ' + error)  
#        else:
#            print(error)
#            logger.error('Port-Channel modify: ' + error)


def physical_selection(all_leaflist, allepglist):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    nodelist.sort()
    for num,node in enumerate(nodelist,1):
        print("{}.) {}".format(num,node))
    while True:
        asknode = custom_raw_input('\nWhat leaf(s): ')
        print('\r')
        returnedlist = parseandreturnsingelist(asknode, nodelist)
        if returnedlist == 'invalid':
            continue
        chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
        break
    compoundedleafresult = []
    for leaf in chosenleafs:
        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
        result = GetResponseData(url, cookie)
        compoundedleafresult.append(result)
    result = compoundedleafresult
    interfacelist = []
    interfacelist2 = []
    for x in result:
        for pathep in x:
            dn = pathep['fabricPathEp']['attributes']['dn']
            name = pathep['fabricPathEp']['attributes']['name']
            descr = pathep['fabricPathEp']['attributes']['descr']
            if 'extpaths' in dn:
                interfacelist2.append(fabricPathEp(descr=descr, dn=dn ,name=name))
            else:
                interfacelist.append(fabricPathEp(descr=descr, dn=dn ,name=name))
            
    interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortname)))
    interfacelist = sorted(interfacelist, key=lambda x: int(x.shortname))
    interfacenewlist = interfacelist2 + interfacelist
    interfacelist = []
    interfacelist2 = []
    finalsortedinterfacelist = sorted(interfacenewlist, key=lambda x: x.removedint)
    interfacedict = {}
    for num,interf in enumerate(finalsortedinterfacelist,1):
        if interf != '':
           interfacedict[interf] = str(num) + '.) '
           interf.number = num
    listlen = len(finalsortedinterfacelist) / 3
    firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]
    finalgrouped = zip(*firstgrouped)
    for column in finalgrouped:
        a = column[0].number
        b = goodspacing(column[0])
        c = column[1].number
        d = goodspacing(column[1])
        if column[2] == '' or column[2] == None:
            e = ''
            f = ''
        else:
            #e = interfacedict[column[2]]
            e = column[2].number
            f = goodspacing(column[2])
            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
        print('{:6}.) {:33}{}.) {:33}{}.) {}'.format(a,b,c,d,e,f))
    while True:
        #try:
            selectedinterfaces = custom_raw_input("\nSelect interface(s) by number: ")
            print('\r')
            if selectedinterfaces.strip().lstrip() == '':
                continue
            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
            if intsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist)
            break
    numepgdict = {}
    print("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG"))
    print("-"* 65)
    allepglist = sorted(allepglist)
    for num,epg in enumerate(allepglist,1):
        numepgdict[num] = epg
        egpslit = epg.split('/')[1:]
        print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
    while True:
        #try:
            askepgnum = custom_raw_input("\nWhich number(s)?: ")
            print('\r')
            if askepgnum.strip().lstrip() == '':
                continue
            epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
            if epgsinglelist == 'invalid':
                continue
            chosenepgs = [allepglist[x] for x in epgsinglelist]
            break
    compoundurllist = []
    urllist =  vlan_and_url_generating(epgsinglelist,numepgdict,choseninterfaceobjectlist)
    add_egps_to_interfaces(urllist, 'Physical')
    #for url in urllist:
    #    result, error = PostandGetResponseData(url.url, url.data,cookie)
    #    shorturl = url.url[30:-5]
    #    if error == None and result == []:
    #        finalresult = 'Success for ' + shorturl + ' > ' + str(url.interface)
    #        print(finalresult)
    #        logger.debug('Physical modify: ' + finalresult)
    #    elif result == 'invalid':
    #        logger.error('Physical modify: ' + error)
    #       # print('level1')
    #        interfacepath = re.search(r'\[.*\]', error)
    #        if 'already exists' in error:
    #            print('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + ' > ' + url.interface.dn + '\t -- EPG already on Interface ')# + interfacepath.group())    
    #        else:
    #            print('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + '\t -- ' + error)
    #    else:
    #        logger.error('Physical modify: ' + error)
    #        print(error)

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
    
        selection = interface_menu()
    
        if selection == '1':
            physical_selection(all_leaflist, allepglist)
            print('\r')
            custom_raw_input('#Press enter to continue...')
        elif selection == '2':
            port_channel_selection(allpclist,allepglist)
            print('\r')
            custom_raw_input('#Press enter to continue...')
          #      for number in sorted(pcsinglelist):
          #          data = """{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(numepgdict[number],vlan=vlan)
          #          print(data)
            #result, totalcount = PostandGetResponseData(url, data)
        elif selection == '3':
            port_channel_selection(allvpclist,allepglist)
            print('\r')
            custom_raw_input('#Press enter to continue...')
        
        #print(numepglist[int(askepgnum)])
     #   for num,a in enumerate(sorted(epgdict, reverse=False),1): 
     #       numepgdict[num] = epgdict[a]
     #       egpslit = epgdict[a].split('/')[1:]
     #       print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
     #   epgnum = custom_raw_input("which number(s)?: ")

        #print(numepgdict[int(epgnum)])
            #print(pcdict)
            #print(epgdict)
#            Curr
#url: https://192.168.255.2/api/node/mo/uni/tn-SI/ap-APP-MGMT/epg-EPG-ESXI-MGMT.json
#payload{"fvRsPathAtt":{"attributes":{"encap":"vlan-235","instrImedcy":"immediate","tDn":"topology/pod-1/paths-102/extpaths-112/pathep-[Find-vpc]","status":"created"},"children":[]}}
#response: {"totalCount":"0","imdata":[]}
#            custom_raw_input("#Press enter to return to main menu...")
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
                print('\n\nEnding Script....\n')
                exit()

#                        url = 'https://{apic}/api/node/mo/uni/fabric/outofsvc.json'
#                        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a fex interface
#                        data = """'{{"fabricRsOosPath":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/extpaths-{fexnumber}/pathep-[{ints}]","lc":"blacklist"}},"children":[]}}}}'""".format(fexnumber=fexnumber,ints=('eth1' + ints[8:]),leaf=leaf)
#                        PostandGetResponseData(url, data)
#                        print(leaf + ' ' + fexnumber + ' ' +  ints + ' shut')
#PC
#url: https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),eq(fabricPathEp.lagT,"link"))
