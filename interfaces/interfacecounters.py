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
import pdb
import os
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

url = """https://{apic}/api/node-101/mo/sys/phys-[eth1/12].json?""".format(interface=interface,apic=apic) \
      + """query-target=subtree&target-subtree-class=rmonIfOut,l1PhysIf,""" \
      + """rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,"""\
      + """l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef"""

result = GetResponseData()
https://192.168.255.2/api/node-101/mo/sys/phys-[eth1/12].json?query-target=subtree&target-subtree-class=rmonIfOut,l1PhysIf,rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef
for x in kk['imdata'][0]['l1PhysIf']['children']:    
     for y in x:
    
class l1PhysIf():
    def __init__(self, interface):
        self.interface = interface
        self.rmonIfIn = None
        self.rmonEtherStats = None
        self.l1RsAttEntityPCons = None
        self.l1RsCdpIfPolCons = None
        self.ethpmPhysIf = None
        self.fvDomDef = []
        self.l1RtMbrIfs = []
        self.pcAggrMbrIf = []
    def add_phys_attr(self, **kwargs):
        self.__dict__.update(kwargs)
    def __str__(self):
        return self.interface
    def __repr__(self):
        return self.interface

class rmonIfIn:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class rmonIfOut:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class rmonEtherStats:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class ethpmPhysIf:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class fvDomDef:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class l1RsAttEntityPCons:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class l1RsCdpIfPolCons:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class l1RtMbrIfs:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__

class pcAggrMbrIf:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.__dict__



interfaceObject = l1PhysIf(interface)

for x in ii['imdata']:
    if x.get('rmonIfIn'):
        interfaceObject.rmonIfIn = x['rmonIfIn']['attributes']
        #print(x['rmonIfIn']['attributes']['errors'])
        #print(x['rmonIfIn']['attributes']['octets'])
        #print(x['rmonIfIn']['attributes']['multicastPkts'])
    if x.get('rmonIfOut'):
        interfaceObject.rmonIfOut = x['rmonIfOut']['attributes']
        #print(x['rmonIfOut']['attributes']['multicastPkts'])
        #print(x['rmonIfOut']['attributes']['errors'])
        #print(x['rmonIfOut']['attributes']['octets'])
        #print(x['rmonIfOut']['attributes']['broadcastPkts'])
    if x.get('rmonEtherStats'):
        interfaceObject.rmonEtherStats =  x['rmonEtherStats']['attributes']
        #print(x['rmonEtherStats']['attributes']['cRCAlignErrors'])
        #print(x['rmonEtherStats']['attributes']['multicastPkts'])
        #print(x['rmonEtherStats']['attributes']['rxGiantPkts'])
        #print(x['rmonEtherStats']['attributes']['rxOversizePkts'])
        #print(x['rmonEtherStats']['attributes']['tXNoErrors'])
    if x.get('ethpmPhysIf'):
        interfaceObject.ethpmPhysIf = x['ethpmPhysIf']['attributes']
        #print(x['ethpmPhysIf']['attributes']['backplaneMac'])
        #print(x['ethpmPhysIf']['attributes']['bundleIndex'])
        #print(x['ethpmPhysIf']['attributes']['operVlans'])
        #print(x['ethpmPhysIf']['attributes']['allowedVlans'])
        #print(x['ethpmPhysIf']['attributes']['operDuplex'])
        #print(x['ethpmPhysIf']['attributes']['operSpeed'])
        #print(x['ethpmPhysIf']['attributes']['operSt'])
    if x.get('l1PhysIf'):
        interfaceObject.add_phys_attr(x['l1PhysIf']['attributes'])
        #print(x['l1PhysIf']['attributes']['adminSt'])
        #print(x['l1PhysIf']['attributes']['autoNeg'])
        #print(x['l1PhysIf']['attributes']['layer'])
        #print(x['l1PhysIf']['attributes']['mtu'])
        #print(x['l1PhysIf']['attributes']['descr'])
        #print(x['l1PhysIf']['attributes']['spanMode'])
        #print(x['l1PhysIf']['attributes']['switchingSt'])
        #print(x['l1PhysIf']['attributes']['usage'])
        #print(x['l1PhysIf']['attributes']['speed'])
    if x.get('fvDomDef'):
        interfaceObject.fvDomDef.append(x['fvDomDef']['attributes'])
        #['domPKey']
    if x.get('l1RsAttEntityPCons'):
        interfaceObject.l1RsAttEntityPCons = x['l1RsAttEntityPCons']['attributes']
        #['tDn']
    if x.get('l1RsCdpIfPolCons'):
        interfaceObject.l1RsCdpIfPolCons = x['l1RsCdpIfPolCons']['attributes']
        #['tDn']
    if x.get('l1RtMbrIfs'):
        interfaceObject.l1RtMbrIf.append(x['l1RtMbrIfs']['attributes'])
        #['tDn']
        #print(x['l1RtMbrIfs']['attributes']['tSKey'])
    if x.get('pcAggrMbrIf'):
        interfaceObject.pcAggrMbrIf.append(x['pcAggrMbrIf']['attributes'])
        #['pcMode']
        #print(x['pcAggrMbrIf']['attributes']['operSt'])






['rmonifIn']['attributes'][errors'] == rx inpur errors
if x.get('rmonIfIn'):
    print(x['rmonIfIn']['attributes']['bytes']) == rx bytes
    print(x['rmonIfIn']['attributes']['multicastPkts'] == rx mulitcast packets
if x.get('rmonIfOut'):
    print(x['rmonIfOut']['attributes']['multicastPkts'] == tx mulitcast packets
    print(x['rmonifOut']['attributes']['errors'] == tx out errorrs
    print(x['rmonifOut']['attributes']['octets'] == tx bytes
    print(x['rmonifOut']['attributes']['broadcastPkts'] == tx broadcast packets
if x.get('rmonEtherStats'):
    print(x['rmonEtherStats']['attributes']['cRCAlignErrors'] == CRC rx
    print(x['rmonEtherStats']['attributes']['multicastPkts'] == tx mulitcast packets
    print(x['rmonEtherStats']['attributes']['rxGiantPkts'] == rx rxGiantPkts
    print(x['rmonEtherstats']['attributes']['rxOversizePkts'] == rx jumo packets
    print(x['rmonEtherStats']['attributes']['txNoErrors'] == tx output packets
if x.get('ethpmPhysIf'):
    print(x['ethpmPhysIf']['attributes']['backplaneMac'] == interface mac
    print(x['ethpmPhysIf']['attributes']['bundleIndex'] == port-channel number
    print(x['ethpmPhysIf']['attributes']['operVlans'] == up vlans
    print(x['ethpmPhysIf']['attributes']['allowedVlans'] == configed vlans
    print(x['ethpmPhysIf']['attributes']['operDuplex'] == operDuplex
    print(x['ethpmPhysIf']['attributes']['operSpeed'] == link operSpeed
    print(x['ethpmPhysIf']['attributes']['operSt'] == link status
if x.get('l1PhysIf'):
    print(x['l1PhysIf']['attributes']['adminSt'] = up
    print(x['l1PhysIf']['attributes']['autoNeg'] = on 
    print(x['l1PhysIf']['attributes']['layer'] = layer2 or layer3
    print(x['l1PhysIf']['attributes']['mtu'] 
    print(x['l1PhysIf']['attributes']['descr']
    print(x['l1PhysIf']['attributes']['spanMode'] = is span dest
    print(x['l1PhysIf']['attributes']['switchingSt'] = epgs on interface
    print(x['l1PhysIf']['attributes']['usage'] = epg,interface
    print(x['l1PhysIf']['attributes']['speed'] = inherit
if x.get('fvDomDef'):
    print(x['fvDomDef']['attributes']['domPKey'] = domain allowed on interface
if x.get('fvDomDef'):
    print(x['l1RsAttEntityPCons']['attributes']['tDn'] = AAEP on interface
if x.get('fvDomDef'):
    print(x['l1RsCdpIfPolCons']['attributes']['tDn'] = current cdp policy
if x.get('fvDomDef'):

    print(x['l1RtMbrIfs']['attributes']['tDn'] == po tDn
    print(x['l1RtMbrIfs']['attributes']['tSKey'] == po num
if x.get('pcAggrMbrIf'):
    print(x['pcAggrMbrIf']['attributes']['pcMode']
    print(x['pcAggrMbrIf']['attributes']['operSt']


