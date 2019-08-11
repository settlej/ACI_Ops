#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os
import ipaddress


def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-trig", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

class fvCEP():
    def __init__(self, mac=None, ifId=None, name=None,
                 pcTag=None, dn=None, flags=None):
        self.mac = mac
        self.ifId = ifId
        self.name = name
        self.pcTag = pcTag
        self.dn = dn
        self.flags = flags
    def __repr__(self):
        return self.dn
    def __getitem__(self, mac):
        if mac in self.mac:
            return self.mac
        else:
            return None

class endpointip():
    def __init__(self, forceResolve=None, ifId=None, name=None,
                 pcTag=None, dn=None, flags=None):
        self.addr = addr
        self.ifId = ifId
        self.name = name
        self.pcTag = pcTag
        self.dn = dn
        self.flags = flags
    def __repr__(self):
        return self.dn
    def __getitem__(self, addr):
        if addr in self.addr:
            return self.addr
        else:
            return None

get_Cookie()
url = """https://localhost/api/class/epmMacEp.json"""
result, totalamount = GetResponseData(url)
epmMacEPlist = [x['epmMacEp']['attributes']['addr'] for x in result]  
print(len(epmMacEPlist))
set1 = set(epmMacEPlist)
print(len(set1))


print('\n\n')
url = """https://localhost/api/class/fvCEp.json"""
result, totalamount = GetResponseData(url)
fvCEplist = [x['fvCEp']['attributes']['mac'] for x in result]  
print(len(fvCEplist))
set2 = set(fvCEplist)
print(len(set2))

print(set2-set1)


#https://192.168.255.2/api/class/epmMacEp.json?rsp-subtree=full
# leaf directly https://192.168.255.101/api/class/epmMacEp.json?rsp-subtree=full