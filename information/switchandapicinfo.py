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


class customFabricNode():
    def __init__(self,kwargs):
        self.__dict__.update(**kwargs)
        self.health = ''
    def __setattr__(self, key, value):
        self.__dict__[key] = value
    def __repr__(self):
        return self.dn

def requestnodeinfo(url, cookie, q):
    try:
        result = GetResponseData(url, cookie)
        q.put(result)
    except:
        pass
        q.put({'error': 'timeout'})
    
class geolocation():
    def __init__(self,kwargs):
        self.__dict__.update(**kwargs)
    def __setattr__(self, key, value):
        self.__dict__[key] = value
    def __repr__(self):
        return self.dn

class infraWiNode():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return self.nodeName


def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        #cnodelist = []
        nodethreadlist = []
        urllist = []
        cnodedict = {}
        q = Queue.Queue()
        url = """https://{apic}/api/node/class/geoRsNodeLocation.json""".format(apic=apic)
        georesult = GetResponseData(url, cookie)
        infralist = []
        url = """https://{apic}/api/class/infraWiNode.json""".format(apic=apic)
        infraresult = GetResponseData(url, cookie)
        for x in infraresult:
            infralist.append(infraWiNode(x['infraWiNode']['attributes']))
        finalinfralist = [list(g) for k, g in itertools.groupby(sorted(infralist, key=lambda x: x.id), lambda x: x.id)]
        geolist = [geolocation(x['geoRsNodeLocation']['attributes']) for x in georesult]
        url = """https://{apic}/api/node/class/geoRack.json""".format(apic=apic)
        geonameresult = GetResponseData(url, cookie)
        for x in geolist:
            for y in geonameresult:
                #print(x.dn, y['geoRack']['attributes']['dn'])
                if y['geoRack']['attributes']['dn'] in x.dn:
                    x.name = y['geoRack']['attributes']['name']
        url = """https://{apic}/api/class/fabricNode.json""".format(apic=apic)
        result = GetResponseData(url, cookie)
        for node in sorted(result, key=lambda a: int(a['fabricNode']['attributes']['id']) ):
            #print(node['fabricNode']['attributes']['id'])
            cnodedict[node['fabricNode']['attributes']['dn']] = customFabricNode(node['fabricNode']['attributes'])
       #url = """https://{apic}/api/node/class/topSystem.json""".format(apic=apic)
        for uu in cnodedict.values():
            #import pdb; pdb.set_trace()
            if uu.fabricSt == 'active' or uu.role == 'controller':
                urllist.append("""https://{apic}/api/class/topSystem.json?query-target-filter=eq(topSystem.id,"{nodeid}")""".format(apic=apic,nodeid=uu.id))
        for url in urllist:
            t = threading.Thread(target=requestnodeinfo, args=[url,cookie,q])
            t.start()
            nodethreadlist.append(t)
        api_pull_error = False
        finalresultlist = []
        for x in nodethreadlist:
            x.join()
            nodetopsystem = q.get()
            finalresultlist.append(nodetopsystem)
        for x in finalresultlist:
            xlocation = 6
            ylocation = 3
            try:
                if type(x) == dict and x.get('error') or x == []:
                    continue

                else:
                    cnodedict[x[0]['topSystem']['attributes']['dn'].replace('/sys', '')].__dict__.update(**x[0]['topSystem']['attributes'])
            except Exception as e:
                #print(e)
                api_pull_error = True
                #import pdb; pdb.set_trace()
        for k,v in cnodedict.items():
            for x in geolist:
                cnodedict[k].health = 'fully-fit'
                if x.tDn in v.dn:
                    cnodedict[k].location = x.name
                    break
        unfitlist = []
        for xgroup in finalinfralist:
            for xchild in xgroup:
                if xchild.health != 'fully-fit':
                    unfitlist.append(xchild)
        unfitlist = list(set(unfitlist))
        #import pdb; pdb.set_trace()
        if len(unfitlist) > 0:
            for x in cnodedict.values():
                for fl in unfitlist:
                    #import pdb; pdb.set_trace()
                    #print(x.id, fl.id)
                    if x.id == fl.id:
                        x.health = '\x1b[1;31;40munfit\x1b[0m'
                        break
        #for x in cnod
        #import pdb; pdb.set_trace()
        clear_screen()
        if api_pull_error:
            print("\n")
            print("\x1b[0m")
            print("\x1b[1;31;40m APIC API Rest call didn't respond in an timely matter (usually Leaf going down),\n please wait a 1-15 seconds and try again. (This is a APIC resource problem)\x1b[0m")
            custom_raw_input('\n Press enter to retry...')
            import pdb; pdb.set_trace()
            continue
        for x,y in sorted(cnodedict.items(), key=lambda x: int((re.search(r'node.*\d{1,3}', x[0])).group()[5:])):
            if y.fabricSt == 'active' or y.role == 'controller':
                try:
                    print('{}'.format('\x1b[' + str(ylocation+1) + ';' + str(xlocation) + 'H' + y.name + '\x1b[0m'))
                    if y.role == 'controller':
                        #print(y.health)
                        print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + y.health + '\x1b[0m'))
                        #if hasattr(y, 'location'):
                        #    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: ' + str(y.location) + '\x1b[0m'))
                        #else:
                        #    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: unknown\x1b[0m'))
                        if hasattr(y, 'inbMgmtAddr'):
                            print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'Hinb: ' + y.inbMgmtAddr + '\x1b[0m'))
                        if hasattr(y, 'oobMgmtAddr'):
                            print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'Hoob: ' + y.oobMgmtAddr + '\x1b[0m'))
                        print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'Htype: ' + y.role + '\x1b[0m'))
                        print('{}'.format('\x1b[' + str(ylocation+6) + ';' + str(xlocation) + 'Hserial: ' + y.serial + '\x1b[0m'))
                        if y.version != 'A0':
                            print('{}'.format('\x1b[' + str(ylocation+7) + ';' + str(xlocation) + 'Hversion: ' + y.version + '\x1b[0m'))
                        if hasattr(y, 'systemUpTime'):
                            print('{}'.format('\x1b[' + str(ylocation+8) + ';' + str(xlocation) + 'Huptime: ' + y.systemUpTime[:-4] + '\x1b[0m'))
                        if hasattr(y, 'currentTime'):
                            print('{}'.format('\x1b[' + str(ylocation+9) + ';' + str(xlocation) + 'Hdate: ' + y.currentTime[:-10] + '\x1b[0m'))
                    else:
                        print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + y.fabricSt + '\x1b[0m'))
                        if hasattr(y, 'location'):
                            print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: ' + str(y.location) + '\x1b[0m'))
                        else:
                            print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: unknown\x1b[0m'))
                        if hasattr(y, 'inbMgmtAddr'):
                            print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'Hinb: ' + y.inbMgmtAddr + '\x1b[0m'))
                        if hasattr(y, 'oobMgmtAddr'):
                            print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'Hoob: ' + y.oobMgmtAddr + '\x1b[0m'))
                        print('{}'.format('\x1b[' + str(ylocation+6) + ';' + str(xlocation) + 'Htype: ' + y.role + '\x1b[0m'))
                        print('{}'.format('\x1b[' + str(ylocation+7) + ';' + str(xlocation) + 'Hserial: ' + y.serial + '\x1b[0m'))
                        print('{}'.format('\x1b[' + str(ylocation+8) + ';' + str(xlocation) + 'Hverison: ' + y.version + '\x1b[0m'))
                        if hasattr(y, 'systemUpTime'):
                            print('{}'.format('\x1b[' + str(ylocation+9) + ';' + str(xlocation) + 'Huptime: ' + y.systemUpTime[:-4] + '\x1b[0m'))
                        if hasattr(y, 'currentTime'):
                            print('{}'.format('\x1b[' + str(ylocation+10) + ';' + str(xlocation) + 'Hdate: ' + y.currentTime[:-10] + '\x1b[0m'))
                except Exception, err:
                    print Exception, err
                    print(y.__dict__)
                    import pdb; pdb.set_trace()
                    
            else:
                print('{}'.format('\x1b[' + str(ylocation+1) + ';' + str(xlocation) + 'H' + y.name + '\x1b[0m'))
                print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + '\x1b[1;31;40m' + y.fabricSt + '\x1b[0m'))
                if hasattr(y, 'location'):
                    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: ' + str(y.location) + '\x1b[0m'))
                else:
                    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: unknown\x1b[0m'))
                print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'Hserial: ' + y.serial + '\x1b[0m'))
                print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'Htype: ' + y.role + '\x1b[0m'))

            xlocation += 33
            if xlocation >= 133:
                ylocation += 12
                xlocation = 6
        ask = custom_raw_input('\nRefresh? [Y]: ') or 'Y'
        if ask.lower() != '':
            if ask[0].upper() == 'Y':
                continue
            else:
                break