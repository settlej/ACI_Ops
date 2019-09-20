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
import pdbi
import os
import itertools
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


def physical_selection(all_leaflist,direction, leaf=None):
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
            selectedinterfaces = custom_raw_input("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: ".format(direction))
            print('\r')
            import pdb; pdb.set_trace()

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    while True:

        all_leaflist = get_All_leafs()
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
#        desiredleaf = custom_custom_raw_input("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
       
        #print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")
        userpath = os.path.expanduser("~")
        userpathmarker = userpath.rfind('/')
        user = os.path.expanduser("~")[userpathmarker+1:]
        name = datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S') + '_' + user
        direction = 'Destination'
        chosendestinterfacobject, leaf = physical_selection(all_leaflist,direction)





#url = """https://{apic}/api/node-101/mo/sys/phys-[eth1/12].json?""".format(interface=interface,apic=apic) \
#      + """query-target=subtree&target-subtree-class=rmonIfOut,l1PhysIf,""" \
#      + """rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,"""\
#      + """l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef"""
#result = GetResponseData()
#https://192.168.255.2/api/node-101/mo/sys/phys-[eth1/12].json?query-target=subtree&target-subtree-class=rmonIfOut,l1PhysIf,rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef
#for x in kk['imdata'][0]['l1PhysIf']['children']:    
#     for y in x:
#    
#class l1PhysIf():
#    def __init__(self, interface):
#        self.interface = interface
#        self.rmonIfIn = None
#        self.rmonEtherStats = None
#        self.l1RsAttEntityPCons = None
#        self.l1RsCdpIfPolCons = None
#        self.ethpmPhysIf = None
#        self.fvDomDef = []
#        self.l1RtMbrIfs = []
#        self.pcAggrMbrIf = []
#    def add_phys_attr(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __str__(self):
#        return self.interface
#    def __repr__(self):
#        return self.interface
#
#class rmonIfIn:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class rmonIfOut:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class rmonEtherStats:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class ethpmPhysIf:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class fvDomDef:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class l1RsAttEntityPCons:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class l1RsCdpIfPolCons:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class l1RtMbrIfs:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#class pcAggrMbrIf:
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#    def __repr__(self):
#        return self.__dict__
#
#
#
#interfaceObject = l1PhysIf(interface)
#
#for x in result:
#    if x.get('rmonIfIn'):
#        interfaceObject.rmonIfIn = x['rmonIfIn']['attributes']
#        #print(x['rmonIfIn']['attributes']['errors'])
#        #print(x['rmonIfIn']['attributes']['octets'])
#        #print(x['rmonIfIn']['attributes']['multicastPkts'])
#    if x.get('rmonIfOut'):
#        interfaceObject.rmonIfOut = x['rmonIfOut']['attributes']
#        #print(x['rmonIfOut']['attributes']['multicastPkts'])
#        #print(x['rmonIfOut']['attributes']['errors'])
#        #print(x['rmonIfOut']['attributes']['octets'])
#        #print(x['rmonIfOut']['attributes']['broadcastPkts'])
#    if x.get('rmonEtherStats'):
#        interfaceObject.rmonEtherStats =  x['rmonEtherStats']['attributes']
#        #print(x['rmonEtherStats']['attributes']['cRCAlignErrors'])
#        #print(x['rmonEtherStats']['attributes']['multicastPkts'])
#        #print(x['rmonEtherStats']['attributes']['rxGiantPkts'])
#        #print(x['rmonEtherStats']['attributes']['rxOversizePkts'])
#        #print(x['rmonEtherStats']['attributes']['tXNoErrors'])
#    if x.get('ethpmPhysIf'):
#        interfaceObject.ethpmPhysIf = x['ethpmPhysIf']['attributes']
#        #print(x['ethpmPhysIf']['attributes']['backplaneMac'])
#        #print(x['ethpmPhysIf']['attributes']['bundleIndex'])
#        #print(x['ethpmPhysIf']['attributes']['operVlans'])
#        #print(x['ethpmPhysIf']['attributes']['allowedVlans'])
#        #print(x['ethpmPhysIf']['attributes']['operDuplex'])
#        #print(x['ethpmPhysIf']['attributes']['operSpeed'])
#        #print(x['ethpmPhysIf']['attributes']['operSt'])
#    if x.get('l1PhysIf'):
#        interfaceObject.add_phys_attr(x['l1PhysIf']['attributes'])
#        #print(x['l1PhysIf']['attributes']['adminSt'])
#        #print(x['l1PhysIf']['attributes']['autoNeg'])
#        #print(x['l1PhysIf']['attributes']['layer'])
#        #print(x['l1PhysIf']['attributes']['mtu'])
#        #print(x['l1PhysIf']['attributes']['descr'])
#        #print(x['l1PhysIf']['attributes']['spanMode'])
#        #print(x['l1PhysIf']['attributes']['switchingSt'])
#        #print(x['l1PhysIf']['attributes']['usage'])
#        #print(x['l1PhysIf']['attributes']['speed'])
#    if x.get('fvDomDef'):
#        interfaceObject.fvDomDef.append(x['fvDomDef']['attributes'])
#        #['domPKey']
#    if x.get('l1RsAttEntityPCons'):
#        interfaceObject.l1RsAttEntityPCons = x['l1RsAttEntityPCons']['attributes']
#        #['tDn']
#    if x.get('l1RsCdpIfPolCons'):
#        interfaceObject.l1RsCdpIfPolCons = x['l1RsCdpIfPolCons']['attributes']
#        #['tDn']
#    if x.get('l1RtMbrIfs'):
#        interfaceObject.l1RtMbrIf.append(x['l1RtMbrIfs']['attributes'])
#        #['tDn']
#        #print(x['l1RtMbrIfs']['attributes']['tSKey'])
#    if x.get('pcAggrMbrIf'):
#        interfaceObject.pcAggrMbrIf.append(x['pcAggrMbrIf']['attributes'])
#        #['pcMode']
#        #print(x['pcAggrMbrIf']['attributes']['operSt'])
#
#
#
#
#
#
#['rmonifIn']['attributes'][errors'] == rx inpur errors
#if x.get('rmonIfIn'):
#    print(x['rmonIfIn']['attributes']['bytes']) == rx bytes
#    print(x['rmonIfIn']['attributes']['multicastPkts'] == rx mulitcast packets
#if x.get('rmonIfOut'):
#    print(x['rmonIfOut']['attributes']['multicastPkts'] == tx mulitcast packets
#    print(x['rmonifOut']['attributes']['errors'] == tx out errorrs
#    print(x['rmonifOut']['attributes']['octets'] == tx bytes
#    print(x['rmonifOut']['attributes']['broadcastPkts'] == tx broadcast packets
#if x.get('rmonEtherStats'):
#    print(x['rmonEtherStats']['attributes']['cRCAlignErrors'] == CRC rx
#    print(x['rmonEtherStats']['attributes']['multicastPkts'] == tx mulitcast packets
#    print(x['rmonEtherStats']['attributes']['rxGiantPkts'] == rx rxGiantPkts
#    print(x['rmonEtherstats']['attributes']['rxOversizePkts'] == rx jumo packets
#    print(x['rmonEtherStats']['attributes']['txNoErrors'] == tx output packets
#if x.get('ethpmPhysIf'):
#    print(x['ethpmPhysIf']['attributes']['backplaneMac'] == interface mac
#    print(x['ethpmPhysIf']['attributes']['bundleIndex'] == port-channel number
#    print(x['ethpmPhysIf']['attributes']['operVlans'] == up vlans
#    print(x['ethpmPhysIf']['attributes']['allowedVlans'] == configed vlans
#    print(x['ethpmPhysIf']['attributes']['operDuplex'] == operDuplex
#    print(x['ethpmPhysIf']['attributes']['operSpeed'] == link operSpeed
#    print(x['ethpmPhysIf']['attributes']['operSt'] == link status
#if x.get('l1PhysIf'):
#    print(x['l1PhysIf']['attributes']['adminSt'] = up
#    print(x['l1PhysIf']['attributes']['autoNeg'] = on 
#    print(x['l1PhysIf']['attributes']['layer'] = layer2 or layer3
#    print(x['l1PhysIf']['attributes']['mtu'] 
#    print(x['l1PhysIf']['attributes']['descr']
#    print(x['l1PhysIf']['attributes']['spanMode'] = is span dest
#    print(x['l1PhysIf']['attributes']['switchingSt'] = epgs on interface
#    print(x['l1PhysIf']['attributes']['usage'] = epg,interface
#    print(x['l1PhysIf']['attributes']['speed'] = inherit
#if x.get('fvDomDef'):
#    print(x['fvDomDef']['attributes']['domPKey'] = domain allowed on interface
#if x.get('fvDomDef'):
#    print(x['l1RsAttEntityPCons']['attributes']['tDn'] = AAEP on interface
#if x.get('fvDomDef'):
#    print(x['l1RsCdpIfPolCons']['attributes']['tDn'] = current cdp policy
#if x.get('fvDomDef'):
#
#    print(x['l1RtMbrIfs']['attributes']['tDn'] == po tDn
#    print(x['l1RtMbrIfs']['attributes']['tSKey'] == po num
#if x.get('pcAggrMbrIf'):
#    print(x['pcAggrMbrIf']['attributes']['pcMode']
#    print(x['pcAggrMbrIf']['attributes']['operSt']
#
#
#