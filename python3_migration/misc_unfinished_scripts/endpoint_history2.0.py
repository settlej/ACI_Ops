#!/bin//python

import re
import readline
import urllib.request, urllib.error, urllib.parse
import json
import ssl
import os


def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib.request.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib.request.urlopen(request, context=ssl._create_unverified_context())

def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def validateipaddress(ip):
    result = re.search(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', ip)
    if result:
        return True
    return False

def findipaddress():
    ipaddr = eval(input("\nWhat is the ip address?: "))
    # verify a valid ip format and its not a blank input
    if not validateipaddress(ipaddr) or ipaddr == '':
        return
    url = """https://localhost/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-include=required&rsp-subtree-filter=eq(fvIp.addr,"{}")""".format(ipaddr)
    result, totalcount = GetResponseData(url)
    try:
        # Check to see if there is no 'live' history of ip address
        if totalcount == '0':
            print('\n')
            print(("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address")))
            print(('-'*97))
            # \x1b[41;1m is a special sequece to start red color for ansii color in terminal and \x1b[0m returns colors to normal 
            print('\x1b[41;1mNo "LIVE Endpoint" IP found...check event history\x1b[0m\n')
            print('\n')
        # If 'live' history found, print history
        else:
            mac = result[0]['fvCEp']['attributes']['mac']
            #encap = result[0]['fvCEp']['attributes']['encap']
            dn = result[0]['fvCEp']['attributes']['dn']
            # split 'dn' into a list and only keep uni->epg
            dnpath = '/'.join(dn.split('/')[:4])
            print('\n')
            print(("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path")))
            print(('-'*115))
                                #url2 = """https://localhost/api/node/mo/uni/tn-SI/ap-APP-ISE/epg-EPG-VL10-ISE/cep-{}.json?query-target=subtree&target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm""".format(mac)
            url3 = """https://localhost/mqapi2/troubleshoot.eptracker.json?ep={}/cep-{}&order-by=troubleshootEpTransition.date|desc&page=0&page-size=25""".format(dnpath,mac)

            result3, totalcount3 = GetResponseData(url3)
            for entry in result3:
                mac = entry['troubleshootEpTransition']['attributes']['mac']
                ip = entry['troubleshootEpTransition']['attributes']['ip']
                date = entry['troubleshootEpTransition']['attributes']['date'][:-6]
                encap_vlan = entry['troubleshootEpTransition']['attributes']['encap']
                path = entry['troubleshootEpTransition']['attributes']['path']

                leaf = re.search(r'paths-[0-9]{3}',path)
                if leaf:
                    leaf = leaf.group().replace('paths-', '')
                interface = re.search(r'\[.*\]',path)
                if interface:
                    interface = interface.group()[1:-1]
                fex = re.search(r'extpaths-[0-9]{3}',path)
                if fex:
                    fex = fex.group().replace('extpaths-', '')
                    path = 'leaf{} fex={} {}'.format(leaf,fex,interface)
                else:
                    path = 'leaf{} {}'.format(leaf,interface)
                 
                print(("{:26}\t{:15}\t{:18}\t{:20}\t{}".format(date, encap_vlan, ip, mac, path) ))
    except Exception as e:
        print(e)
        return
    history = eval(input("\nWould you like to see event history of {}? [y/n]: ".format(ipaddr)))
    if history != '' and history.lower() == 'y':
        return ipaddr
    else:
        return 0

def searcheventrecords(ipaddr):
    #event record code E4209236 is "ip detached event"
    url = """https://localhost/api/node/class/eventRecord.json?query-target-filter=and(eq(eventRecord.code,"E4209236"))&""" \
          """query-target-filter=and(wcard(eventRecord.descr,"{ipaddr}$"))&order-by=eventRecord.created|desc&page=0&page-size=25""".format(ipaddr=ipaddr)
    result, totalcount = GetResponseData(url)
    print('\n')
    if totalcount == '0':
        print(("{:.<45}0\n".format("Searching Event Records")))
    else:
        print(("{:.<45}Found {} Events\n".format("Searching Event Records",totalcount)))
       
    print(("{:26}{:12}".format('Date','Description', )))
    print(('-'*90))
    if totalcount == '0':
        print(("\x1b[41;1mNo event history found for IP {}\x1b[0m\n\n".format(ipaddr)))
        return
    for event in result:
        timestamp = event['eventRecord']['attributes']['created']
        descr = event['eventRecord']['attributes']['descr']
        dn = event['eventRecord']['attributes']['dn']
        mac = re.search(r'cep-.{17}', dn)
        print(("{:26}{:^12}  [{}]".format(timestamp[:-6],descr,'mac: ' + mac.group()[4:])))
        

def main():
    while True:
        os.system('clear')
        ipaddr = findipaddress()
        # If user desides not to search events but wants to look up another ip address
        if ipaddr == 0:
            ask = eval(input("\nCheck another ip address? [y/n]: "))
            # if 'y' then restart the while loop to findipaddress()
            if ask.lower() == 'y' and ask != '':
                continue
            else:
                exit()
        # If user did want to search events and then look up another ip address afterwards
        elif ipaddr:
            searcheventrecords(ipaddr)
            ask = eval(input("\nCheck another ip address? [y/n]: "))
            # if 'y' then restart the while loop to findipaddress()
            if ask.lower() == 'y' and ask != '':
                continue
            else:
                exit()

if __name__ == '__main__':

    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()
        
    main()
