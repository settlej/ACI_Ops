#!/bin//python

from __future__ import print_function
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
logger = logging.getLogger('aciops.' + __name__)


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
                        x.health = 'unfit'
                        break
        #for x in cnod
        #import pdb; pdb.set_trace()
        clear_screen()
        location_banner('Node Status and Info')
        if api_pull_error:
            print("\n")
            print("\x1b[0m")
            print("\x1b[1;31;40m APIC API Rest call didn't respond in an timely matter (usually Leaf going down),\n please wait a 1-15 seconds and try again. (This is a APIC resource problem)\x1b[0m")
            custom_raw_input('\n Press enter to retry...')
            import pdb; pdb.set_trace()
            continue
        nodelistarrangment = []
        for x,y in sorted(cnodedict.items(), key=lambda x: int((re.search(r'node.*\d{1,3}', x[0])).group()[5:])):
            if y.fabricSt == 'active' or y.role == 'controller':
                    if hasattr(y, 'systemUpTime'):
                        y.systemUpTime = y.systemUpTime[:-4]
                    if hasattr(y, 'currentTime'):
                        y.currentTime = y.currentTime[:-6]
                        #print(y.health)
                        nodelistarrangment.append((y.name,y.__dict__.get('fabricSt',''),y.__dict__.get('health',''),y.__dict__.get('location',''),y.__dict__.get('inbMgmtAddr',''),y.__dict__.get('oobMgmtAddr',''),y.__dict__.get('role',''),y.serial,y.__dict__.get('version',''),y.__dict__.get('systemUpTime',''),y.__dict__.get('currentTime','')))
                       # #if hasattr(y, 'location'):
                       # #    print('{}'.format(' + 'location: ' + str(y.location))
                       # #else:
                       # #    print('{}'.format(' + 'location: unknown\x1b[0m'))
                       # if hasattr(y, 'inbMgmtAddr'):
                       #     print('{}'.format(inb: inbMgmtAddr)
                       # if hasattr(y, 'oobMgmtAddr'):
                       #     print('{}'.format(oob: oobMgmtAddr)
                       # print('{}'.format(type: role)
                       # print('{}'.format(serial: serial)
                       # if y.version != 'A0':
                       #     print('{}'.format(version: version)
                       # if hasattr(y, 'systemUpTime'):
                       #     print('{}'.format(uptime: systemUpTime[:-4])
                       # if hasattr(y, 'currentTime'):
                       #     print('{}'.format(date: currentTime[:-10])
                       # print('{}'.format(fabricSt)
                       # if hasattr(y, 'location'):
                       #     print('{}'.format(' + 'location: ' + str(y.location))
                       # else:
                       #     print('{}'.format(' + 'location: unknown\x1b[0m'))
                       # if hasattr(y, 'inbMgmtAddr'):
                       #     print('{}'.format(inb: inbMgmtAddr)
                       # if hasattr(y, 'oobMgmtAddr'):
                       #     print('{}'.format(oob: oobMgmtAddr)
                       # print('{}'.format(role)
                       # print('{}'.format(serial: serial)
                       # print('{}'.format(verison: version)
                       # if hasattr(y, 'systemUpTime'):
                       #     print('{}'.format(uptime: systemUpTime[:-4])
                       # if hasattr(y, 'currentTime'):
                       #     print('{}'.format(Hdate: currentTime[:-10])

                    
            else:
                nodelistarrangment.append((y.name,y.fabricSt,y.__dict__.get('health',''),y.__dict__.get('location',''),y.__dict__.get('inbMgmtAddr',''),y.__dict__.get('oobMgmtAddr',''),y.__dict__.get('role',''),y.serial,y.__dict__.get('version',''),y.__dict__.get('systemUpTime',''),y.__dict__.get('currentTime','')))
#
            #    print('{}'.format('\x1b[' + str(ylocation+1) + ';' + str(xlocation) + 'H' + y.name + '\x1b[0m'))
            #    print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + '\x1b[1;31;40m' + y.fabricSt + '\x1b[0m'))
            #    if hasattr(y, 'location'):
            #        print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: ' + str(y.location) + '\x1b[0m'))
            #    else:
            #        print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: unknown\x1b[0m'))
            #    print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'Hserial: ' + y.serial + '\x1b[0m'))
            #    print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'Htype: ' + y.role + '\x1b[0m'))
#
            #xlocation += 33
            #if xlocation >= 133:
            #    ylocation += 12
            #    xlocation = 6
        topstringheaders = ('Node','Status','Health','location','Inband IP','Oob IP','Type','Serial #','Version','Uptime','Current Time')
        #for row in nodelistarrangment:

        sizes = get_column_sizes(nodelistarrangment, minimum=5,baseminimum=topstringheaders)
        print('{:{node}} | {:{status}} | {:{health}} | {:{location}} | {:{inb}} | {:{oob}} | {:{ltype}} | {:{serial}} | {:{version}} | {:{uptime}} | {:{currenttime}}'.format('Node','Status','Health','location','Inband IP','Oob IP','Type','Serial #','Version','Uptime','Current Time',node=sizes[0],status=sizes[1],health=sizes[2],location=sizes[3],inb=sizes[4],oob=sizes[5],ltype=sizes[6],serial=sizes[7],version=sizes[8],uptime=sizes[9],currenttime=sizes[10]))
        print('{:-<{node}} | {:-<{status}} | {:-<{health}} | {:-<{location}} | {:-<{inb}} | {:-<{oob}} | {:-<{ltype}} | {:-<{serial}} | {:-<{version}} | {:-<{uptime}} | {:-<{currenttime}}'.format('','','','','','','','','','','',node=sizes[0],status=sizes[1],health=sizes[2],location=sizes[3],inb=sizes[4],oob=sizes[5],ltype=sizes[6],serial=sizes[7],version=sizes[8],uptime=sizes[9],currenttime=sizes[10]))

        for x,y in sorted(cnodedict.items(), key=lambda x: int((re.search(r'node.*\d{1,3}', x[0])).group()[5:])):
            if y.role == 'controller':
                if y.health == 'unfit':
                    y.health = '\033[1;31;40m{}\033[0m'.format(y.health)
                y.fabricSt = 'N/A'
            if y.role != 'controller':
                if y.fabricSt != 'active':
                    y.fabricSt = '\x1b[1;31;40m{}\x1b[0m'.format(y.fabricSt)
                y.health = 'N/A'

               # print('---'.join(node))
            if 'unfit' in y.health: 
                print('{:{node}} | {:{status}} | {:{health}} | {:{location}} | {:{inb}} | {:{oob}} | {:{ltype}} | {:{serial}} | {:{version}} | {:{uptime}} | {:{currenttime}}'.format(y.name,y.__dict__.get('fabricSt',''),y.__dict__.get('health',''),y.__dict__.get('location',''),y.__dict__.get('inbMgmtAddr',''),y.__dict__.get('oobMgmtAddr',''),y.__dict__.get('role',''),y.serial,y.__dict__.get('version',''),y.__dict__.get('systemUpTime',''),y.__dict__.get('currentTime',''),node=sizes[0],status=sizes[1],health=sizes[2] + 14,location=sizes[3],inb=sizes[4],oob=sizes[5],ltype=sizes[6],serial=sizes[7],version=sizes[8],uptime=sizes[9],currenttime=sizes[10]))
            else:
                print('{:{node}} | {:{status}} | {:{health}} | {:{location}} | {:{inb}} | {:{oob}} | {:{ltype}} | {:{serial}} | {:{version}} | {:{uptime}} | {:{currenttime}}'.format(y.name,y.__dict__.get('fabricSt',''),y.__dict__.get('health',''),y.__dict__.get('location',''),y.__dict__.get('inbMgmtAddr',''),y.__dict__.get('oobMgmtAddr',''),y.__dict__.get('role',''),y.serial,y.__dict__.get('version',''),y.__dict__.get('systemUpTime',''),y.__dict__.get('currentTime',''),node=sizes[0],status=sizes[1],health=sizes[2],location=sizes[3],inb=sizes[4],oob=sizes[5],ltype=sizes[6],serial=sizes[7],version=sizes[8],uptime=sizes[9],currenttime=sizes[10]))
                #print('{:{node}} {:{status}} {:{health}} {:{location}} {:{inb}} {:{oob}} {:{type}} {:{serial}} {:{version}} {:{uptime}} {:{currenttime}}'.format(y.name,y.__dict__.get('fabricSt',''),y.__dict__.get('health',''),y.__dict__.get('location',''),y.__dict__.get('inbMgmtAddr',''),y.__dict__.get('oobMgmtAddr',''),y.__dict__.get('role',''),y.serial,y.__dict__.get('version',''),y.__dict__.get('systemUpTime',''),y.__dict__.get('currentTime','')))

        #for x,y in sorted(cnodedict.items(), key=lambda x: int((re.search(r'node.*\d{1,3}', x[0])).group()[5:])):
        #    if y.fabricSt == 'active' or y.role == 'controller':
        #        try:
        #            print('{}'.format('\x1b[' + str(ylocation+1) + ';' + str(xlocation) + 'H' + y.name + '\x1b[0m'))
        #            if y.role == 'controller':
        #                #print(y.health)
        #                print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + y.health + '\x1b[0m'))
        #                #if hasattr(y, 'location'):
        #                #    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: ' + str(y.location) + '\x1b[0m'))
        #                #else:
        #                #    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: unknown\x1b[0m'))
        #                if hasattr(y, 'inbMgmtAddr'):
        #                    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'Hinb: ' + y.inbMgmtAddr + '\x1b[0m'))
        #                if hasattr(y, 'oobMgmtAddr'):
        #                    print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'Hoob: ' + y.oobMgmtAddr + '\x1b[0m'))
        #                print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'Htype: ' + y.role + '\x1b[0m'))
        #                print('{}'.format('\x1b[' + str(ylocation+6) + ';' + str(xlocation) + 'Hserial: ' + y.serial + '\x1b[0m'))
        #                if y.version != 'A0':
        #                    print('{}'.format('\x1b[' + str(ylocation+7) + ';' + str(xlocation) + 'Hversion: ' + y.version + '\x1b[0m'))
        #                if hasattr(y, 'systemUpTime'):
        #                    print('{}'.format('\x1b[' + str(ylocation+8) + ';' + str(xlocation) + 'Huptime: ' + y.systemUpTime[:-4] + '\x1b[0m'))
        #                if hasattr(y, 'currentTime'):
        #                    print('{}'.format('\x1b[' + str(ylocation+9) + ';' + str(xlocation) + 'Hdate: ' + y.currentTime[:-10] + '\x1b[0m'))
        #            else:
        #                print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + y.fabricSt + '\x1b[0m'))
        #                if hasattr(y, 'location'):
        #                    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: ' + str(y.location) + '\x1b[0m'))
        #                else:
        #                    print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: unknown\x1b[0m'))
        #                if hasattr(y, 'inbMgmtAddr'):
        #                    print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'Hinb: ' + y.inbMgmtAddr + '\x1b[0m'))
        #                if hasattr(y, 'oobMgmtAddr'):
        #                    print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'Hoob: ' + y.oobMgmtAddr + '\x1b[0m'))
        #                print('{}'.format('\x1b[' + str(ylocation+6) + ';' + str(xlocation) + 'Htype: ' + y.role + '\x1b[0m'))
        #                print('{}'.format('\x1b[' + str(ylocation+7) + ';' + str(xlocation) + 'Hserial: ' + y.serial + '\x1b[0m'))
        #                print('{}'.format('\x1b[' + str(ylocation+8) + ';' + str(xlocation) + 'Hverison: ' + y.version + '\x1b[0m'))
        #                if hasattr(y, 'systemUpTime'):
        #                    print('{}'.format('\x1b[' + str(ylocation+9) + ';' + str(xlocation) + 'Huptime: ' + y.systemUpTime[:-4] + '\x1b[0m'))
        #                if hasattr(y, 'currentTime'):
        #                    print('{}'.format('\x1b[' + str(ylocation+10) + ';' + str(xlocation) + 'Hdate: ' + y.currentTime[:-10] + '\x1b[0m'))
        #        except Exception, err:
        #            print Exception, err
        #            print(y.__dict__)
        #            import pdb; pdb.set_trace()
        #            
        #    else:
        #        print('{}'.format('\x1b[' + str(ylocation+1) + ';' + str(xlocation) + 'H' + y.name + '\x1b[0m'))
        #        print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + '\x1b[1;31;40m' + y.fabricSt + '\x1b[0m'))
        #        if hasattr(y, 'location'):
        #            print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: ' + str(y.location) + '\x1b[0m'))
        #        else:
        #            print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + 'location: unknown\x1b[0m'))
        #        print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'Hserial: ' + y.serial + '\x1b[0m'))
        #        print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'Htype: ' + y.role + '\x1b[0m'))
#
        #    xlocation += 33
        #    if xlocation >= 133:
        #        ylocation += 12
        #        xlocation = 6

        ask = custom_raw_input('\nRefresh? [Y]: ') or 'Y'
        if ask.lower() != '':
            if ask[0].upper() == 'Y':
                continue
            else:
                break