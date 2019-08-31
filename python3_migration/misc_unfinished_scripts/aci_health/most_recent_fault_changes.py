#!/bin//python

import re
import readline
import urllib.request, urllib.error, urllib.parse
import json
import ssl
import os
import datetime


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

def getCookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

def displaycurrenttime():
    currenttime = datetime.datetime.now()
    return str(currenttime)[:-3]

def time_difference(fault_time):
    currenttime = datetime.datetime.now()
    ref_fault_time = datetime.datetime.strptime(fault_time, '%Y-%m-%d %H:%M:%S.%f')
    return str(currenttime - ref_fault_time)[:-7]


def askrefresh():
    while True:
        refresh = eval(input("Return to fault list? [y=default|n]:  ")) or 'y'
        if refresh[0].lower() == 'y':
            return True
        elif refresh[0].lower() == 'n':
            return False
        else:
            continue
    

def gatheranddisplayrecentfaults():
    while True:
        getCookie()
        os.system('clear')
        print(("Current time = " + displaycurrenttime()))
        url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"))&order-by=faultInfo.lastTransition|desc&page=0&page-size=100"""
        result, totalcount = GetResponseData(url)
        print(('\n{:>5}   {:26}{:20}{:18}{:18}{}'.format('#','Time','Time Difference', 'Type','Fault-State','Fault Summary')))
        print(('-'*175))
        faultdict = {}
        for num,fault in enumerate(result,1):
            if fault.get('faultInst'):
                faultdescr = fault['faultInst']['attributes']['descr'].split()
                faultdescr = ' '.join(faultdescr)
                if len(faultdescr) > 120:
                     summaryfaultdescr = faultdescr[:120] + '...'
                else:
                    summaryfaultdescr = faultdescr
                faultlastTransition = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
                faulttype = fault['faultInst']['attributes']['type']
                faultstate = fault['faultInst']['attributes']['lc']
                faultdn = fault['faultInst']['attributes']['dn']
                diff_time = time_difference(faultlastTransition[:-6])
                faultdict[num] = [faultlastTransition[:-6],faulttype,faultstate,faultdn,faultdescr]
                print(('{:5}.) {:26}{:20}{:18}{:18}{}'.format(num,faultlastTransition[:-6],diff_time,faulttype,faultstate,summaryfaultdescr)))
            else:
                faultdescr = fault['faultDelegate']['attributes']['descr'].split()
                faultdescr = ' '.join(faultdescr)
                if len(faultdescr) > 120:
                     summaryfaultdescr = faultdescr[:120] + '...'
                else:
                    summaryfaultdescr = faultdescr
                faultlastTransition = ' '.join(fault['faultDelegate']['attributes']['lastTransition'].split('T'))
                faulttype = fault['faultDelegate']['attributes']['type']
                faultstate = fault['faultDelegate']['attributes']['lc']
                faultdn = fault['faultDelegate']['attributes']['dn']
                diff_time = time_difference(faultlastTransition[:-6])
                faultdict[num] = [faultlastTransition[:-6],faulttype,faultstate,faultdn,faultdescr]
                print(('{:5}.) {:26}{:20}{:18}{:18}{}'.format(num,faultlastTransition[:-6],diff_time,faulttype,faultstate,summaryfaultdescr)))
        while True:
            moredetails = eval(input("\nMore details, select number [refresh=Blank and Enter]:  "))
            if moredetails == '':
                break
            if moredetails.isdigit() and faultdict.get(int(moredetails)):
                break
            else:
                print('\x1b[41;1mInvalid, number does not exist...try again\x1b[0m\n') 
        if moredetails == '':
            continue
        diff_time = time_difference(faultdict[int(moredetails)][0])
        print(('\n\n{:26}{:20}{:18}{:18}{}'.format('Time','Time Difference', 'Type','Fault-State','Object-Affected')))
        print(('-'*120))
        print(('{:26}{:20}{:18}{:18}{}\n'.format(faultdict[int(moredetails)][0],diff_time, faultdict[int(moredetails)][1],faultdict[int(moredetails)][2],'/'.join(str(faultdict[int(moredetails)][3]).split('/')[:-1]))))
        print('Fault Details')
        print(('-'*15))
        print((faultdict[int(moredetails)][4]))
        print('\n\n')
        refresh = askrefresh()
        if refresh == True:
            continue
        else:
            print('\nEnding Program...\n')
            break
        

def main():
    gatheranddisplayrecentfaults()

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print("\n\nExiting Program....")
        exit()
