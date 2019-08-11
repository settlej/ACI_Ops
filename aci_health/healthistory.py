#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os
import datetime
import itertools
import trace
import pdb
import datetime

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]



class healthscores():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.healthMin


def grouper(iterable, n, fillvalue=''):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n  # creates list * n so args is a list of iters for iterable
    return itertools.izip_longest(*args, fillvalue=fillvalue)

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()
get_Cookie()
url = """https://localhost/api/node/mo/topology.json?rsp-subtree-include=stats&rsp-subtree-class=fabricOverallHealthHist5min"""
result, totalcount = GetResponseData(url)

healthlist = []
for health in result[0]['fabricTopology']['children']:
    #print(health)
    healthlist.append(healthscores(**health['fabricOverallHealthHist5min']['attributes']))
healthlist = sorted(healthlist, key=lambda x: x.repIntvEnd)
grouped = grouper(healthlist, 96)

print(grouped)
healthlist = zip(*grouped)
for h in healthlist:
    print(h)
    #if h.healthMin < h.healthAvg:
    #    aa = 31
    #else:
    #    aa = 37
    #if h.healthMax > h.healthAvg:
    #    cc = 32
    #else:
    #    cc = 37
    #print('\x1b[1;{};40m{}\x1b[0m  {}  \x1b[1;{};40m{}\x1b[0m  {}'.format(aa,h.healthMin,h.healthAvg,cc,h.healthMax, h.repIntvEnd))
    #zip(h.healthMin, h.healthMax, h.healthAvg)


#for a,b,c in kk: 
#    if a < b:
#       aa = 31
#    else:
#       aa = 37
#    if c > b:
#       cc = 32
#    else:
#       cc = 37
#    print('\x1b[1;{};40m{}\x1b[0m  {}  \x1b[1;{};40m{}\x1b[0m'.format(aa,a,b,cc,c))