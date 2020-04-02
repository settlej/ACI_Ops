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
logger = logging.getLogger('aciops.' + __name__)

class fvEPG():
    def __init__(self, epg):
        _,t,a,e = epg.split('/')
        self.tenant = t
        self.app = a
        self.epg = e

class fvBD():
    def __init__(self, bd):
        self.tenant = bd.split('/')[1].replace('tn-','')
        self.bd = bd.split('/')[2].replace('BD-','',1)
        self.epglist = []
    def add_epg(self, epg):
        self.epglist.append(epg)
    def sort_epgs(self):
        self.epglist.sort(key=lambda x: (x.tenant.lower(),x.app.lower(),x.epg.lower()))
    def __repr__(self):
        if self.epglist == []:
            return "BD-{}_EPGs-[None]".format(self.bd)
        else:
            return "BD-{}_EPGs-{}".format(self.bd,self.epglist)

def gather_bd_and_epg(apic, cookie):
    url = """https://{apic}/api/node/class/fvBD.json?rsp-subtree=children&rsp-subtree-class=fvRtBd""".format(apic=apic)
    result = GetResponseData(url, cookie)
    return result

def catigorize_bd_to_epg(bd_tree):
    bdlist = []
    for bd in bd_tree:
        bdobj = fvBD(bd['fvBD']['attributes']['dn'])
        if bd['fvBD'].get('children'):
            for epg in bd['fvBD']['children']:
                bdobj.add_epg(fvEPG(epg['fvRtBd']['attributes']['tDn']))
        bdobj.sort_epgs()
        bdlist.append(bdobj)
    return bdlist

def main(apic, cookie):
    clear_screen()
    location_banner('BD to EPG Relationships')
    bd_tree = gather_bd_and_epg(apic,cookie)
    bd_epg_objlist = catigorize_bd_to_epg(bd_tree)
    layoutlist = []
    for bdobj in sorted(bd_epg_objlist, key=lambda x: (x.tenant.lower(), x.bd.lower())):
        #print(bdobj)
        if bdobj.epglist == []:
            #if not currenttenant == bdobj.tenant:
            #    print('-'* 75)
            #    currenttenant = bdobj.tenant
            layoutlist.append((bdobj.tenant,bdobj.bd,''))
        else:
           #if not currenttenant == bdobj.tenant:
           #    print('-' * 75)
           #    currenttenant = bdobj.tenant
            layoutlist.append((bdobj.tenant, bdobj.bd, ('/'.join((bdobj.epglist[0].tenant,bdobj.epglist[0].app,bdobj.epglist[0].epg))).replace('tn-','').replace('ap-','').replace('epg-','')))
          #  print('{:20} {:25} {}|{}|{}'.format(bdobj.tenant, bdobj.bd, bdobj.epglist[0].tenant,bdobj.epglist[0].app,bdobj.epglist[0].epg))
        if len(bdobj.epglist) > 1:
           # if not currenttenant == bdobj.tenant:
           #     print('-' * 75)
           #     currenttenant = bdobj.tenant
            for epg in bdobj.epglist[1:]:
                layoutlist.append(('','',('/'.join((epg.tenant,epg.app,epg.epg))).replace('tn-','').replace('ap-','').replace('epg-','')))
               # print('{:20} {:25} {}|{}|{}'.format('','',epg.tenant,epg.app,epg.epg))
    currenttenant = None
    #import pdb; pdb.set_trace()
    topstringheaders = ('Tenant','Bridge Domain','Tenant/App/EPG')
    sizes = get_column_sizes(layoutlist, minimum=5,baseminimum=topstringheaders)    
    print(' \x1b[1;33;40m{:{tenant}} | {:{bd}} | {:{tae}}\x1b[0m'.format('Tenant','Bridge Domain','Tenant/App/EPG',tenant=sizes[0],bd=sizes[1],tae=sizes[2]))
    for row in layoutlist:
        if not currenttenant == row[0] and row[0] != '':
            print(' ' + '-' * (sum(sizes) + 6))
            currenttenant = row[0]
        print(' {:{tenant}} | {:{bd}} | {:{epg}}'.format(*row,tenant=sizes[0],bd=sizes[1],epg=sizes[2]))
            #print(bdobj.bd, bdobj.epglist)
    #import pdb; pdb.set_trace()
    custom_raw_input('\nContinue...')