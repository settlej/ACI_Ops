#!/bin//python

from __future__ import print_function 
import re
try:
    import readline
except:
    pass
import urllib2
import json
import datetime
import itertools
#import trace
#import pdb
#import random
import threading
import Queue
from collections import namedtuple, OrderedDict
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import localutils.program_globals 
from localutils.base_classes import *
import logging
from operator import itemgetter
#from collections import Counter
#from multiprocessing.dummy import Pool as ThreadPool


# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)


class ruleclass():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return "rule|{id}|{action}|{dPcTag}".format(id=self.id,action=self.action,dPcTag=self.dPcTag)

class epgclass():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return "epg|{pcTag}|{epgname}".format(pcTag=self.pcTag,epgname=self.name)

class l3outclass():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return "l3out:{name}".format(pcTag=self.pcTag,name=self.name)

class vrfclass():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return "vrf:{name}".format(pcTag=self.pcTag,name=self.name)

class bdclass():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return "bd|{name}".format(pcTag=self.pcTag,name=self.name)


def gather_vrf_sclass(tenant=None):
    if tenant:
        url = """https://{apic}/api/node/mo/uni/tn-SI.json?query-target=children&target-subtree-class=fvCtx"""
        pass
    else:
        url = """https://{apic}/api/node/class/fvCtx.json""".format(apic=apic)
    results = GetResponseData(url,cookie)
    return results

def gather_bd_sclass(tenant=None):
    if tenant:
        pass
    else:
        url = """https://{apic}/api/node/class/fvBD.json""".format(apic=apic)
    results = GetResponseData(url,cookie)
    return results

def create_epgnum_to_epgname_dict(epgapiresults):
    epgdict = {}
    for epg in epgapiresults:
        #import pdb; pdb.set_trace()
        if epg.get('fvAEPg'):
            epgobj = epgclass(epg['fvAEPg']['attributes'])
            epgdict[str(epgobj.pcTag)] = epgobj
        elif epg.get('l3extInstP'):
            epgobj = l3outclass(epg['l3extInstP']['attributes'])
            epgdict[str(epgobj.pcTag)] = epgobj
        elif epg.get('fvCtx'):
            epgobj = vrfclass(epg['fvCtx']['attributes'])
            epgdict[str(epgobj.pcTag)] = epgobj
        elif epg.get('fvBD'):
            epgobj = bdclass(epg['fvBD']['attributes'])
            epgdict[str(epgobj.pcTag)] = epgobj
    return epgdict

def gather_per_leaf_zonerules(leaf,pod='1'):
    url = """https://{apic}/api/node/class/topology/pod-{pod}/node-{leaf}/actrlRule.json?rsp-subtree-include=stats&rsp-subtree-class=actrlRuleHit5min""".format(apic=apic,leaf=leaf,pod=pod)
    results = GetResponseData(url,cookie)
    rulelist = []
    for rule in results:
        ruleobj = ruleclass(rule['actrlRule']['attributes'])
        if rule['actrlRule'].get('children'):
            ruleobj.hitcum = int(rule['actrlRule']['children'][0]['actrlRuleHit5min']['attributes']['pktsCum'])
            ruleobj.pktsLast = int(rule['actrlRule']['children'][0]['actrlRuleHit5min']['attributes']['pktsLast'])
            ruleobj.hitcum += ruleobj.pktsLast
            ruleobj.rate = rule['actrlRule']['children'][0]['actrlRuleHit5min']['attributes']['pktsRate']
        rulelist.append(ruleobj)
    return rulelist

def gather_l3out_epgs(tenant=None):
    if tenant:
        url = """https://{apic}/api/node/mo/uni/tn-SI/out-L3-OUT.json?query-target=children&target-subtree-class""".format(apic=apic) + \
              """=l3extInstP&query-target-filter=not(wcard(l3extInstP.dn,"^.*/instP-__int_.*"))&order-by=l3extInstP.name"""
    else:
        url = """https://{apic}/api/node/class/l3extInstP.json?order-by=l3extInstP.name""".format(apic=apic)
    results = GetResponseData(url,cookie)
    #l3outlist = []
    #for l3out in results:
    #    l3outobj = l3outclass(l3out['l3extInstP']['attributes'])
    #    l3outlist.append(l3outobj)
    return results
    

def gather_epg_numbers_to_names(vrf=None,leaf=None):
    url = """https://{apic}/api/node/mo/topology/pod-{pod}/node-{leaf}.json?order-by=actrlRule.fltId""".format(apic=apic,leaf=leaf,pod=pod)

def options_menu():
    print('\n')
    print('Options:\n\n' 
        + '\t1.) Show rules per leaf\n'
        + '\t2.) Rules to 1 EPG\n'
        + '\t3.) Rules from 1 EPG\n'
        + '\t4.) Rules for VRF\n'
        + '\t5.) Rules between 2 EPGs\n'
        + '\t6.) Show rules entire POD\n'
        + '\t7.) Show Hit rules only per leaf\n\n')
    while True:
        ask = custom_raw_input('Selection [select number]: ')
        if ask != '' and ask.isdigit() and int(ask) > 0 and int(ask) <= 6:
            return ask
        
    
rulepriority = {'class-eq-filter': '1',
                'class-eq-deny': '2',
                'class-eq-allow': '3',
                'prov-nonshared-to-cons': '4',
                'black_list': '5',
                'fabric_infra': '6',
                'fully_qual': '7',
                'system_incomplete': '8',
                'src_dst_any': '9',
                'shsrc_any_filt_perm': '10',
                'shsrc_any_any_perm': '11',
                'shsrc_any_any_deny': '12',
                'src_any_filter': '13',
                'any_dest_filter': '14',
                'src_any_any': '15',
                'any_dest_any': '16',
                'any_any_filter': '17',
                'grp_src_any_any_deny': '18',
                'grp_any_dest_any_deny': '19',
                'grp_any_any_any_permit': '20',
                'any_any_any': '21',
                'any_vrf_any_deny': '22',
                'default_action': '23'}

class Aclfilter():
    ENTRY_PRIORITY = {'flags':1,
                      'sport_dport':2,
                      'dport':3,
                      'sport':4,
                      'proto':5,
                      'frag':6,
                      'def':7,
                      'implicit':8}
    def __init__(self,rule):
        self.name = rule['name']
        self.parse_categorize_fields(rule)
    def __setitem__(self, k,v):
        setattr(self, k, v)
    def parse_categorize_fields(self,rule):
        for category in rule:
            self[category] = rule[category]
            if category == 'prio':
                self['entry_priority'] = self.ENTRY_PRIORITY[rule[category]]
            if category == 'dn':
                try:
                    filtersearch = re.search(r'filt-(\d+)|filt-([\w|\d]+)',rule[category])
                    if filtersearch.group(1):
                        self['filterid'] = filtersearch.group(1)
                    else:
                        self['filterid'] = filtersearch.group(2)
                except:
                    self['filterid'] = 'Unknown'
        
        

def gather_aclfilters_entries(leaf):
            url = "https://{apic}/api/node/class/topology/pod-{pod}/node-{node}/actrlEntry.json".format(apic=apic,pod=1,node=leaf)
            #url = """https://{apic}/api/node/class/vzFilter.json?rsp-subtree=children&rsp-subtree-class=vzEntry""".format(apic=apic)
            results = GetResponseData(url, cookie)
            acldict = {}
            for acl in results:
                a = Aclfilter(acl['actrlEntry']['attributes'])
                if acldict.get(a.filterid):
                    acldict[a.filterid].append(a)
                else:
                    acldict[a.filterid] = [a]

            return acldict
            #aclre_compile = re.compile(r"filt-(.*)\/ent-(.*)")


            #for acl in results:
            #    if len(acl['actrlEntry']['attributes']['name'].split('_')) == 1:
            #        acldict[acl['actrlEntry']['attributes']['name']] = acl['actrlEntry']['attributes']
            #    else:
            #        if acldict.get(acl['actrlEntry']['attributes']['name'].split('_')[0]):
            #            acldict[acl['actrlEntry']['attributes']['name'].split('_')[0]].append(acl['actrlEntry']['attributes'])
            #        else:
            #            acldict[acl['actrlEntry']['attributes']['name'].split('_')[0]] = acl['actrlEntry']['attributes']
            #import pdb; pdb.set_trace()
            #    
            ##    aclre_compile.search(acl['actrlEntry']['attributes']['name'])
            ##    acldict[]
            #mmm = grab_lowest_MO_keyvalues(results, primaryKey='dn', keys=['name','etherT','prot','icmpv4T','icmpv6T','dFromPort','dToPort','sFromPort','sToPort','tcpRules','applyToFrag'])
            ##mmm = grab_lowest_MO_keyvalues2(results, parentclass='vzFilter',parentid='dn', parent_keys=['uid','name','fwdId','revId'], childclass='vzEntry', childid='name',child_keys=['name','etherT','prot','icmpv4T','icmpv6T','dFromPort','dToPort','sFromPort','sToPort','tcpRules','applyToFrag'])
            #import pdb; pdb.set_trace()
            #for k in mmm.values():
            #    print(k.dn, k.fwdId, k.children)



def main():
        global cookie
        global apic
        cookie = localutils.program_globals.TOKEN
        apic = localutils.program_globals.APIC
        allepglist = get_All_EGPs_data(apic,cookie)
        #allpclist = get_All_PCs(apic,cookie)
        #allvpclist = get_All_vPCs(apic,cookie)
        all_leaflist = get_All_leafs(apic,cookie)
        clear_screen()
        location_banner('Zoning-Rules Policy Checker')
        selectedoption = options_menu()
        chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
        if selectedoption == '1':
            allrules = gather_per_leaf_zonerules(chosenleafs[0],pod='1')
            epgdict = create_epgnum_to_epgname_dict(allepglist)
            l3outresults = gather_l3out_epgs()
            tempdict = create_epgnum_to_epgname_dict(l3outresults)
            #import pdb; pdb.set_trace()
            epgdict.update(tempdict)
            vrfresults = gather_vrf_sclass()
            tempdict = create_epgnum_to_epgname_dict(vrfresults)
            epgdict.update(tempdict)
            bdresults = gather_bd_sclass()
            tempdict = create_epgnum_to_epgname_dict(bdresults)
            epgdict.update(tempdict)
            vrfdict = {}
            for k in vrfresults:
                    #import pdb; pdb.set_trace()
                    scope = k['fvCtx']['attributes']['scope']
                    dn = k['fvCtx']['attributes']['dn']
                    dn = ('|'.join(dn.split('/')[1:])).replace('tn-','').replace('ctx-','')
                    vrfdict[scope] = dn
            del tempdict
            try:
                for rule in allrules:
                    #import pdb; pdb.set_trace()
                   # if rule.dPcTag == '10937' or rule.dPcTag == 10937:
                   #     import pdb; pdb.set_trace()
                    if epgdict.get(rule.dPcTag):
                        nameformat = epgbase._tenantappepg_formatter(epgdict[rule.dPcTag].dn,delimiter='|')
                        if nameformat == None:
                            nameformat = repr(epgdict[rule.dPcTag])
                        rule.dPcTagname = nameformat
                    elif rule.dPcTag == 15 or rule.dPcTag == '15':
                        rule.dPcTagname = 'pfx(0.0.0.0/0)'
                    else:
                        rule.dPcTagname = rule.dPcTag
    
                    
                    if epgdict.get(rule.sPcTag):
                        if rule.sPcTag == '15':
                            nameformat
                        nameformat = epgbase._tenantappepg_formatter(epgdict[rule.sPcTag].dn,delimiter='|')
                        if nameformat == None:
                            nameformat = repr(epgdict[rule.sPcTag])
                        rule.sPcTagname = nameformat
                    elif rule.sPcTag == 15 or rule.sPcTag == '15':
                        rule.sPcTagname = 'pfx(0.0.0.0/0)'
                    else:
                        rule.sPcTagname = rule.sPcTag

            except:
                import pdb; pdb.set_trace()
    
            finalacllist = []
            for x in allrules:                
                try:
                    if vrfdict.get(x.scopeId):
                        finalacllist.append([rulepriority[x.prio],x.id,x.action,vrfdict[x.scopeId],x.sPcTag,x.sPcTagname,x.dPcTag,x.dPcTagname,x.ctrctName,x.fltId,x.hitcum,x.pktsLast])
                    else:
                        if x.sPcTagname == '32777' or x.sPcTagname == 32777:
                            import pdb; pdb.set_trace()
                        finalacllist.append([rulepriority[x.prio],x.id,x.action,x.scopeId,x.sPcTag,x.sPcTagname,x.dPcTag,x.dPcTagname,x.ctrctName,x.fltId,x.hitcum,x.pktsLast])
                except TypeError:
                    import pdb; pdb.set_trace()

            aclentriesdict = gather_aclfilters_entries(chosenleafs[0])
            for aclentry in aclentriesdict.values():
                for entry in aclentry:
                    print(entry.entry_priority, entry.tcpRules)

            ######
            from collections import deque
            from Queue import PriorityQueue
            priroitydictgroupings = {}
            for priroitygroup, items in itertools.groupby(sorted(finalacllist,key=itemgetter(0)), key=itemgetter(0)):
                priroitydictgroupings[priroitygroup] = list(items)
            for prilevel, entries in priroitydictgroupings.items():
                qq = PriorityQueue()
                #denyque = deque()
                #permitque = deque()
                #redirque = deque()
                for rule in entries:
                    if 'deny' in rule[2] and 'log' in rule[2]:
                        rule.insert(3,'1')
                        #qq.put((1,rule))
                        #denyque.appendleft(rule)
                if qq.qsize != len(entries):

                #if len(denyque) != len(entries):
                    for rule in entries:
                        if 'deny' in rule[2] and 'log' not in rule[2]:
                            rule.insert(3,'2')
                            #qq.put((3,rule))
                            #denyque.append(rule)
                    for rule in entries:
                        if 'redir' in rule[2] and 'log' in rule[2]:
                            rule.insert(3,'30')
                            #qq.put((30,rule))
                        if 'redir' in rule[2] and 'log' not in rule[2]:
                            rule.insert(3,'40')
                            #qq.put((40,rule))
                            #redirque.appendleft(rule)
                    #if len(redirque) > 1:
                    #    tiebreaker
                    for rule in entries:
                        if 'permit' in rule[2] and 'log' in rule[2]:
                            rule.insert(3,'50')
                            #qq.put((50,rule))
                            #permitque.append(rule)
                    for rule in entries:
                        if 'permit' in rule[2]  and 'log' not in rule[2]:
                            rule.insert(3,'60')
                            #qq.put((60,rule))
                            #permitque.append(rule)
                print(prilevel)
                ruleprint = ''
                newentries = []
                for x in entries:
                    if len(aclentriesdict[x[10]]) > 1:
                        for num,z in enumerate(aclentriesdict[x[10]]):
                            v = aclentriesdict[x[10]][num]
                            t = x[:]
                            rulestring = ';'.join((v.etherT,v.prot,v.sFromPort,v.sToPort,v.dFromPort,v.dToPort,v.tcpRules)).replace('unspecified','unsp')
                            t.append(rulestring)
                            t.append(str(aclentriesdict[x[10]][num].entry_priority))
                            newentries.append(t)
                    else:
                        v = aclentriesdict[x[10]][0]
                        t = x[:]
                        rulestring = ';'.join((v.etherT,v.prot,v.sFromPort,v.sToPort,v.dFromPort,v.dToPort,v.tcpRules)).replace('unspecified','unsp')
                        t.append(rulestring)
                        t.append(str(v.entry_priority))
                        newentries.append(t)


                for x in sorted(newentries, key=lambda x: (x[0],x[3],x[-1],x[5])):
                    ruleprint += ', '.join(map(str,x))
                    ruleprint += '\n'
                print(ruleprint)
                #for x in sorted(entries, key=lambda x: (x[0],x[3],x[5])):
                    
                #for x in range(qq.qsize()):
                #    print(qq.get())
                print('\n\n')
                continue
                import pdb; pdb.set_trace()
                redirque.extend(permitque)
                denyque.extend(redirque)
                print(denyque)



                    #if len(per)
                
                #denyresults = [entry for entry in entries if 'deny' in entry[2]]
                #dequdenyresults
                #if len(denyresults) > 1:
                #    denylogresults = []
#
#
                #print(results)
            #
            ######
            import pdb; pdb.set_trace()
            headers = ['','','Action','T/vrf','(S)Tag','Source EPG','(D)Tag','Destination EPG','Contract','Total Hit','Last5min Hits']
            sizes = get_column_sizes(rowlist=newentries,baseminimum=headers)
            print(' Order #  {:{s2}} {:{s3}} {:{s4}} {:{s5}} {:{s6}} {:{s7}} {:{s8}} {:{s9}} {:{s10}}'.format(*headers[2:],s0=sizes[0],s1=sizes[1],s2=sizes[2],s3=sizes[3],s4=sizes[4],s5=sizes[5],s6=sizes[6],s7=sizes[7],s8=sizes[8],s9=sizes[9],s10=sizes[10]))
            print('-' * sum(sizes))
            for x in sorted(finalacllist, key=lambda x: (int(x[0]),x[3],x[2])):
                print('[{:>{s0}}:{:{s1}}] {:{s2}} {:{s3}} {:{s4}} {:{s5}} {:{s6}} {:{s7}} {:{s8}} {:{s9}} {:{s10}} {{:s11}} {:{s12}} {:{s13}} {{:s14}} {{:s15}}'.format(*x,s0=sizes[0],s1=sizes[1],s2=sizes[2],s3=sizes[3],s4=sizes[4],s5=sizes[5],s6=sizes[6],s7=sizes[7],s8=sizes[8],s9=sizes[9],s10=sizes[10]))

            import pdb; pdb.set_trace()
        elif selectedoption == '2':
            pass
        elif selectedoption == '3':
            pass
        elif selectedoption == '4':
            pass

        chosenepgs, _ = display_and_select_epgs(None, allepglist)


