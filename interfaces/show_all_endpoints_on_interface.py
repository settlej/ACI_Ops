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
import os
import time
import itertools
import ipaddress
from localutils.custom_utils import *


def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

class fvCEp():
    def __init__(self, mac=None, name=None, encap=None,
                 lcC=None, dn=None, fvRsVm=None, fvRsHyper=None,
                 fvRsCEpToPathEp=None, ip=None, fvIplist=[]):
        self.mac = mac
        self.name = name
        self.encap = encap
        self.dn = dn
        self.lcC = lcC
        self.fvRsVm = fvRsVm
        self.fvRsHyper = fvRsHyper
        self.ip = ip
        #self.iplist = iplist
        self.fvIplist = fvIplist
        self.fvRsCEpToPathEp = fvRsCEpToPathEp
    def __repr__(self):
        return self.dn
    def __getitem__(self, mac):
        if mac in self.mac:
            return self.mac
        else:
            return None
    def showips(self):
        iplist = [fvIP.addr for fvIP in self.fvIplist]
        return ', '.join(iplist)


class fvIp():
    def __init__(self, addr=None, rn=None,fvReportingNodes=None):
        self.addr = addr
        self.rn = rn
        self.fvReportingNodes = fvReportingNodes
    def __repr__(self):
        return self.addr
    def __getitem__(self, addr):
        if addr in self.addr:
            return self.addr
        else:
            return None

class fvRsCEpToPathEp():
    def __init__(self, tDn=None, lcC=None, fvReportingNodes=[], forceResolve=None):
        self.lcC = lcC #shows location it learned if 'vmm' vmm knows it cause vmware, 'vmm,learned' means vmware and switch knows, if just 'learned' not vmm source 
        self.tDn = tDn # location of learned interface "topology/pod-1/paths-102/extpaths-112/pathep-[eth1/25]" example
        self.fvReportingNodes = fvReportingNodes # looks like port-channels use fvReportingNode api class (describes leafs where ep is discovered)
        self.forceResolve = forceResolve
    def __repr__(self):
        return self.tDn

class fvRsVm():
    def __init__(self, state=None, tDn=None, dn=None):
        self.state = state
        self.dn = dn
        self.tDn = tDn #internal vm name to lookup vmware vm name
    def __repr__(self):
        return self.tDn

class fvRsHyper():
    def __init__(self, state=None, tDn=None):
        self.state = state
        self.tDn = tDn  #hyperviser internal name to look up vmware host name
    def __repr__(self):
        return self.tDn

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()


def gather_fvCEp_fullinfo(result):
    eplist = []
    fvRsVmobject = None
    fvRsCEpToPathEpobject = None
    fvRsHyperobject = None
    fvIplist = []
    for ep in result:
        fvReportingNodes = []
        mac = ep['fvCEp']['attributes']['mac']
        name = ep['fvCEp']['attributes']['name']
        encap = ep['fvCEp']['attributes']['encap']
        lcC = ep['fvCEp']['attributes']['lcC']
        dn = ep['fvCEp']['attributes']['dn']
        ip = ep['fvCEp']['attributes']['ip']
        if ep['fvCEp'].get('children'):
            for ceptopath in ep['fvCEp']['children']:
                if ceptopath.get('fvRsCEpToPathEp') and ceptopath['fvRsCEpToPathEp']['attributes']['state'] == 'formed':
                    fvRsCEpToPathEp_tDn = ceptopath['fvRsCEpToPathEp']['attributes']['tDn']
                    fvRsCEpToPathEp_lcC = ceptopath['fvRsCEpToPathEp']['attributes']['lcC']
                    fvRsCEpToPathEp_forceResolve = ceptopath['fvRsCEpToPathEp']['attributes']['forceResolve']
                    fvRsCEpToPathEpobject = fvRsCEpToPathEp(forceResolve=fvRsCEpToPathEp_forceResolve, 
                                                            tDn=fvRsCEpToPathEp_tDn, lcC=fvRsCEpToPathEp_lcC)
                elif ceptopath.get('fvIp'):
                    fvIp_addr = ceptopath['fvIp']['attributes']['addr']
                    fvIp_rn = ceptopath['fvIp']['attributes']['rn']
                    if ceptopath['fvIp'].get('children'):
                        fvReportingNodes = [node['fvReportingNode']['attributes']['rn'] for node in ceptopath['fvIp']['children']]
                    else:
                        fvReportingNodes = None
                    fvIplist.append(fvIp(addr=fvIp_addr, rn=fvIp_rn,
                                        fvReportingNodes=fvReportingNodes))
                elif ceptopath.get('fvRsVm') and ceptopath['fvRsVm']['attributes']['state'] == 'formed':
                    fvRsVm_state = ceptopath['fvRsVm']['attributes']['state']
                    fvRsVm_tDn = ceptopath['fvRsVm']['attributes']['tDn']
                    fvRsVmobject = fvRsVm(state=fvRsVm_state,
                                            tDn=fvRsVm_tDn)
                elif ceptopath.get('fvRsHyper') and ceptopath['fvRsHyper']['attributes']['state'] == 'formed':
                    fvRsHyper_state = ceptopath['fvRsHyper']['attributes']['state']
                    fvRsHyper_tDn = ceptopath['fvRsHyper']['attributes']['tDn']
                    fvRsHyperobject = fvRsHyper(state=fvRsHyper_state,
                                                tDn=fvRsHyper_tDn)
        eplist.append(fvCEp(mac=mac, name=name, encap=encap,
                                lcC=lcC, dn=dn, fvRsVm=fvRsVmobject, fvRsCEpToPathEp=fvRsCEpToPathEpobject, 
                                ip=ip, fvRsHyper=fvRsHyperobject, fvIplist=fvIplist))
        fvIplist = []
    return eplist


def mac_path_function():
    url = """https://{apic}/api/node/class/fvCEp.json?rsp-subtree=full&target-subtree-class=fvCEp,fvRsCEpToPathEp""".format(apic=apic)
    result, totalcount = GetResponseData(url)
    fvCEplist = gather_fvCEp_fullinfo(result)
    return fvCEplist
    #for x in fvCEplist:
        #print("{:25}{:20}{:20}{}".format(x.mac, x.ip, x.fvIplist, x.fvRsCEpToPathEp))
    #    print("{},{},{},{}".format(x.mac,x.ip,x.fvIplist,x.fvRsCEpToPathEp))
    #print(totalcount)
    #for fvCEp in fvCEplist:
    #        result, totalcount = GetResponseData(url)
    #        completefvCEplist = gather_fvCEp_fullinfo(result)
    #        #print(completefvCEplist)
    #        #Display current endpoint info
    #
    #        find_current_ep_info(completefvCEplist[0], totalcount)
    #        #Display current known endpoint history
    #        display_live_history_info(completefvCEplist[0], totalcount)

def physical_selection(all_leaflist,leaf=None):
    if leaf == None:
        nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
        nodelist.sort()
        for num,node in enumerate(nodelist,1):
            print("{}.) {}".format(num,node))
        while True:
            #try:
                asknode = custom_raw_input('\nWhat leaf: ')
                print('\r')
                if asknode.strip().lstrip() == '' or '-' in asknode or ',' in asknode or not asknode.isdigit():
                    print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
                    continue
                returnedlist = parseandreturnsingelist(asknode, nodelist)
                if returnedlist == 'invalid':
                    continue
                chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
                break
            #except KeyboardInterrupt as k:
            #    print('\n\nEnding Script....\n')
            #    return
    else:
        chosenleafs = [leaf]
    compoundedleafresult = []
    for leaf in chosenleafs:
        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
        result, totalcount = GetResponseData(url)
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
        b = goodspacing(column[0]) + '  ' + column[0].descr
        c = column[1].number
        d = goodspacing(column[1]) + '  ' + column[1].descr
        if column[2] == '' or column[2] == None:
            e = ''
            f = ''
        else:
            #e = interfacedict[column[2]]
            e = column[2].number
            f = goodspacing(column[2]) + '  ' + column[2].descr
            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
        print('{:6}.) {:42}{}.) {:42}{}.) {}'.format(a,b,c,d,e,f))
    while True:
        #try:
            selectedinterfaces = custom_raw_input("\nSelect interface(s) by number: ")
            print('\r')
            if selectedinterfaces.strip().lstrip() == '' or '-' in selectedinterfaces or ',' in selectedinterfaces: # or not selectedinterfaces.isdigit():
                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
                continue
            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
            if intsinglelist == 'invalid':
                continue
            return filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist), leaf

def get_All_leafs():
    url = """https://{apic}/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),""" \
          """and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    return result

def goodspacing(column):
    if column.fex:
        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
    elif column.fex == '':
        return column.leaf + ' ' + str(column.name)

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

def menu():
    while True:
        clear_screen()
        print("\nSelect interface for adding EPGs: \n" + \
          "\n\t1.) Physical Interfaces: \n" + \
          "\t2.) PC Interfaces: \n" + \
          "\t3.) VPC Interfaces: \n")
        selection = custom_raw_input("Select number: ")
        print('\r')
        if selection.isdigit() and selection != '' and 1 <= int(selection) <= 3:
            break
        else:
            continue
    return selection 

def get_All_EGPs():
    #get_Cookie()
    epgdict = {}
    url = """https://{apic}/api/node/class/fvAEPg.json""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    #print(json.dumps(result, indent=2))
    epglist = [epg['fvAEPg']['attributes']['dn'] for epg in result]
            #epgdict[epg['fvAEPg']['attributes']['name']] = epg['fvAEPg']['attributes']['dn']
    #    epglist.append(epg['fvAEPg']['attributes']['dn'])
    return epglist

def get_All_PCs():
    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """eq(fabricPathEp.lagT,"link"))""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    return result

def get_All_vPCs():
    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-")))""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    return result


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

def port_channel_selection(allpclist,allepglist):
    pcdict = {}  
    pcobjectlist = []
    for pc in allpclist:
        pcobjectlist.append(pcObject(name = pc['fabricPathEp']['attributes']['name'],
                                     dn = pc['fabricPathEp']['attributes']['dn'] ))
    #for pc in allpclist:
    #    pcdict[pc['fabricPathEp']['attributes']['name']] = pc['fabricPathEp']['attributes']['dn']
    print("\n{:>4} |  {}".format("#","Port-Channel Name"))
    print("-"* 65)
   # numpcdict = {}
    for num,pc in enumerate(sorted(pcobjectlist),1):
        print("{:>4}.) {}".format(num,pc.name))
        pc.number = num
    #    numpcdict[num] = pc
    while True:
        try:
            askpcnum = custom_raw_input("\nWhich number(s)?: ")
            print('\r')
            if askpcnum.strip().lstrip() == '':
                continue
            #askpcnum = '1,2,3,6,9,12,14'
            pcsinglelist = parseandreturnsingelist2(askpcnum,pcobjectlist)
            if pcsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = filter(lambda x: x.number in pcsinglelist, pcobjectlist)
           # for chosennumber in pcsinglelist:
           #     #if chosennumber in 
           #     pcdict[pcobjectlist[int(t)]]
            break
        except ValueError as v:
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    return choseninterfaceobjectlist
    #numepgdict = {}
#
    #print("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG"))
    #print("-"* 65)
    #for num,epg in enumerate(sorted(allepglist),1):
    #    numepgdict[num] = epg
    #    egpslit = epg.split('/')[1:]
    #    print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
    #while True:
    #    try:
    #        askepgnum = custom_raw_input("\nWhich number(s)?: ")
    #        print('\r')
    #        if askepgnum.strip().lstrip() == '':
    #            continue
    #        epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
    #        if epgsinglelist == 'invalid':
    #            continue
    #        #for x in epgsinglelist:
    #        #    print(numepgdict[x])
    #        break
    #    except ValueError as v:
    #        print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    #urllist =  vlan_and_url_generating(epgsinglelist,numepgdict,choseninterfaceobjectlist)
    #    ##        urldict[uniquenumber] = (url, interface.dn, fvRsPa)
    #for url in urllist:
    #    #print(url[0],data)
    #   # try:
    #    result, error = PostandGetResponseData(url[0],url[2])
    #    shorturl = url[0][30:-5]
    #    if error == None and result == []:
    #        print('Success for ' + shorturl + ' > ' + str(url[1]))
#
    #        #print('Success for ' + str(url[1]))
    #    elif result == 'invalid':
    #       # print('level1')
    #        interfacepath = re.search(r'\[.*\]', error)
    #        if 'already exists' in error:
    #            #print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + interfacepath.group() + ' -- EPG already on Interface ' )    
    #            print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + url[1] + ' -- EPG already on Interface ' )    
    #        elif 'AttrBased EPG' in error:
    #          #  print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + pcdict[numpcdict[interface]] +' -- Attribute EPGs need special static attirbutes')    
    #            print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + url[1] + ' -- Attribute EPGs need special static attirbutes')    
    #        else:
    #            print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + '\t -- ' + error)  
    #            # "\x1b[1;37;41mIncorrect Date/Format, Please try again\x1b[0m\x1b[0m\n\n"
    #       #pass#print('Failed for ' + url[0])
    #    else:
    #        print(error)
    #     #   print('level2')

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


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    allepglist = get_All_EGPs()
    allpclist = get_All_PCs()
    allvpclist = get_All_vPCs()
    all_leaflist = get_All_leafs()
    if all_leaflist == []:
        print('\x1b[1;31;40mFailed to retrieve active leafs, make sure leafs are operational...\x1b[0m')
        custom_raw_input('\n#Press enter to continue...')
        return
    selection = menu()
    try:
        if selection == '1':
            print("\nSelect leaf(s): \r")
            interfacelist, leaf = physical_selection(all_leaflist)
            #interface =  interfacelist[0].name
            #interfacelist = physical_selection(all_leaflist, allepglist)
            print(interfacelist)
            #custom_raw_input('#Press enter to continue...')
        elif selection == '2':
            interfacelist = port_channel_selection(allpclist,allepglist)
            print(interfacelist)
            #custom_raw_input('#Press enter to continue...')
        elif selection == '3':
            interfacelist = port_channel_selection(allvpclist,allepglist)
            print(interfacelist)
    except Exception as e:
        print(e)
        raw_input()

        #custom_raw_input('#Press enter to continue...')

    #all_leaflist = get_All_leafs()
    fvCEplist = mac_path_function()
    for x in fvCEplist:
        #print('\t', x.fvRsCEpToPathEp, interfacelist[0])
        if str(x.fvRsCEpToPathEp) == str(interfacelist[0]):
            print("{},{},{},{},{}".format(x.mac,x.ip,x.fvIplist,x.fvRsCEpToPathEp,x.dn))
    raw_input()
#def main():
#    get_Cookie()
#    mac_path_function()

if __name__ == '__main__':
    main()
