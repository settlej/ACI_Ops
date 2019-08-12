#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os

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

def retrieve_leaf_list():
    # Display available leafs beginning of script
    url = """https://localhost/api/node/mo/topology/pod-1.json?query-target=children&target-subtree-class=fabricNode&query-target-filter=and(wcard(fabricNode.id,"^1[0-9][0-9]"))"""
    result, totalcount = GetResponseData(url)
    #print(result)
    leafs = [leaf['fabricNode']['attributes']['id'] for leaf in result]
    #print('Available leafs to bounce ports...')
    return leafs

def displayepgs(result):
    print('\n{:10}{:15}{}'.format('Tenant','APP','EPG'))
    print('-'*40)
    #print(result)
    if result[0]['l1PhysIf']['attributes']['layer'] == 'Layer3':
        print('Layer 3 interface, no EPGs\n')
        return
    if result[0]['l1PhysIf'].get('children'):
        for int in result[0]['l1PhysIf']['children']:
            for epgs in int['pconsCtrlrDeployCtx']['children']:
                epgpath = epgs['pconsResourceCtx']['attributes']['ctxDn'].split('/')
                #print(epgpath)
                tenant = epgpath[1][3:]
                app = epgpath[2][3:]
                epg = epgpath[3][4:]
                print('{:10}{:15}{}'.format(tenant,app,epg))
        print('\n')
    else:
        print('No Epgs found...\n')


with open('/.aci/.sessions/.token', 'r') as f:
    cookie = f.read()

def gatherandstoreinterfacesforleaf(leaf):
    url = """https://localhost/api/node/class/topology/pod-1/node-101/l1PhysIf.json"""
    result, totalcount = GetResponseData(url)
    listofinterfaces = [interface['l1PhysIf']['attributes']['id'] for interface in result]
    return listofinterfaces

def main():
    fex = False
    print("\n1.) Physical interface\n" + 
            "2.) Port-channel/vPC\n")
    int_type = raw_input("What is the interface type?: ")
    if int_type == '1':
        listleafs = retrieve_leaf_list()
        print('\nAvailable Leafs\n' + '-'*12)
        for leaf in sorted(listleafs):
            print(leaf)#Leaf' + ' Leaf'.join(leafs))
        print('\r')
        while True:
            leaf = raw_input("What is leaf number?: ")
            if leaf in listleafs:
                break
            else:
                print('\x1b[41;1mInvalid or leaf does not exist...try again\x1b[0m\n')
        availableinterfaces = gatherandstoreinterfacesforleaf(leaf)
        #while True:
        #    askfex = raw_input("Fex interface? [y|n] (default=n):  ") or 'n'
        #    if askfex[0].lower() == 'y':
        #        fex = True
        #        break
        #    else:
        #        break
        while True:
            if fex == True:
                interface = raw_input("What is the interface? (format: ethxxx/x/x): ")
            else:
                interface = raw_input("What is the interface? (format: ethx/x): ")
            if interface in availableinterfaces:
                break
            else:
                print('\x1b[41;1mInvalid or interface does not exist...try again\x1b[0m\n')
        
        url = """https://localhost/api/node/mo/topology/pod-1/node-{leaf}/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(leaf=leaf,interface=interface)
        #print(url)
        result, totalcount = GetResponseData(url)
        displayepgs(result)
    elif int_type == 2:
        pass
    else:
        pass



if __name__ == '__main__':
    while True:
        main()
        ask = raw_input('Another interface? [y|n]:  ') or 'n'
        #print(ask)
        if ask[0].lower() == 'y':
            continue
        else:
            break



