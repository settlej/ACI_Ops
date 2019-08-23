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
import ipaddress
from localutils.custom_utils import *

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


class nexthopObject():
    def __init__(self, nexthopif=None, nexthopaddr=None, nexthopstatus=None,
                 nexthoptype=None, nexthopvrf=None, nexthoprouteType=None):
        self.nexthopif = nexthopif
        self.nexthopaddr = nexthopaddr
        self.nexthopstatus = nexthopstatus
        self.nexthoptype = nexthoptype
        self.nexthopvrf = nexthopvrf
        self.nexthoprouteType = nexthoprouteType
    def __repr__(self):
        return self.nexthopaddr
    def __getitem__(self, route):
        if route in self.nexthopaddr:
            return self.nexthopaddr
        else:
            return None

class routeObject():
    def __init__(self, vrf=None, routeprefix=None, subnetmask=None, nexthoplist=[]):
        self.vrf = vrf
        self.routeprefix = routeprefix
        self.subnetmask = subnetmask
        self.nexthoplist = nexthoplist
    def __repr__(self):
        return self.routeprefix
    def __getitem__(self, route):
        if route in self.routeprefix:
            return self.routeprefix
        else:
            return None
    def add_nexthop(self, nexthoplistitem):
        self.nexthoplist.append(nexthoplistitem)

class searchedObject():
    def __init__(self, vrf=None, bd=None, tenant=None,app=None,epg=None,subnetlist=None, fvRsCons=None,fvRsProv=None, vzTaboo=None):
        self.vrf = vrf
        self.bd = bd
        self.tenant = tenant
        self.app = app
        self.epg = epg
        self.subnetlist = subnetlist
        self.fvRsCons = fvRsCons
        self.fvRsProv = fvRsProv
        self.vzTaboo = vzTaboo
        self.tDn = 'uni/tn-{}/ap-{}/epg-{}'.format(tenant,app,epg)
    def __repr__(self):
        return 'tn-{}:vrf-{}/ap-{}/epg-{}'.format(self.tenant,self.vrf,self.app,self.epg)


def getallroutes(leaf,vrf,tenant):
    #get_Cookie()
    url = """https://{apic}/api/node/mo/topology/pod-1/node-{}/sys/uribv4/dom-{}:{}.json?rsp-subtree=full&query-target=subtree&target-subtree-class=uribv4Route""".format(leaf,vrf,tenant,apic=apic)
    result, totalcount = GetResponseData(url)
    routelist = []
    for routes in result:
        routeprefix = routes['uribv4Route']['attributes']['prefix']
        subnetmask = routes['uribv4Route']['attributes']['prefixLength']
        dn = routes['uribv4Route']['attributes']['dn']
        vrf = dn[5:6].replace('dom-', '')
        if routes['uribv4Route'].get('children'):
            nexthopobjectlist = []
            for route in routes['uribv4Route']['children']:
                nexthopvrf = route['uribv4Nexthop']['attributes']['vrf']
                nexthopaddr = route['uribv4Nexthop']['attributes']['addr']
                nexthopif = route['uribv4Nexthop']['attributes']['if']
                nexthopstatus = route['uribv4Nexthop']['attributes']['active']
                nexthoptype = route['uribv4Nexthop']['attributes']['type']
                nexthoprouteType = route['uribv4Nexthop']['attributes']['routeType']
                #print(nexthopif,)
                nexthopobjectlist.append(nexthopObject(nexthopif=nexthopif, 
                    nexthopaddr=nexthopaddr, nexthopstatus=nexthopstatus, nexthoptype=nexthoptype,
                    nexthopvrf=nexthopvrf, nexthoprouteType=nexthoprouteType))
        routelist.append(routeObject(routeprefix=routeprefix, subnetmask=subnetmask, nexthoplist=nexthopobjectlist))
    return routelist
                
    #ask = custom_raw_input("what ip address?: ")
    #for x in routelist:
    #    if ask == x.routeprefix[:-3]:
    #        print("""{:25}\t {:25}\t {}\t {}\t {}""".format(x.routeprefix, x.nexthopaddr, x.nexthoptype, x.nexthoprouteType, x.nexthopvrf))
def allnexthopIPs(ip,results1):
    for route in results1:
        if route['ipv4Addr']['attributes']['addr'] == ip:
            return str(route['ipv4Addr']['attributes']['dn'].split('/')[2:3])

#def nexthopip_lookup(ip):
#    url = """https://{apic}/api//class/ipv4Addr.json?&query-target-filter==eq(ipv4Addr.addr,"{}")""".format(ip)
#    result, totalcount = GetResponseData(url)
#    for x in result:
#        if x != '':
#            node = result[0]['ipv4Addr']['attributes']['dn'].split('/')[2:3]
            #print(node)

    #print(result)
    #print(result[0]['ipv4Addr']['attributes']['dn'])

"""Use this for nexthop lookup - https://192.168.255.2/api//class/ipv4Addr.json?&query-target-filter==eq(ipv4Addr.addr,"10.255.216.66/32")"""
"""nexthop lookup -  https://192.168.255.2/api//class/ipv4If.json?rsp-subtree=children&rsp-subtree-filter==eq(ipv4Addr.addr,"10.255.216.66/32")"""

"""tunnel interfaces"""
"""url = https://192.168.255.2/api/node/class/topology/pod-1/node-101/tunnelIf.json?subscription=yes&order-by=tunnelIf.name|desc&page=0&page-size=100"""

class contractObject():
    def __init__(self,vzSubjectlist, name=None, scope=None, ):
        self.name = name
        self.scope = scope
        self.vzSubjectlist = vzSubjectlist
    def __repr__(self):
        return self.name

class vzSubjObject():
    def __init__(self,vzSubjectattObjectlist, name=None, unidirectional=False, unid_cons_to_prov_container=None, unid_prov_to_cons_container=None, uni_container=None, reversedports=False):
        self.name = name
        self.unidirectional = unidirectional
        self.unid_cons_to_prov_container = unid_cons_to_prov_container
        self.unid_prov_to_cons_container = unid_prov_to_cons_container
        self.reversedports = reversedports
        self.vzSubjectattObjectlist = vzSubjectattObjectlist
    def __repr__(self):
        return self.name

class vzSubjectattObject():
    def __init__(self, action=None, rn=None, tDn=None, tnVzFilterName=None, priority=None, Filterobjectlist=None):
        self.action = action
        self.rn = rn
        self.tDn = tDn
        self.tnVzFilterName = tnVzFilterName
        self.Filterobjectlist = Filterobjectlist
        self.priority = priority
    def __repr__(self):
        return self.rn

class vzFilterObject():
    def __init__(self, name=None, dn=None, tnVzFilterName=None, override=None):
        self.name = name
        self.dn = dn
        self.tnVzFilterName = tnVzFilterName
        self.override = override
    def __repr__(self):
        return self.tnVzFilterName

class vzFilterEntryObject():
    def __init__(self, name=None, protocol=None, etherT=None, sFromPort=None,sToPort=None, dFromPort=None, dToPort=None, tcpRules=None):
        self.name = name
        self.etherT = etherT
        self.protocol = protocol
        self.sFromPort = sFromPort
        self.sToPort = sToPort
        self.dFromPort = dFromPort
        self.dToPort = dToPort
        self.tcpRules = tcpRules
    def __repr__(self):
        return "protocol={}src=({})dest=({})".format(self.protocol,self.sFromPort + ',' + self.sToPort,self.dFromPort + ',' + self.dToPort)

class vzRsFiltAtt():
    def __init__(self, action=None, tnVzFilterName=None, tDn=None, Filterobjectlist=None, priority=None):
        self.action = action
        self.tnVzFilterName = tnVzFilterName
        self.tDn = tDn
        self.Filterobjectlist = Filterobjectlist
        self.priority = priority
    def __repr__(self):
        return self.tDn

def getfilterinfo(filter,filter_result):
    filterlist = []
    for vzfilter in filter_result:
        #print(filter)
        if vzfilter['vzFilter']['attributes']['dn'] == filter:
            for entry in vzfilter['vzFilter']['children']:
                if entry.get('vzEntry'):
                    name = entry['vzEntry']['attributes']['name']
                    protocol = entry['vzEntry']['attributes']['prot']
                    if protocol == 'unspecified':
                        protocol = 'any'
                    etherT = entry['vzEntry']['attributes']['etherT']
                    if etherT == 'unspecified':
                        etherT = 'any'
                    sFromPort = entry['vzEntry']['attributes']['sFromPort']
                    if sFromPort == 'unspecified':
                        sFromPort = 'any'
                    sToPort = entry['vzEntry']['attributes']['sToPort']
                    if sToPort == 'unspecified':
                        sToPort = 'any'
                    dFromPort = entry['vzEntry']['attributes']['dFromPort']
                    if dFromPort == 'unspecified':
                        dFromPort = 'any'
                    dToPort = entry['vzEntry']['attributes']['dToPort']
                    if dToPort == 'unspecified':
                        dToPort = 'any'
                    tcpRules = entry['vzEntry']['attributes']['tcpRules']
                    if tcpRules == 'est':
                        tcpRules = 'established'
                    filterlist.append(vzFilterEntryObject(
                                                name=name,
                                                protocol=protocol,
                                                etherT=etherT,
                                                sFromPort=sFromPort,
                                                sToPort=sToPort,
                                                dFromPort=dFromPort,
                                                dToPort=dToPort,
                                                tcpRules=tcpRules))
    return filterlist

def gathervzFilter():
    url = """https://{apic}/api/node/class/vzFilter.json?rsp-subtree=full""".format(apic=apic)
    result, totalamount = GetResponseData(url)
    return result

def getcontractinfo(contract):
    #get_Cookie()
    temp_list = []
    allvzSubjectObjects = []
    temp_list_prov_to_cons = []
    temp_list_cons_to_prov = []
    unid_cons_to_prov_container = []
    unid_prov_to_cons_container = []
    url = """https://{apic}/api/node/class/vzBrCP.json?query-target-filter=and(eq(vzBrCP.name,"{}"))&rsp-subtree=full""".format(contract,apic=apic)
    #print(url)
    result, totalamount = GetResponseData(url)
    filter_result = gathervzFilter()
    #filter_result, filtertotalamount = GetResponseData(filterurl)
    scope = result[0]['vzBrCP']['attributes']['scope']
    for vzBrCP_children in result[0]['vzBrCP']['children']:
        if vzBrCP_children.get('vzSubj') and vzBrCP_children['vzSubj'].get('children'):
            for vzSubjatt in vzBrCP_children['vzSubj']['children']:
                if vzSubjatt.get('vzRsSubjFiltAtt') and vzSubjatt['vzRsSubjFiltAtt']['attributes']['state'] == 'formed':
                    unidirect = False
                    #uni_provcontainer=None
                    #uni_conscontainer=None
                    currentvzSubjATTobject = vzSubjectattObject(action=vzSubjatt['vzRsSubjFiltAtt']['attributes']['action'],
                                                tDn=vzSubjatt['vzRsSubjFiltAtt']['attributes']['tDn'],
                                                rn=vzSubjatt['vzRsSubjFiltAtt']['attributes']['rn'],
                                                tnVzFilterName=vzSubjatt['vzRsSubjFiltAtt']['attributes']['tnVzFilterName'],
                                                Filterobjectlist=getfilterinfo(vzSubjatt['vzRsSubjFiltAtt']['attributes']['tDn'], filter_result),
                                                priority=vzSubjatt['vzRsSubjFiltAtt']['attributes']['priorityOverride'])
                    temp_list.append(currentvzSubjATTobject)
                elif vzSubjatt.get('vzOutTerm'):
                    unidirect = True
                    if vzSubjatt['vzOutTerm'].get('children'):
                        for subj in vzSubjatt['vzOutTerm']['children']:
                            #print(subj)
                            Outterm = vzRsFiltAtt(tnVzFilterName=subj['vzRsFiltAtt']['attributes']['tnVzFilterName'],
                                                tDn=subj['vzRsFiltAtt']['attributes']['tDn'],
                                                action=subj['vzRsFiltAtt']['attributes']['action'],
                                                Filterobjectlist=getfilterinfo(subj['vzRsFiltAtt']['attributes']['tDn'], filter_result),
                                                priority=subj['vzRsFiltAtt']['attributes']['priorityOverride'])
                            temp_list_prov_to_cons.append(Outterm)

                    unid_prov_to_cons_container = temp_list_prov_to_cons
                    temp_list_prov_to_cons = []

                elif vzSubjatt.get('vzInTerm'):
                    unidirect = True
                    if vzSubjatt['vzInTerm'].get('children'):
                        for subj in vzSubjatt['vzInTerm']['children']:
                            #print(subj)
                            INterm = vzRsFiltAtt(tnVzFilterName=subj['vzRsFiltAtt']['attributes']['tnVzFilterName'],
                                                tDn=subj['vzRsFiltAtt']['attributes']['tDn'],
                                                action=subj['vzRsFiltAtt']['attributes']['action'],
                                                Filterobjectlist=getfilterinfo(subj['vzRsFiltAtt']['attributes']['tDn'], filter_result),
                                                priority=subj['vzRsFiltAtt']['attributes']['priorityOverride'])
                            temp_list_cons_to_prov.append(INterm)
                    unid_cons_to_prov_container = temp_list_cons_to_prov
                    temp_list_cons_to_prov = []

            currentSubjObject = vzSubjObject(name=vzBrCP_children['vzSubj']['attributes']['name'], 
                                    reversedports=vzBrCP_children['vzSubj']['attributes']['revFltPorts'],
                                    unidirectional=unidirect,
                                    unid_cons_to_prov_container=unid_cons_to_prov_container,
                                    unid_prov_to_cons_container=unid_prov_to_cons_container,
                                    vzSubjectattObjectlist=temp_list)
            allvzSubjectObjects.append(currentSubjObject)
            temp_list = []
    return contractObject(name=contract,scope=scope, vzSubjectlist=allvzSubjectObjects)

#def getallContractrelationships():
#    url = """https://{apic}/api/class/vzBrCP.json?rsp-subtree=full"""
#    result, ammount = GetResponseData(url)
#    contractconslist = []
#    contractprovlist = []
#    tempconslist = []
#    tempprovlist = []
#    for contract in result:
#        if contract['vzBrCP'].get('children'):
#            for child in contract['vzBrCP']['children']:
#                if child.get('vzDirAssDef'):
#                    for tod in child['vzDirAssDef']['children']:
#                        if tod.get('vzProvDef'):
#                            if tod['vzProvDef']['attributes']['name'] == 'uSEG-VCENTER':
#                                print('uSEG-VCENTER provide :' + contract['vzBrCP']['attributes']['name'])
#                            elif tod['vzProvDef']['attributes']['name'] == 'EPG-VL9-SERVERS':
#                                print('EPG-VL9-SERVERS provide :' + contract['vzBrCP']['attributes']['name'])
#                        elif tod.get('vzConsDef'):
#                            if tod['vzConsDef']['attributes']['name'] == 'uSEG-VCENTER':
#                                print('uSEG-VCENTER consume :' + contract['vzBrCP']['attributes']['name'])
#                            elif tod['vzConsDef']['attributes']['name'] == 'EPG-VL9-SERVERS':
#                                print('EPG-VL9-SERVERS consume :' + contract['vzBrCP']['attributes']['name'])
#

def getvzAnyContactusage():
    url = """https://{apic}/api/class/vzAny.json?rsp-subtree=children&rsp-subtree-class=vzRsAnyToProv,vzRsAnyToCons""".format(apic=apic)
    result, amount = GetResponseData(url)
    return result



   ## https://192.168.255.2/api/node/class/vzFilter.json?rsp-subtree=full for filter info

def getbdfromepg(tenant,app,epg):
    #get_Cookie()
    fvRsProv = []
    fvRsCons = []
    url = """https://{apic}/api/node/mo/uni/tn-{tenant}/ap-{app}/epg-{epg}.json?query-target=children""".format(tenant=tenant,app=app,epg=epg,apic=apic)
    #print(url)
    result, totalamount = GetResponseData(url)
    for target in result:
        #print(target)
        if target.get('fvRsBd'):
            bd =  target['fvRsBd']['attributes']['tnFvBDName']
        elif target.get('fvRsCons'):
            fvRsCons.append(target['fvRsCons']['attributes']['tnVzBrCPName'])
        elif target.get('fvRsConsIf'):
            fvRsCons.append(target['fvRsConsIf']['attributes']['tnVzCPIfName'])
        elif target.get('fvRsProv'):
            fvRsProv.append(target['fvRsProv']['attributes']['tnVzBrCPName'])
        elif target.get('fvRsProvIf'):
            fvRsProv.append(target['fvRsProvIf']['attributes']['tnVzCPIfName'])
    return bd,fvRsCons,fvRsProv

#def getfvRsCons():
#    url = """https://{apic}/api/node/class/fvRsCons.json"""
#    result, totalamount = GetResponseData(url)
#    return result
#
#def getfvRsProv():
#    url = """https://{apic}/api/node/class/fvRsProv.json"""
#    result, totalamount = GetResponseData(url)
#    return result

def getBDsubnetsandvrf(bd,tenant):
    url = """https://{apic}/api/node/mo/uni/tn-{tenant}/BD-{bd}.json?query-target=children&target-subtree-class=fvRsCtx,fvSubnet""".format(bd=bd,tenant=tenant,apic=apic)
    #get_Cookie()
    subnetlist = []
    result, totalamount = GetResponseData(url)
    #print(result)
    for level in result:
        #print(level)
        if level.get('fvSubnet'):
            subnetlist.append(level['fvSubnet']['attributes']['ip'])
        elif level.get('fvRsCtx'):
            vrf = level['fvRsCtx']['attributes']['tnFvCtxName']
    return subnetlist,vrf

def checkvzTaboo(tDn):
    url = """https://{apic}/api/class/vzTaboo.json?rsp-subtree=full""".format(apic=apic)
    #get_Cookie()
    result, totalamount = GetResponseData(url)
    #print(result)
    for vzTaboo in result:
        if vzTaboo['vzTaboo'].get('children'):
            for child in vzTaboo['vzTaboo']['children']:
                #print(child)
                if child.get('vzRtProtBy'):
                    if child['vzRtProtBy']['attributes']['tDn'] == tDn:
                        return vzTaboo
                    #for vzRtProtBy in child['vzRtProtBy']:
                        #if vzRtProprint('hi')#print(vzRtProtBy)
                        
      #              if vzRtProtBy.get('vzRtProtBy'):
      #                  if vzRtProtBy['vzRtProtBy']['attributes']['tDn'] == tDn:
      #                      return vzTaboo


def allips():
    #get_Cookie()
    url = """https://{apic}/api//class/ipv4Addr.json""".format(apic=apic)
    return GetResponseData(url)

def sourceEPGinfo():
    print('\n')
    tenant = custom_raw_input("(EPG1) What tenant [default=SI] ") or 'SI'
    app = custom_raw_input("(EPG1) What App [default=APP-HQ] ") or 'APP-HQ'
    epg = custom_raw_input("(EPG1) What epg [default=EPG-VL9-SERVERS] ") or 'EPG-VL9-SERVERS'
    bd,fvRsCons,fvRsProv = getbdfromepg(tenant,app,epg)
    subnetlist,vrf = getBDsubnetsandvrf(bd=bd,tenant=tenant)
    sobject = searchedObject(vrf=vrf, bd=bd, tenant=tenant,app=app,epg=epg,subnetlist=subnetlist,
                  fvRsCons=fvRsCons,fvRsProv=fvRsProv)
    vzTaboo = checkvzTaboo(sobject.tDn)

    if vzTaboo:
        sobject.vzTaboo = vzTaboo
    #print(sobject.vzTaboo)
    return sobject

def destEPGinfo():
    print('\n')
    #print("\x1b[7")
    #tenant = custom_raw_input("\x1b[1;152HWhat tenant [default=SI] ") or 'SI'
    tenant = custom_raw_input("(EPG2) What tenant [default=SI] ") or 'SI'
    app = custom_raw_input("(EPG2) What App [default=APP-ISE] ") or 'APP-ISE'
    epg = custom_raw_input("(EPG2) What epg [default=EPG-VL10-ISE] ") or 'EPG-VL10-ISE'
    #app = custom_raw_input("\x1b[2;152Hwhat App [default=APP-HQ] ") or 'APP-HQ'
    #epg = custom_raw_input("\x1b[3;152Hwhat epg [default=EPG-VL9-SERVERS] ") or 'EPG-VL9-SERVERS'
    bd,fvRsCons,fvRsProv = getbdfromepg(tenant,app,epg)
    subnetlist,vrf = getBDsubnetsandvrf(bd=bd,tenant=tenant)
    dobject = searchedObject(vrf=vrf, bd=bd, tenant=tenant,app=app,epg=epg,subnetlist=subnetlist,
                  fvRsCons=fvRsCons,fvRsProv=fvRsProv)
    vzTaboo = checkvzTaboo(dobject.tDn)
    if vzTaboo:
        dobject.vzTaboo = vzTaboo
    #print(dobject.vzTaboo)
    return dobject

def gatheranddisplaycontractandfiltersbetweenepgs(match):
    
    contractlevel1dict = {}
    contractlevel2dict = {}
    contractlevel3dict = {}
    
    for contract in match:
        contractobject = getcontractinfo(contract)
        print('\n\tContract: \x1b[0;30;47m ' + contractobject.name + ' \x1b[0m')
        print('\tContract Scope: ' + contractobject.scope)
        for vzsubject in contractobject.vzSubjectlist:
            print('\r')
            print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','Name','Protocol','Ether-type','SFromPort','SToPort','DFromPort','DToPort','TCPRule'))
            print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12))

            if vzsubject.unidirectional:
                print('\t\t[Unidirection Rules]  {}\x1b[1;33;44m{}\x1b[0m'.format('Subject: ', vzsubject.name))
                print('\t\t\t{} {}'.format('Consumer-to-Provider fiters: ', '' ))
                for unidirectionalfilter in vzsubject.unid_cons_to_prov_container:
                    if unidirectionalfilter.priority == 'default' or unidirectionalfilter.priority == 'level2':
                        unidirectionalfilter.priority = 'level2'
                        print('\t\t\t\t{}: {} \x1b[1;33;40m{:20}\x1b[0m'.format(unidirectionalfilter.action,unidirectionalfilter.priority,unidirectionalfilter.tnVzFilterName))
                        for efilter in unidirectionalfilter.Filterobjectlist:
                            print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('',efilter.name,efilter.protocol,efilter.etherT,efilter.sFromPort,efilter.sToPort,efilter.dFromPort,efilter.dToPort,efilter.tcpRules))
                print('\t\t\t{} {}'.format('Provider-to-Consumer fiters: ', ' '))
                #print('\t\t\t\t{:8}{:20}{:30}'.format('action','priority','filter-containter'))
                #print('\t\t\t\t{:_<8}{:_<20}{:_<30}'.format('','',''))
                for unidirectionalfilter in vzsubject.unid_prov_to_cons_container:
                    if unidirectionalfilter.priority == 'default' or unidirectionalfilter.priority == 'level2':
                        unidirectionalfilter.priority = 'level2'
                        print('\t\t\t\t{}: {} \x1b[1;33;40m{:20}\x1b[0m'.format(unidirectionalfilter.action,unidirectionalfilter.priority,unidirectionalfilter.tnVzFilterName))
                        for efilter in unidirectionalfilter.Filterobjectlist:
                            print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('',efilter.name,efilter.protocol,efilter.etherT,efilter.sFromPort,efilter.sToPort,efilter.dFromPort,efilter.dToPort,efilter.tcpRules))

            else:
                #print('\r')
                print('\t\t[Bi-direction Rules]  {}\x1b[1;33;44m{}\x1b[0m'.format('Subject: ', vzsubject.name))

            for vzfilter in vzsubject.vzSubjectattObjectlist:
                if vzfilter.priority == 'level1':
                    contractlevel1dict[vzfilter] = vzfilter.priority
                elif vzfilter.priority == 'default' or vzfilter.priority == 'level2':
                    vzfilter.priority = 'level2'
                    contractlevel2dict[vzfilter] = vzfilter.priority
                else:
                    contractlevel3dict[vzfilter] = vzfilter.priority
            combinedlevels = [contractlevel3dict,contractlevel2dict,contractlevel1dict]
            contractlevel1dict = {}
            contractlevel2dict = {}
            contractlevel3dict = {}
            for level in combinedlevels:
                for entry,priority in level.items():
                    if entry.action == 'deny':
                        print('\t\t\t\t\x1b[1;31;40m{:6}  {}\x1b[0m \x1b[1;33;40m{:20}\x1b[0m\x1b[1;31;40m  '.format(entry.action,priority,entry.tnVzFilterName))
                        for efilter in entry.Filterobjectlist:
                            print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}\x1b[0m'.format('',efilter.name,efilter.etherT,efilter.protocol,efilter.sFromPort,efilter.sToPort,efilter.dFromPort,efilter.dToPort,efilter.tcpRules))

                    else: 
                        print('\t\t\t\t{}  {} \x1b[1;33;40m{:20}\x1b[0m  '.format(entry.action,priority,entry.tnVzFilterName))
                        for efilter in entry.Filterobjectlist:
                            print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('',efilter.name,efilter.etherT,efilter.protocol,efilter.sFromPort,efilter.sToPort,efilter.dFromPort,efilter.dToPort,efilter.tcpRules))#    entry.Filterobjectlist))

#getcontractinfo('SI-to-RAL_LEAK')
#contractobject = getcontractinfo('PERMIT-ALL')
#print(contractobject.name)
#print(contractobject.scope)
#for x,y in contractobject.subject.items():
#    print('subj', x)
#    for z in y:
#        print('filter', z)


#if x.priority is'default' or x.priority is 'level2':

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    clear_screen()
    #get_Cookie()
    #getallContractrelationships()
    consumerobject = sourceEPGinfo()
    providerobject = destEPGinfo()

    vzAnyResults = getvzAnyContactusage()
    #print(vzAnyResults)
    providerlist = []
    consumerlist = []
    for vzAny in vzAnyResults:
        if vzAny['vzAny'].get('children'):
            for vzRs in vzAny['vzAny']['children']:
                if vzRs.get('vzRsAnyToProv'):
                    #print(vzRs['vzRsAnyToProv'])
                    providerlist.append(vzRs['vzRsAnyToProv']['attributes']['tnVzBrCPName'])
                elif vzRs.get('vzRsAnyToCons'):
                    consumerlist.append(vzRs['vzRsAnyToCons']['attributes']['tnVzBrCPName'])
    print('\n')
    print("vzANY VRF Provider list: {}".format(providerlist))
    print("vzANY VRF Consumer list: {}".format(consumerlist))
    print('\n')
    if consumerobject.vzTaboo:
        print('{}{}'.format('Taboo in: ',consumerobject))
    if providerobject.vzTaboo:
        print('{}{}'.format('Taboo in: ',providerobject))
    if consumerobject.tenant == providerobject.tenant and consumerobject.vrf == providerobject.vrf:
        print('\n')
        print("Consumer {} consuming contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(consumerobject.epg, consumerobject.fvRsCons, consumerlist))
        print("Consumer {} providing contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(consumerobject.epg, consumerobject.fvRsProv, providerlist))
        print("Provider {} consuming contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(providerobject.epg, providerobject.fvRsCons, consumerlist))
        print("Provider {} providing contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(providerobject.epg, providerobject.fvRsProv, providerlist)) 
        consumerobject.fvRsCons += consumerlist
        consumerobject.fvRsProv += providerlist
        providerobject.fvRsCons += consumerlist
        providerobject.fvRsProv += providerlist
    else:
        print('\n')
        print("Consumer {} consuming contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(consumerobject.epg, consumerobject.fvRsCons, consumerlist))
        print("Consumer {} providing contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(consumerobject.epg, consumerobject.fvRsProv, providerlist))
        print("Provider {} consuming contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(providerobject.epg, providerobject.fvRsCons, consumerlist))
        print("Provider {} providing contracts: {} , \n\t\tvzANY VRF-Only Inherited:{}\n".format(providerobject.epg, providerobject.fvRsProv, providerlist)) 

    match = set(consumerobject.fvRsCons) & set(providerobject.fvRsProv)
    match2 = set(consumerobject.fvRsProv) & set(providerobject.fvRsCons)
    print('\n')
    print("{} {}".format("epg1 to epg2 matched contract(s): ",  list(match)))
    print("{} {}".format("epg2 to epg1 matched contract(s): ",  list(match2)))
    print('\n')
    print('='*100)
    print('\n')
    print('{:^20}{:40}{:^20}'.format('Consuming EPG','','Providing EPG'))
    print('{:20}{:40}{:20}'.format('-'*20,'','-'*20))
    print("\x1b[0;30;43m{:^20}\x1b[0m  <{:35}  \x1b[0;30;46m{:^20}\x1b[0m\n".format(consumerobject.epg,'-'*35, providerobject.epg))
    if providerobject.vzTaboo:
        print('\t\x1b[1;31;40m{} Taboo'.format(providerobject.epg))
        print('\t{}{}'.format('TABOO Contract: ', providerobject.vzTaboo['vzTaboo']['attributes']['name']))
        for subject in providerobject.vzTaboo['vzTaboo']['children']:
            if subject.get('vzTSubj'):
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','Name','Protocol','Ether-type','SFromPort','SToPort','DFromPort','DToPort','TCPRule'))
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12))

                print('\t\t[Any Direction Rules] Subject: {}'.format(subject['vzTSubj']['attributes']['name']))
                if subject['vzTSubj'].get('children'):
                    for denyrule in subject['vzTSubj']['children']:
                        if denyrule.get('vzRsDenyRule'):
                            filtertDn = denyrule['vzRsDenyRule']['attributes']['tDn']
                            filtername = denyrule['vzRsDenyRule']['attributes']['tnVzFilterName']
                            print('\t\t\t\tDeny: {}'.format(filtername))
                            filterresult = gathervzFilter()
                            entries = getfilterinfo(filtertDn, filterresult)
                            for entry in entries:
                                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('',entry.name,entry.etherT,entry.protocol,entry.sFromPort,entry.sToPort,entry.dFromPort,entry.dToPort,entry.tcpRules))
        print('\x1b[0m')
        #print('\t\t\t{}{}'.format('Subject:', providerobject.vzTaboo['vzTaboo']['attributes']['name']))
        #print(providerobject.vzTaboo['vzTaboo']['attributes']['name'])
    if consumerobject.vzTaboo:
        print('\t\x1b[1;31;40m{} Taboo'.format(consumerobject.epg))
        print('\t{}{}'.format('TABOO Contract: ', consumerobject.vzTaboo['vzTaboo']['attributes']['name']))
        for subject in consumerobject.vzTaboo['vzTaboo']['children']:
            if subject.get('vzTSubj'):
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','Name','Protocol','Ether-type','SFromPort','SToPort','DFromPort','DToPort','TCPRule'))
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12))

                print('\t\t[Any Direction Rules] Subject: {}'.format(subject['vzTSubj']['attributes']['name']))
                if subject['vzTSubj'].get('children'):
                    for denyrule in subject['vzTSubj']['children']:
                        if denyrule.get('vzRsDenyRule'):
                            filtertDn = denyrule['vzRsDenyRule']['attributes']['tDn']
                            filtername = denyrule['vzRsDenyRule']['attributes']['tnVzFilterName']
                            print('\t\t\t\tDeny: {}'.format(filtername))
                            filterresult = gathervzFilter()
                            entries = getfilterinfo(filtertDn, filterresult)
                            for entry in entries:
                                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('',entry.name,entry.etherT,entry.protocol,entry.sFromPort,entry.sToPort,entry.dFromPort,entry.dToPort,entry.tcpRules))
        print('\x1b[0m')
    gatheranddisplaycontractandfiltersbetweenepgs(match)
    print('='*100)
    print('\n')
    print('{:^20}{:40}{:^20}'.format('Consuming EPG','','Providing EPG'))
    print('{:20}{:40}{:20}'.format('-'*20,'','-'*20))
    print("\x1b[0;30;46m{:^20}\x1b[0m  <{:35}  \x1b[0;30;43m{:^20}\x1b[0m\n".format(providerobject.epg,'-'*35, consumerobject.epg))
    if providerobject.vzTaboo:
        print('\t\x1b[1;31;40m{} Taboo'.format(providerobject.epg))
        print('\t{}{}'.format('TABOO Contract: ', providerobject.vzTaboo['vzTaboo']['attributes']['name']))
        for subject in providerobject.vzTaboo['vzTaboo']['children']:
            if subject.get('vzTSubj'):
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','Name','Protocol','Ether-type','SFromPort','SToPort','DFromPort','DToPort','TCPRule'))
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12))

                print('\t\t[Any Direction Rules] Subject: {}'.format(subject['vzTSubj']['attributes']['name']))
                if subject['vzTSubj'].get('children'):
                    for denyrule in subject['vzTSubj']['children']:
                        if denyrule.get('vzRsDenyRule'):
                            filtertDn = denyrule['vzRsDenyRule']['attributes']['tDn']
                            filtername = denyrule['vzRsDenyRule']['attributes']['tnVzFilterName']
                            print('\t\t\t\tDeny: {}'.format(filtername))
                            filterresult = gathervzFilter()
                            entries = getfilterinfo(filtertDn, filterresult)
                            for entry in entries:
                                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('',entry.name,entry.etherT,entry.protocol,entry.sFromPort,entry.sToPort,entry.dFromPort,entry.dToPort,entry.tcpRules))
        print('\x1b[0m')
        #print('\t\t\t{}{}'.format('Subject:', providerobject.vzTaboo['vzTaboo']['attributes']['name']))
        #print(providerobject.vzTaboo['vzTaboo']['attributes']['name'])
    if consumerobject.vzTaboo:
        print('\t\x1b[1;31;40m{} Taboo'.format(consumerobject.epg))
        print('\t{}{}'.format('TABOO Contract: ', consumerobject.vzTaboo['vzTaboo']['attributes']['name']))
        for subject in consumerobject.vzTaboo['vzTaboo']['children']:
            if subject.get('vzTSubj'):
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','Name','Protocol','Ether-type','SFromPort','SToPort','DFromPort','DToPort','TCPRule'))
                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('','-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12,'-'*12))

                print('\t\t[Any Direction Rules] Subject: {}'.format(subject['vzTSubj']['attributes']['name']))
                if subject['vzTSubj'].get('children'):
                    for denyrule in subject['vzTSubj']['children']:
                        if denyrule.get('vzRsDenyRule'):
                            filtertDn = denyrule['vzRsDenyRule']['attributes']['tDn']
                            filtername = denyrule['vzRsDenyRule']['attributes']['tnVzFilterName']
                            print('\t\t\t\tDeny: {}'.format(filtername))
                            filterresult = gathervzFilter()
                            entries = getfilterinfo(filtertDn, filterresult)
                            for entry in entries:
                                print('{:70}{:12} {:12} {:12} {:12} {:12} {:12} {:12} {:12}'.format('',entry.name,entry.etherT,entry.protocol,entry.sFromPort,entry.sToPort,entry.dFromPort,entry.dToPort,entry.tcpRules))
        print('\x1b[0m')
    gatheranddisplaycontractandfiltersbetweenepgs(match2)
    print('='*100)
    raw_input('#Press enter to continue')








    #    if contractobject.vzSubject.vzSubjectattObjectlist:
    #        for x in contractobject.vzSubject.vzSubjectattObjectlist:
    #            if x.priority == 'level1':
    #                contractlevel1dict[x] = x.priority
    #            elif x.priority == 'default' or x.priority == 'level2':
    #                x.priority = 'level2'
    #                contractlevel2dict[x] = x.priority
    #            else:
    #                contractlevel3dict[x] = x.priority
    #    combinedlevels = [contractlevel3dict,contractlevel2dict,contractlevel1dict]
    #    for level in combinedlevels:
    #        for entry,priority in level.items():
    #            print(entry.tnVzFilterName, priority, entry.action)
    #            #print('\t\t\tFilter: ' + contractlevel3dict[entry].tDn +  ' ' + x.priority)
    #    contractlevel1dict = {}
    #    contractlevel2dict = {}
    #    contractlevel3dict = {}
    #    combinedlevels = []
    #

def iproutecheckfromleaf():
    cidrcollection = {}
    askleaf = custom_raw_input("What leaf [default=101] ") or 101
    asktenant = custom_raw_input("what tenant [default=SI] ") or 'SI'
    askvrf = custom_raw_input("What vrf [default=SI]: ") or 'SI'
    askipaddress = custom_raw_input("Compair ip address to routing table: ")
    routes= getallroutes(vrf=askvrf,leaf=askleaf,tenant=asktenant)
    ipv4addressresults, totalcount = allips()  #not used yet
    possible_route_matches = []
    for route in routes:
        if ipaddress.ip_address(unicode(askipaddress)) in ipaddress.ip_network(unicode(route.routeprefix)):
            possible_route_matches.append(route)
    if len(possible_route_matches) > 1:
        for network in possible_route_matches:
            slashlocation = network.routeprefix.find('/')
            cidr = network.routeprefix[slashlocation+1:]
            cidrcollection[cidr] = network
    elif len(possible_route_matches) == 1:
        network = possible_route_matches[0]
        slashlocation = network.routeprefix.find('/')
        cidr = network.routeprefix[slashlocation+1:]
        cidrcollection[cidr] = network
    maxcidr = max(cidrcollection)
    return cidrcollection[maxcidr], ipv4addressresults
        #stringa += "{} {} {} {} {} ".format(route, route.nexthoplist[0].nexthopaddr,route.nexthoplist[0].nexthoptype, route.nexthoplist[0].nexthopif, route.nexthoplist[0].nexthoprouteType)
        #if 'recursive' in route.nexthoplist[0].nexthoptype:
        #    stringa += allnexthopIPs(route.nexthoplist[0].nexthopaddr, ipv4addressresults) + '\n'
        #else:
        #    stringa += '\n'
    #possible_route_matches = stringa.strip().split('\n')
#possible_route_matches = iproutecheckfromleaf()
#routestring = ""
#cidrcollection = {}
#if len(possible_route_matches) > 1:
#    for network in possible_route_matches:
#        slashlocation = network.routeprefix.find('/')
#        cidr = network.routeprefix[slashlocation+1:]
#        cidrcollection[cidr] = network
#elif len(possible_route_matches) == 1:
#    network = possible_route_matches[0]
#    slashlocation = network.routeprefix.find('/')
#    cidr = network.routeprefix[slashlocation+1:]
#    cidrcollection[cidr] = network
#
#maxcidr = max(cidrcollection)
#route = cidrcollection[maxcidr]
def routelookup():
    routestring = ""
    route, ipv4addressresults = iproutecheckfromleaf()
    routestring+= "{} {} {} {} {} ".format(route, route.nexthoplist[0].nexthopaddr,route.nexthoplist[0].nexthoptype, route.nexthoplist[0].nexthopif, route.nexthoplist[0].nexthoprouteType)
    if 'recursive' in route.nexthoplist[0].nexthoptype:
        routestring += allnexthopIPs(route.nexthoplist[0].nexthopaddr, ipv4addressresults) 
    print(routestring)
#print(possible_route_matches)
#print(stringa)
        #nexthopip_lookup(route.nexthoplist[0].nexthopaddr)
    #print(route.nexthoplist[0].nexthoprouteType)
