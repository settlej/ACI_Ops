from __future__ import print_function
import json
import getpass
import time
try:
    import readline
except:
    pass
import subprocess
import os
import sys
import ipaddress
import argparse
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import localutils.program_globals 


class RestartException(Exception):
    pass

def custom_raw_input_restart(inputstr):
    r = custom_raw_input(inputstr).strip()
    if r == 'restart':
        raise RestartException
    else:
        return r




def sshlogin(user,device,command):
    cipher_re_attempt = None
    sshcommand = 'ssh {}@{} -o ConnectTimeout=3 -C {}'.format(user,device,command)
    while True:
        if cipher_re_attempt:
            sshcommand += ' -c {}'.format(cipher_re_attempt)
        try:
            output = subprocess.Popen(
                                      sshcommand,
                                      stderr = subprocess.PIPE,
                                      shell=True,
                                      universal_newlines=True)
            stdout, stderr = output.communicate()
            del stdout
            if 'no matching cipher' in stderr:
               if not cipher_re_attempt:
                    result = re.findall(r'aes\d{3}-[a-z]{3}', stderr)
                    cipher_re_attempt = result[-1]
                    continue
               else:
                    print(stderr)
                    return
            else:
                print(stderr)
                return
        except KeyboardInterrupt:
            print('\nUser killed ssh attempt...\n')
            return
        except Exception as e:
            print('Error: {}'.format(e))
            return


def create_erspan_dest(name,user,erspandestip,erspansourceip,epgdn):
    url = """https://{apic}/api/node/mo/uni/infra/destgrp-{name}.json""".format(apic=apic,name=name)
    urllist.append(('ERSPAN DESTINTATION',url))
    data = """{{"spanDestGrp":{{"attributes":{{"name":"{name}","descr":"{user} {currenttime}","status":"created"}},"children":[
              {{"spanDest":{{"attributes":{{"name":"{name}","status":"created"}},"children":[
              {{"spanRsDestEpg":{{"attributes":{{"ip":"{erspandestip}","srcIpPrefix":"{erspansourceip}","mtu":"1400",
              "tDn":"{epgdn}","status":"created,modified"}},"children":[]}}}}]}}}}]}}}}"""
    data = data.format(apic=apic,name=name,user=user,erspandestip=erspandestip,erspansourceip=erspansourceip,epgdn=epgdn,currenttime=currenttime)
    results = PostandGetResponseData(url,data,cookie)
    if results[1] == None:
        print('Successfully created ERSPAN Destination')
    else:
        print('ESPAN Destination ERROR: {}'.format(repr(results)))
    return 'uni/infra/destgrp-{name}'.format(name=name)

def create_span_sourcegroup(name,erspandestname,filterdn):
    url = """https://{apic}/api/node/mo/uni/infra/srcgrp-{name}.json""".format(apic=apic,name=name)
    urllist.append(('ERSPAN SOURCEGROUP',url))
    if filterdn != None:
        data = """{{"spanSrcGrp":{{"attributes":{{"name":"{name}","descr":"auto generated for span to oobmsw {currenttime}","adminSt":"disabled","status":"created"}},"children":[
                  {{"spanSpanLbl":{{"attributes":{{"name":"{erspandestname}","status":"created"}}}}}}]}}}}"""
    else:
        data = """{{"spanSrcGrp":{{"attributes":{{"name":"{name}","descr":"auto generated for span to oobmsw {currenttime}","adminSt":"disabled","status":"created"}},"children":[
                  {{"spanSpanLbl":{{"attributes":{{"name":"{erspandestname}","status":"created"}}}}}}]}}}}"""
    data = data.format(name=name,erspandestname=erspandestname,currenttime=currenttime,filterdn=filterdn)
    results = PostandGetResponseData(url,data,cookie)
    if results[1] == None:
        print('Successfully created ERSPAN SourceGroup')
    else:
        print('ESPAN SourceGroup ERROR: {}'.format(repr(results)))
    return 'uni/infra/srcgrp-{name}'.format(name=name)

def add_filter_to_span(name,filterdn):
    url = """https://{apic}/api/node/mo/uni/infra/srcgrp-{name}/rssrcGrpToFilterGrp.json""".format(apic=apic,name=name)
    data = """{{"spanRsSrcGrpToFilterGrp":{{"attributes":{{"tDn":"{filterdn}","status":"created"}}}}}}""".format(filterdn=filterdn)
    results = PostandGetResponseData(url,data,cookie)
    if results[1] == None:
        print('Successfully associated ERSPAN Filter to SourceGroup')
    else:
        print('ESPAN association of Filter ERROR: {}'.format(repr(results)))

def enable_span(name):
    url = """https://{apic}/api/node/mo/uni/infra/srcgrp-{name}.json""".format(apic=apic,name=name)
    data = """{"spanSrcGrp":{"attributes":{"adminSt":"enabled"},"children":[]}}"""
    results = PostandGetResponseData(url,data,cookie)
    if results[1] == None:
        print('Successfully started SourceGroup')
    else:
        print('ESPAN Start ERROR: {}'.format(repr(results)))

def gather_l3out_interfaces(apic):
    url = """https://{apic}/api/node/class/l3extRsPathL3OutAtt.json""".format(apic=apic)
    results, totalcount = GetResponseData(url,cookie, return_count=True)
    if totalcount == '0':
        print("Unable to find any l3out interfaces")
        return 0
    else:
        l3interfacelist = []
        for l3out in results:
            dn = l3out['l3extRsPathL3OutAtt']['attributes']['dn']
            addr = l3out['l3extRsPathL3OutAtt']['attributes']['addr']
            encap = l3out['l3extRsPathL3OutAtt']['attributes']['encap']
            mtu = l3out['l3extRsPathL3OutAtt']['attributes']['mtu']
            path = l3out['l3extRsPathL3OutAtt']['attributes']['tDn']
            l3outnamepath = '/'.join(dn.split('/')[:3])
            l3outnamelist = l3outnamepath[4:].replace('tn-','').replace('out-','').split('/')
            l3interfacelist.append([l3outnamepath,l3outnamelist,addr,encap,mtu,path[9:],path])
        return l3interfacelist

def create_span_sourcelocations(name,spangroupdn,interfacesources,addepgfilter=False):
    url = """https://{apic}/api/node/mo/{spangroupdn}/src-{name}.json""".format(apic=apic,name=name,spangroupdn=spangroupdn)
    urllist.append(('ERSPAN SOURCE INTERFACES',url))
    data = """{{"spanSrc":{{"attributes":{{"name":"{name}","descr":"autogenerated {currenttime}","status":"created"}},
    "children":[]}}}}""".format(name=name,currenttime=currenttime)
    interfacednlist = []
    for interfacedn in interfacesources:
        pathep = """{{"spanRsSrcToPathEp":{{"attributes":{{"tDn":"{interfacedn}","status":"created"}},"children":[]}}}}""".format(interfacedn=interfacedn)
        interfacednlist.append(json.loads(pathep))
    if addepgfilter:        
        interfacednlist.append(json.loads('{{"spanRsSrcToEpg":{{"attributes":{{"tDn":"{epgdn}","status":"created,modified"}}}}}}'.format(epgdn=addepgfilter[0])))
    data = json.loads(data)
    data['spanSrc']['children'] = interfacednlist
    data = json.dumps(data)
    results = PostandGetResponseData(url,data,cookie)
    if results[1] == None:
        print('Successfully created ERSPAN Source Interfaces')
    else:
        print('ESPAN Source Interfaces ERROR: {}'.format(repr(results)))    #"""{"spanRsSrcToPathEp":{"attributes":{"tDn":"topology/pod-1/paths-101/pathep-[eth1/3]","status":"created"},"children":[]}},


def create_l3span_sourcelocations(name,spangroupdn,l3outinterlist,addepgfilter=False):
    url = """https://{apic}/api/node/mo/{spangroupdn}/src-{name}.json""".format(apic=apic,name=name,spangroupdn=spangroupdn)
    urllist.append(('ERSPAN L3 SOURCE INTERFACES',url))
    data = """{{"spanSrc":{{"attributes":{{"name":"{name}","dir":"{direction}","descr":"autogenerated {currenttime}","status":"created"}},
    "children":[]}}}}""".format(name=name,currenttime=currenttime,direction=l3outinterlist[0][-1])
    interfacednlist = []
    for interfacedn in l3outinterlist:
        pathep = """{{"spanRsSrcToPathEp":{{"attributes":{{"tDn":"{interfacedn}","status":"created"}},"children":[]}}}}""".format(interfacedn=interfacedn[-2])
        interfacednlist.append(json.loads(pathep))
    l3pathep = """{{"spanRsSrcToL3extOut":{{"attributes":{{"tDn":"{l3name}","encap":"{vlan}","status":"created"}}}}}}""".format(l3name=l3outinterlist[0][0],vlan=l3outinterlist[0][3])
    interfacednlist.append(json.loads(l3pathep))
    if addepgfilter:        
        interfacednlist.append(json.loads('{{"spanRsSrcToEpg":{{"attributes":{{"tDn":"{epgdn}","status":"created,modified"}}}}}}'.format(epgdn=addepgfilter[0])))
    data = json.loads(data)
    data['spanSrc']['children'] = interfacednlist
    data = json.dumps(data)
    results = PostandGetResponseData(url,data,cookie)
    if results[1] == None:
        print('Successfully created ERSPAN Source Interfaces')
    else:
        print('ESPAN Source Interfaces ERROR: {}'.format(repr(results)))    

def create_filter_acl(filtername,user,srcip,dstip,protocol,srcports,destports):
    url = "https://{apic}/api/node/mo/uni/infra/filtergrp-{filtername}.json".format(apic=apic,filtername=filtername)
    urllist.append(('ERSPAN FILTER',url))
    aclentries = """[{{"spanFilterEntry":{{"attributes":{{"srcAddr":"{sip}","dstAddr":"{dip}","status":"created"}}}}}},
                     {{"spanFilterEntry":{{"attributes":{{"srcAddr":"{dip}","dstAddr":"{sip}","status":"created"}}}}}}]"""
    if srcip == 'unspecified':
        srcip = '0.0.0.0'
    if dstip == 'unspecified':
        dstip = '0.0.0.0'
    aclentries = aclentries.format(sip=srcip,dip=dstip)
    aclentries = json.loads(aclentries)
    if protocol:
        entry = {}
        entry["ipProto"] = protocol
        aclentries[0]['spanFilterEntry']['attributes'].update(entry)
        aclentries[1]['spanFilterEntry']['attributes'].update(entry)

    entry = {}
    entry['dstPortFrom'] = str(destports[0])
    entry['dstPortTo'] = str(destports[1])
    entry['srcPortFrom'] = str(srcports[0])
    entry['srcPortTo'] = str(srcports[1])
    aclentries[0]['spanFilterEntry']['attributes'].update(entry)
    entry = {}
    entry['dstPortFrom'] = str(srcports[0])
    entry['dstPortTo'] = str(srcports[1])
    entry['srcPortFrom'] = str(destports[0])
    entry['srcPortTo'] = str(destports[1])
    aclentries[1]['spanFilterEntry']['attributes'].update(entry)
    data = """{{"spanFilterGrp":{{"attributes":{{"name":"{filter}","descr":"{user}","status":"created"}},"children":[]}}}}""".format(filter=filtername,user=user)
    data = json.loads(data)
    data['spanFilterGrp']['children'] = aclentries
    data = json.dumps(data)
    results = PostandGetResponseData(url,data,cookie)
    if results[1] == None:
        print('Successfully created ERSPAN Filter')
    else:
        print('ESPAN Filter ERROR: {}'.format(repr(results)))
    return 'uni/infra/filtergrp-{filtername}'.format(filtername=filtername)
    

def monitor_interface_menu():
    while True:
        print("\nSelect type of interface(s) to monitor: \n\n" + \
          "\t1.) Physical Interfaces \n" + \
          "\t2.) PC Interfaces \n" + \
          "\t3.) VPC Interfaces \n")
        selection = custom_raw_input_restart("Select number: ")
        print('\r')
        if selection.isdigit() and selection != '' and 1 <= int(selection) <= 3:
            break
        else:
            continue
    return selection 

class SpanSession():
    def __init__(self, info):
        self.__dict__.update(**info)
        self.destination = []
        self.sourcedictlist = [] 
        
        self.faultsdict = {}
    def __setitem__(self, k,v):
        setattr(self, k, v)
    def __getitem__(self, k):
        try:
            return getattr(self, k)
        except:
            return None
    def add_source(self, source):
        sourcedict = dict()
        for att, val in source['attributes'].items():
            if att == 'dir':
                sourcedict.update({att:val})
            elif att == 'mode':
                sourcedict.update({att:val})
            elif att == 'type':
                sourcedict.update({att:val})
        if source.get('children'):
            for child in source['children']:
                if child.get('spanRsSpanSrcToL1IfAtt'):
                    for inter in child['spanRsSpanSrcToL1IfAtt']:
                        if inter == 'attributes':
                            #sourcedict['sourcelist'].append(
                            #    {"interfacefull": child['spanRsSpanSrcToL1IfAtt']['attributes']['tDn'],
                            #    "status": child['spanRsSpanSrcToL1IfAtt']['attributes']['operSt'],
                            #    "interfaceshort": child['spanRsSpanSrcToL1IfAtt']['attributes']['tSKey']}
                            #    )
                            node = re.search(r"node-\d+",child['spanRsSpanSrcToL1IfAtt']['attributes']['tDn'])
                            custom_name = '{node}:{inter}'.format(node=node.group(0),inter=child['spanRsSpanSrcToL1IfAtt']['attributes']['tSKey'])
                            self['sourcedictlist'].append({'name':custom_name,'status':child['spanRsSpanSrcToL1IfAtt']['attributes']['operSt'],'faultamount': 0})
                        if inter == 'children':
                        #import pdb; pdb.set_trace()
                        #self[custom_name] = {'status':child['spanRsSpanSrcToL1IfAtt']['attributes']['operSt'],'faultamount':0}
                            for subchild in child['spanRsSpanSrcToL1IfAtt']['children']:
                                self['sourcedictlist'][-1]['faultamount'] += 1
                                if not self['sourcedictlist'][-1].get('faultlist'):
                                    self['sourcedictlist'][-1].update({'faultlist':[]})
                                self['sourcedictlist'][-1]['faultlist'].append({'faultcode':subchild['faultInst']['attributes']["code"], 'faultdescr': subchild['faultInst']['attributes']["descr"]})
                            #self.faultsdictlist['subchild['attributes']['tDn']]
                            #self.faultslist.append(subchild['attributes'])
    def add_dest(self, dests):
        destdict = dict()
        for att, val in dests['attributes'].items():
            if att == 'dir':
                destdict.update({att:val})
            elif att == 'mode':
                destdict.update({att:val})
            elif att == 'type':
                destdict.update({att:val})
        for dest in dests:
            if dest == 'attributes':
                #destdict['destlist'].append(
                #    {"interfacefull": child['spanLDestination']['attributes']['tDn'],
                #    "status": child['spanLDestination']['attributes']['operSt'],
                #    "interfaceshort": child['spanLDestination']['attributes']['tSKey']}
                #    )
                custom_name = dests['attributes']['port']
                self['destination'].append({'name':custom_name,'status':dests['attributes']['operSt'],'faultamount': 0})
            if dest == 'children':
            #import pdb; pdb.set_trace()
            #self[custom_name] = {'status':dests['attributes']['operSt'],'faultamount':0}
                for subchild in dests['children']:
                    self['destination'][-1]['faultamount'] += 1
                    if not self['destination'][-1].get('faultlist'):
                        self['destination'][-1].update({'faultlist':[]})
                    self['destination'][-1]['faultlist'].append({'faultcode':subchild['faultInst']['attributes']["code"], 'faultdescr': subchild['faultInst']['attributes']["descr"]})
                #self.faultsdictlist['subchild['attributes']['tDn']]
                            #self.faultslist.append(subchild['attributes'])
    def add_erspandest(self, erspandests):
        erspandestdict = dict()
        for att, val in erspandests['attributes'].items():
            if att == 'dir':
                erspandestdict.update({att:val})
            elif att == 'mode':
                erspandestdict.update({att:val})
            elif att == 'type':
                erspandestdict.update({att:val})
        for erspandest in erspandests:
            if erspandest == 'attributes':
                #erspandestdict['erspandestlist'].append(
                #    {"interfacefull": child['spanLerspandestination']['attributes']['tDn'],
                #    "status": child['spanLerspandestination']['attributes']['operSt'],
                #    "interfaceshort": child['spanLerspandestination']['attributes']['tSKey']}
                #    )
                custom_name = erspandests['attributes']['name']
                self['destination'].append({'name':custom_name,'status':erspandests['attributes']['operSt'],'dstIp':erspandests['attributes']['dstIp'],'faultamount': 0})
            if erspandest == 'children':
            #import pdb; pdb.set_trace()
            #self[custom_name] = {'status':erspandests['attributes']['operSt'],'faultamount':0}
                for subchild in erspandests['children']:
                    self['destination'][-1]['faultamount'] += 1
                    if not self['destination'][-1].get('faultlist'):
                        self['destination'][-1].update({'faultlist':[]})
                    self['destination'][-1]['faultlist'].append({'faultcode':subchild['faultInst']['attributes']["code"], 'faultdescr': subchild['faultInst']['attributes']["descr"]})
        

def display_current_span_sessions():
    result, count = GetResponseData('https://{apic}/api/node/class/spanSession.json?rsp-subtree=full&rsp-subtree-include=faults'.format(apic=apic),cookie=cookie,return_count=True)
    if int(count) == 0:
        print("\nNo Running Span Sessions")
    else:
        print('')
        spanlist = []
        for sess in result:
            currentsession = SpanSession(sess['spanSession']['attributes'])
            if sess['spanSession'].get('children'):
                for child in sess['spanSession']['children']:
    
                    if child.get('spanSource'):
                        currentsession.add_source(child['spanSource'])
                    if child.get('spanLDestination'):
                        currentsession.add_dest(child['spanLDestination'])
                    if child.get('spanERDestination'):
                        currentsession.add_erspandest(child['spanERDestination'])
            spanlist.append(currentsession)
        for span in sorted(spanlist):
            print(span['ASrcGrpDn'])
            print(span['adminSt'])
            print('SOURCES:')
            for x in span['sourcedictlist']:
               print('  interface {}'.format(x['name']))
               print('  status: {}'.format(x['status']))
               print('  total faults: {}'.format(x['faultamount']))
            print('DESTINATION')
            for y in span.destination:
               print('  interface {}'.format(y['name']))
               print('  status: {}'.format(y['status']))
               print('  total faults: {}'.format(y['faultamount']))
               if y.get('dstIp'):
                   print(y['dstIp'])
            print('-' * 40)
                   # if child.get('spanLDestination')
                   #import pdb; pdb.set_trace()
                #for epg in bd['fvBD']['children']:
                #    bdobj.add_epg(fvEPG(epg['fvRtBd']['attributes']['tDn']))
                    
                




def main(user=None,prestaged=False,erspandestip = None,relay = False):
    global cookie
    global apic
    global currenttime
    global urllist
    urllist = []
    l3locations = []
    l3outinterlist = []
    currenttime = localutils.program_globals.TIME
    cookie = localutils.program_globals.TOKEN
    if user == None:
        user = os.getenv['USER']
    apic = localutils.program_globals.APIC
    refreshToken(apic,cookie)
    while True:
        try:
            clear_screen()
            location_banner('ERSPAN Setup')
            switchip = '10.200.200.213'
            permanent = False
            if not prestaged:
                duration = None
                vpc = None
                location  = None
                destip = None
                srcip = None
                protocol = 'unspecified'
                ports = 'unspecified'
                while True:
                    askpermanent =  custom_raw_input_restart("\n 1.) Temporary ERSPAN\n"
                                                     + " 2.) Permanent ERSPAN\n"
                                                     + " 3.) View Span Sessions \n\nSelection [1]: ") or '1'
                    if askpermanent == '1':
                        permanent = False
                        break
                    elif askpermanent == '2':
                        permanent = True
                        break
                    elif askpermanent == '3':
                        display_current_span_sessions()
                        raw_input('\nContinue...')
                        clear_screen()
                        location_banner('ERSPAN Setup')
                        continue
                    else:
                        print('Invalid number')
                        continue
        
            print('')
            if not erspandestip:
                while True:
                    erspandestip = custom_raw_input_restart("Desination IP for ERSPAN traffic?: ")
                    try: 
                        ipaddress.IPv4Address(unicode(erspandestip))
                        break
                    except:
                        print('Invalid Ip address')
                        continue
            if relay == True:
                while True:
                    computerip = custom_raw_input_restart("What is Capture workstation IP for relayed ERSPAN traffic?: ")
                    try: 
                        ipaddress.IPv4Address(unicode(computerip))
                        break
                    except:
                        print('Invalid Ip address')
                        continue
            if not duration and permanent == False:
                while True:
                    duration = custom_raw_input_restart('How long to run datacenter ERSPAN? [10-500 sec]: ')
                    if not duration.isdigit():
                        print('Invalid number')
                        continue
                    if int(duration) > 500:
                        print('500 seconds is the limit')
                        continue
                    break
            external = False
            while True:
                askext = custom_raw_input_restart("Include L3out interfaces? [y]:  ") or 'y'
                if askext.lower()[0] == 'n':
                    break
                if askext.lower()[0] == 'y':
                    external = True
                    break
                else:
                    continue
            skipfilter = False
            if not srcip and not destip and ports == 'unspecified':
                while True:
                    createfilter = custom_raw_input_restart("Create Filter ACL for capturing?: ") or 'y'
                    if createfilter != "" and createfilter[0].lower() == 'n':
                        skipfilter = True
                        break
                    elif createfilter != "" and createfilter[0].lower() == 'y':
                        while True:
                            srcip = custom_raw_input_restart("What Source ip to monitor?: ")
                            try: 
                                if srcip == 'any' or srcip == '0.0.0.0':
                                    srcip = 'unspecified'
                                    break
                                ipaddress.IPv4Address(unicode(srcip))
                                break
                            except:
                                print('Invalid Ip address')
                                continue
                        while True:
                            destip = custom_raw_input_restart("What destination ip to monitor?: ")
                            try: 
                                if destip == 'any' or destip == '0.0.0.0':
                                    destip = 'unspecified'
                                    break
                                ipaddress.IPv4Address(unicode(destip))
                                break
                            except:
                                print('Invalid Ip address')
                                continue
                        while True:
                            protocol = custom_raw_input_restart("What IP Protocol? (Example: ospf,pim,icmp,tcp,udp,any) [default=any]: ") or 'any'
                            if protocol != "":
                                if protocol == 'any':
                                    protocol = 'unspecified'
                                    break
                            if protocol.strip() in ['ip', 'tcp', 'udp']:
                                if protocol == 'ip':
                                    protocol = 'unspecified'
                                while True:
                                    ports = custom_raw_input_restart("What port or port range? (Example: 80 or 80-90 or any) [default=any]: ") or 'any'
                                    if ports != "":
                                        if ports == 'any':
                                            ports = 'unspecified'
                                            break
                                    if '-' in ports:
                                        ports = ports.split('-')
                                        if not ports[0].isdigit() or not ports[1].isdigit():
                                            print('Invalid port numbers')
                                            continue
                                        if int(ports[0]) > int(ports[1]):
                                            print('Invalid port range')
                                            continue
                                        break
                                    else:
                                        ports = [ports,ports]
                                        break
                            else:
                                ports = 'unspecified'
                                break
                            break
                    else:
                        continue
                    break
            locationlist = []
            templocationlist = []
            if not location and not vpc:
                if srcip and destip:
                    print('\nSearching for source and destination interfaces...\n')
                    for ip in [srcip,destip]:
                        if ip != 'unspecified':
                            url = """https://{apic}/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvRsCEpToPathEp&rsp-subtree-include=required&query-target-filter=eq(fvCEp.ip,"{ip}")""".format(apic=apic,ip=ip)
                            results, totalcount = GetResponseData(url,cookie,return_count=True)
                            if int(totalcount) == 1:
                               templocationlist.extend([path['fvRsCEpToPathEp']['attributes']['tDn'] for path in results[0]['fvCEp']['children']])
                            elif int(totalcount) > 1:
                                for endpoint in results:
                                    templocationlist.extend([path['fvRsCEpToPathEp']['attributes']['tDn'] for path in results['fvCEp']['children']])
                            elif totalcount == '0':
                                print('Unable to dynamically locate source interface for Endpoint using {}'.format(ip))
                    if len(templocationlist) > 0:
                        templocationlist = list(set(templocationlist))
                        print("Found interfaces associated to IPs provided:\n")
                        for num,path in enumerate(templocationlist,1):
                            print('   {}.) {}'.format(num,path))
                        while True:
                            if len(templocationlist) == 1:
                                search = custom_raw_input_restart("\nWould you like to monitor found interface? [default=yes]: ") or 'all'
                                if search[0].lower() == 'n':
                                    break
                                elif search[0].lower() == 'y':
                                    location = templocationlist
                                    break
                            else:
                                search = custom_raw_input_restart("\nWhich interfaces would you like to monitor? [default=all]: ") or 'all'
                            if search[0].lower() == 'n':
                                break
                            elif search == 'all':
                                location = templocationlist
                                locationlist = templocationlist
                                break
                            try:
                                menunumbers = parseandreturnsingelist(search)
                                locationlist = [templocationlist[loc - 1] for loc in menunumbers]
                                break
                            except:
                                print('Invalid options, try again...')
                                continue
                    else:
                        print("\nUnable to locate any interface from IPs provide")
                additional = None
                if external:
                    print('\nL3 Menu:\n')
                    l3outinterlist = gather_l3out_interfaces(apic)
                    headers = ['Tenant','L3out']
                    columns = [(x[1][0],x[1][1]) for x in l3outinterlist]
                    sizes = get_column_sizes(rowlist=columns,baseminimum=headers)
                    print('     {:{s1}} | {:{s2}}'.format('Tenant','L3out',s1=sizes[0],s2=sizes[1]))
                    print('     ' + '-' * sizes[0] + '---' + '-' * sizes[1])
                    for num,x in enumerate(l3outinterlist,1):
                        print(' {}.) {:{s1}} | {:{s2}}'.format(num,x[1][0],x[1][1],s1=sizes[0],s2=sizes[1]))
                    print('')
                    while True:
                        selections = custom_raw_input_restart('L3 Selection or none: ')
                        if (not '-' in selections and not ',' in selections) and not selections.isdigit():
                            print('Invalid selection')
                            continue
                        if selections.lower() == 'none':
                            l3location = []
                            l3outinterlist = []
                            break
                        else:
                            menunumbers = parseandreturnsingelist(selections)
                            try:
                                l3locations.extend([l3outinterlist[num -1] for num in menunumbers])
        
                            except IndexError:
                                print('Invalid selection')
                                continue
                            if len(menunumbers) > 1:
                                print('Only one selection is supported')
                                continue
                        print('')
                        while True:
                            direc = custom_raw_input_restart('L3OUT capture direction? [both,in,out] [[both]]: ') or 'both'
                            if direc in ['both','in','out']:
                                [x.append(direc) for x in l3locations]
                                break
                            else:
                                continue
                        break
        
                if locationlist != [] or l3locations != []:
                    while True:
                        ask = custom_raw_input_restart("\nWould you like to add interfaces manually? [n]: ") or 'no'
                        if ask[0].lower() == 'y':
                            additional = True
                            break
                        if ask[0].lower() == 'n':
                            break
                if (locationlist == [] and l3outinterlist == []) or additional:
                    allepglist = get_All_EGPs_names(apic,cookie)
                    allpclist = get_All_PCs(apic,cookie)
                    allvpclist = get_All_vPCs(apic,cookie)
                    all_leaflist = get_All_leafs(apic,cookie)
                    additional = True
                    while additional == True:
                        selection = monitor_interface_menu()
                        if selection == '1':
                            chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
                            switchpreviewutil.main(apic,cookie,chosenleafs)
                            returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
                            locationlist.extend(returnedlist)
                            print('\r')
                        elif selection == '2':
                            returnedlist = port_channel_selection(allpclist)
                            locationlist.extend(returnedlist)
                            print('\r')
                        elif selection == '3':
                            returnedlist = port_channel_selection(allvpclist)
                            locationlist.extend(returnedlist)
                            print('\r')
                        while True:
                            addmore = custom_raw_input_restart("Add any more Interfaces,PCs,VPCs? [n]: ") or 'n'
                            if addmore[0].lower() == 'n':
                                additional = False
                                break
                            elif addmore[0].lower() == 'y':
                                break
            if locationlist == []:
                if location == None and vpc != None:
                    if ';' in vpc:
                        locationlist = vpc.split(';')
                    else:
                        locationlist = [vpc]
                elif location == None and vpc == None and l3outinterlist == []:
                    custom_raw_input_restart('ERROR: Source interface is required, exiting...')
                    raise KeyboardInterrupt
                else:
                    locationlist = location
        
            if ports == 'unspecified':
                srcports = ['unspecified','unspecified']
                destports = ['unspecified','unspecified']
            elif type(ports) is list:
                srcports = ['unspecified','unspecified']
                destports = ports
            else: 
                destports = ports.split(':')
                srcports= ['unspecified','unspecified']
            #erspandestname = 'ERSPAN_DEST'
            erspandestname = 'ERSPAN_DESTINATION_{}'.format(erspandestip.replace('.',""))
            chosenepgs = []
            while True:
                filterepg = custom_raw_input_restart("Capture speceific EPG traffic on source interface(s)? [y|default=n]: ") or 'no'
                if filterepg[0].lower() == 'n':
                    epgfilter = False
                    break
                elif filterepg[0].lower() == 'y':
                    allepglist = get_All_EGPs_names(apic,cookie)
                    while True:
                       chosenepgs, _ = display_and_select_epgs(None, allepglist)
                       if len(chosenepgs) > 1:
                           print("Only one EPG supported, try again...\n")
                           continue
                       epgfilter = chosenepgs
                       break
                    break
            print('')
            print('*' * 25)
            print("Summary:")
            if skipfilter == False:
                print(" ACL Procotol {protocol}\n ACL Ports: {ports}".format(protocol=protocol,ports=ports))
                print(" ACL IP source: {srcip}\n ACL IP dest: {destip}".format(srcip=srcip,destip=destip))
            else:
                print(" ACL filter: None")
            print(" Duration: {duration} sec".format(duration=duration))
            print(" ERSPAN Destination: " + str(erspandestip))
            if chosenepgs:
                print(" EPG filtered: {}".format(chosenepgs[0]))
            if locationlist:
                for loc in locationlist:
                   print(' Source interface: ' + str(loc))
            if l3outinterlist:
                for l3 in l3outinterlist:
                    print(' L3out interface: ' + str(l3[-2]))
            print('*' * 25)
            while True:
                create = custom_raw_input_restart('\nCreate ERSPAN? [y|n]:')
                if create.strip() != "" and create.strip()[0].lower() == 'n':
                    custom_raw_input_restart('\nCanceled!')
                    raise RestartException
                elif create.strip() != "" and create.strip()[0].lower() == 'y':
                    break
            try:
                if skipfilter == True:
                    filterdn = None
                else:
                    filterdn = create_filter_acl('ERSPAN_Filter_{}_{}'.format(user,currenttime),user,srcip,destip,protocol,srcports,destports)
                erspanddestdn  = create_erspan_dest(erspandestname,user,erspandestip,erspansourceip='2.2.2.2',epgdn='uni/tn-HQ/ap-APP-HQ/epg-EPG-VL7-NET-MGMT')
                spangroupdn = create_span_sourcegroup('ERSPAN_SOURCEGROUP_{}_{}'.format(user,currenttime),erspandestname,filterdn)
                if locationlist:
                    create_span_sourcelocations('SPAN_Interfaces',spangroupdn,locationlist,epgfilter)
                if l3outinterlist:
                    create_l3span_sourcelocations('L3Out_Interfaces',spangroupdn,l3outinterlist)
                if skipfilter == False:
                    add_filter_to_span('ERSPAN_SOURCEGROUP_{}_{}'.format(user,currenttime),filterdn)
                enable_span('ERSPAN_SOURCEGROUP_{}_{}'.format(user,currenttime))
                print('\n')
                if duration:
                    duration = int(duration)
                if __name__ == '__main__':
                    command = 'wireshark erspan ip 2.2.2.2 any {computerip} Gi1/1/1 214.26.x.x {duration} rx silent'.format(duration=str(duration),computerip=computerip)
                    print('Logging into OOBM Switch (214.26.x.x) to relay traffic to computer\n')
                    print('ssh {}@214.26.x.x to start erspan relay'.format(user))
                    sshlogin(user,'214.26.x.x',command)
                else:
                    if permanent == False:
                        print('ERSPAN will run for {duration} seconds'.format(duration=duration))
                        print('\n')
                        for i in range(duration +1):
                            incre = int(50.0 / duration * i)
                            if i != duration:
                                print('|{}{}| {}%{}'.format('='*incre, ' '*(51-incre), 2*incre,'\b'*200),end="") 
                            else:
                                print('|{}{}{}| {}%'.format('='*20, 'COMPLETE!', '='*22, 100))
                            time.sleep(1)
            except KeyboardInterrupt:
                print('\n\nCancelling and will delete ERSPAN')
            except:
                print('\n\nERROR has occurred! Removing ERSPAN')
            finally:
                failurenum = 0
                failurelist = []
                if permanent == False:
                    for url in urllist:
                        result = DeleteandGetResponseData(url[1],cookie)
                        if result[1] != None:
                            failurenum += 1
                            failurelist.append('Failure: Unable to delete {} object'.format(url[0]))
                    if failurenum == 0:
                        print('\nSuccessfully removed ERSPAN from ACI')
                else:
                    print('\nERSPAN will remain operation until admin disables via GUI or API')
                custom_raw_input_restart('\nContinue...')
        except RestartException:
            continue
        else:
            break
        finally:
            refreshToken(apic,cookie)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol', type=str, nargs='?', help='protocol type')
    parser.add_argument('-s','--srcip', type=str, nargs='?',  help='source ip to filter')
    parser.add_argument('-d','--destip', type=str, nargs='?',  help='destination ip to filter')
    parser.add_argument('-p','--ports', type=str, nargs='?', help='protcol port numbers 80:85 means 80 upto 85')
    parser.add_argument('-t','--duration', type=str, nargs='?',  help='time limit for span')
    parser.add_argument('-l','--location', type=str, nargs='?',  help='leafxxx:ethx/x')
    parser.add_argument('--vpc', type=str, nargs='?',  help='vpcname to listen')
    parser.add_argument('--erspandest', type=str, nargs='?',  help='erspan destination ip')
    args = parser.parse_args()
    duration = args.duration
    vpc = args.vpc
    location = args.location
    destip = args.destip
    srcip = args.srcip
    protocol = args.protocol
    ports = args.ports
    erspandestip = args.erspandestip
    USER = os.environ['USER']
    main(user=USER,prestaged=True)



    #print(filter)
   # a = subprocess.Popen(r'ssh -T {user}@{switchip} -C "wireshark erspan ip any any {erspandest} Vlan1000 2.2.2.2 {duration} rx silent'.format(user=user,switchip=switchip,erspandest=erspandest,duration=duration), stderr=subprocess.PIPE,shell=True)
   # while True:
   #     s, b = a.communicate(input='show version')
   #     if b != "None":
   #         print(b)
   #     break
