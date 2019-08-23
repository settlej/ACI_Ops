#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os
import datetime


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

def getCookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

def displaycurrenttime():
    currenttime = datetime.datetime.now()
    return str(currenttime)[:-3]

def time_difference(admin_time):
    currenttime = datetime.datetime.now()
    ref_admin_time = datetime.datetime.strptime(admin_time, '%Y-%m-%d %H:%M:%S.%f')
    return str(currenttime - ref_admin_time)[:-7]


def askrefresh():
    while True:
        refresh = raw_input("Return to admin list? [y=default|n]:  ") or 'y'
        if refresh[0].lower() == 'y':
            return True
        elif refresh[0].lower() == 'n':
            return False
        else:
            continue
    

def gatheranddisplayrecentadmins():
    while True:
        getCookie()
        os.system('clear')
        print("Current time = " + displaycurrenttime())
        url = """https://localhost/api/node/class/aaaModLR.json?query-target-filter=not(wcard(aaaModLR.dn,%22__ui_%22))&order-by=aaaModLR.created|desc&page=0&page-size=50"""
        result, totauserount = GetResponseData(url)
        print('\n{:>5}   {:26}{:20}{:18}{:18}{}'.format('#','Time','Time Difference', 'Type','User','admin Summary'))
        print('-'*175)
        admindict = {}
        for num,admin in enumerate(result,1):
            if admin.get('aaaModLR'):
                admindescr = admin['aaaModLR']['attributes']['descr'].split()
                admindescr = ' '.join(admindescr)
                if len(admindescr) > 120:
                     summaryadmindescr = admindescr[:120] + '...'
                else:
                    summaryadmindescr = admindescr
                admincreated = ' '.join(admin['aaaModLR']['attributes']['created'].split('T'))
                admintrig = admin['aaaModLR']['attributes']['trig']
                adminuser = admin['aaaModLR']['attributes']['user']
                admindn = admin['aaaModLR']['attributes']['dn']
                diff_time = time_difference(admincreated[:-6])
                admindict[num] = [admincreated[:-6],admintrig,adminuser,admindn,admindescr]
                print('{:5}.) {:26}{:20}{:18}{:18}{}'.format(num,admincreated[:-6],diff_time,admintrig,adminuser,summaryadmindescr))
        
        while True:
            moredetails = raw_input("\nMore details, select number [refresh=Blank and Enter]:  ")
            if moredetails == '':
                break
            if moredetails.isdigit() and admindict.get(int(moredetails)):
                break
            else:
                print('\x1b[41;1mInvalid, number does not exist...try again\x1b[0m\n') 
        if moredetails == '':
            continue
        diff_time = time_difference(admindict[int(moredetails)][0])
        print('\n\n{:26}{:20}{:18}{:18}{}'.format('Time','Time Difference', 'Type','User','Object-Affected'))
        print('-'*120)
        print('{:26}{:20}{:18}{:18}{}\n'.format(admindict[int(moredetails)][0],diff_time, admindict[int(moredetails)][1],admindict[int(moredetails)][2],'/'.join(str(admindict[int(moredetails)][3]).split('/')[:-1])))
        print('admin Details')
        print('-'*15)
        print(admindict[int(moredetails)][4])
        print('\n\n')

        refresh = askrefresh()
        if refresh == True:
            continue
        else:
            print('\nEnding Program...\n')
            break
        

def main():
    gatheranddisplayrecentadmins()

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print("\n\nExiting Program....")
        exit()
