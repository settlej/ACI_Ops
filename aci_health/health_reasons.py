#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import ipaddress


ipaddr = None

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

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()
get_Cookie()
#url = """https://localhost/api/node/mo/topology/pod-1/node-101/sys.json?query-target=children&rsp-subtree-include=health,fault-count"""
#result, totalcount = GetResponseData(url)
#for object in result:
#    for currentobject in object:
#        print(currentobject)
#        if object[currentobject]['children']:
#            for ob in object[currentobject]['children']:
#                if ob.get('healthInst'):
#                    print(ob['healthInst'])


#url = """https://localhost/api/node/mo/topology/pod-1/node-102/sys/ch.json?query-target=children&rsp-subtree-include=health,required&rsp-subtree-filter=lt(healthInst.cur,"100")"""
#result, totalcount = GetResponseData(url)
#for object in result:
#    for currentobject in object:
#        print(currentobject, object[currentobject]['children'][0]['healthInst']['attributes']['cur'])

url = """https://localhost/api/node/mo/topology/pod-1/node-102/sys.json?query-target=children&rsp-subtree-include=health,required&rsp-subtree-filter=lt(healthInst.cur,"100")"""
result, totalcount = GetResponseData(url)
for object in result:
    for currentobject in object:
        #print(currentobject, object[currentobject]['children'][0]['healthInst']['attributes']['cur'], object[currentobject]['attributes']['dn'])
        url = """https://localhost/api/node/mo/{}.json?query-target=children&rsp-subtree-include=health,required&rsp-subtree-filter=lt(healthInst.cur,"100")""".format(object[currentobject]['attributes']['dn'])
        #print(url)
        result2, totalcount = GetResponseData(url)
        for object2 in result2:
            for currentobject2 in object2:
                #pass
                #print(currentobject2, object2[currentobject2]['children'][0]['healthInst']['attributes']['cur'], object2[currentobject2]['attributes']['dn'])
                url = """https://localhost/api/node/mo/{}.json?query-target=children&rsp-subtree-include=health,required&rsp-subtree-filter=lt(healthInst.cur,"100")""".format(object2[currentobject2]['attributes']['dn'])
                result3, totalcount = GetResponseData(url)
                for object3 in result3:
                    for currentobject3 in object3:
                        print(currentobject3, object3[currentobject3]['children'][0]['healthInst']['attributes']['cur'], object3[currentobject3]['attributes']['dn'])
#url = """https://localhost/api/node/class/faultInst.json?query-target-filter=eq(wcard(faultInst,"102"))"""
#result, totalcount = GetResponseData(url)
#print(result)