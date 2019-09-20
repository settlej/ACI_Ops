#!/usr/bin/env python

import os
import getpass
import urllib2
import ssl
import json
import sys
import threading
import time
from localutils.custom_utils import *
import interfaces.change_interface_state as shut_noshut_interfaces
import interfaces.assign_epg_interfaces as assign_epg_interfaces
import interfaces.remove_epgs_interfaces as remove_egps
#import interfaces.show_interface_epgs as show_epgs
import interfaces.portsanddescriptions as portsanddescriptions
import faults_and_logs.new_important_faults as fault_summary
import faults_and_logs.most_recent_fault_changes as most_recent_fault_changes
import faults_and_logs.most_recent_admin_changes as most_recent_admin_changes
import faults_and_logs.most_recent_event_changes as most_recent_event_changes
import faults_and_logs.alleventsbetweendates as alleventsbetweendates
import faults_and_logs.alleventsbetweendates_fulldetail as alleventsbetweendates_fulldetail
import information.endpoint_search as ipendpoint
#import information.routetranslation as epg_troubelshooting
import information.routetranslation as routetranslation
import information.routetrace as check_routing
import configuration.create_local_span_session as create_local_span_session





def getToken(apic, user, pwd):
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://{apic}/api/aaaLogin.json".format(apic=apic)
    payload = '{"aaaUser":{"attributes":{"name":"%(user)s","pwd":"%(pwd)s"}}}' % {"pwd":pwd,"user":user}
    request = urllib2.Request(url, data=payload)
    response = urllib2.urlopen(request, timeout=4)
    token = json.loads(response.read())
    global cookie
    cookie = token["imdata"][0]["aaaLogin"]["attributes"]["token"]
    #return cookie

def getCookie():
    with open('/.aci/.sessions/.token', 'r') as f:
        global cookie
        cookie = f.read()
        return cookie

def localOrRemote():
    if os.path.isfile('/.aci/.sessions/.token'):
        apic = "localhost"
        global cookie
        cookie = getCookie()
        return apic, cookie
    else:
        unauthenticated = False
        timedout = False
        error = ''
        while True:
            clear_screen()
            if unauthenticated:
                print(error)
                unauthenticated = False
            elif timedout:
                print(error)
                apic = raw_input("Enter IP address or FQDN of APIC: ")
                timedout = False
            else:
                print(error)
                apic = raw_input("\nEnter IP address or FQDN of APIC: ")
            try:
                user = raw_input('\nUsername: ')
                pwd = getpass.getpass('Password: ')
                getToken(apic, user,pwd)
            except urllib2.HTTPError as auth:
                unauthenticated = True
                error = '\n\x1b[1;31;40mAuthentication failed\x1b[0m\n'
                continue
            except urllib2.URLError as e:
                timedout = True
                error = "\n\x1b[1;31;40mThere was an '%s' error connecting to APIC '%s'\x1b[0m\n" % (e.reason,apic)
                continue
            except KeyboardInterrupt as k:
                print("\nEnding Program\n")
                exit()
            except Exception as e:
                print(e)
                print("\n\x1b[1;31;40mError has occured, please try again\x1b[0m\n")
                continue
            break
    return apic, cookie

def reauthenticate(apic, error):
    unauthenticated = True
    timedout = False
    while True:
        clear_screen()
        if unauthenticated:
            print(error)
            unauthenticated = False
        elif timedout:
            print(error)
            apic = raw_input("Enter IP address or FQDN of APIC: ")
            timedout = False
        try:
            user = raw_input('\nUsername: ')
            pwd = getpass.getpass('Password: ')
            getToken(apic, user,pwd)
        except urllib2.HTTPError:
            unauthenticated = True
            error = '\n\x1b[1;31;40mAuthentication failed\x1b[0m\n'
            continue
        except urllib2.URLError as e:
            timedout = True
            error = "\n\x1b[1;31;40mThere was an '%s' error connecting to APIC '%s'\x1b[0m\n" % (e.reason,apic)
            continue
        except Exception as e:
            print("\n\x1b[1;31;40mError has occured, please try again\x1b[0m\n")
            continue
        return cookie

class AuthenticationFailure(Exception):
    """Authentication Failure"""
    pass

def authentication_session(apic, cookie):
    while True:
        time.sleep(3)
        print('auth session deamon')
    #q = Queue.Queue()
    #refreshToken()

def main():
    unauthenticated = False
    apic, cookie = localOrRemote()
    a = threading.Thread(target=authentication_session, args=(apic,cookie))
    a.daemon = True
    a.start()
    print(a.isDaemon)
   # raw_input('test')
    keyinterrupt = False
    while True:
        try:
            clear_screen()
            if unauthenticated:
                error = '\n\x1b[1;31;40mAuthentication Failed or timed out...restarting program\x1b[0m'
                cookie = reauthenticate(apic, error)
            unauthenticated = False
            clear_screen()
            if keyinterrupt:
                pass
                #print('\x1b[1;31;40m-------------------------------------------------')
                #print('\nPrevious operation cancelled\n')
                #print('-------------------------------------------------\x1b[0m')
          #  import pdb; pdb.set_trace()

            print('\n What would you like to do?:\n\n' +
                            '\t\x1b[1;32;40m  [INTERFACES]\n'+
                            '\t ---------------------------------------------------\n' +
                            '\t| 1.)  Shut/NoShut interfaces\n' + 
                            '\t| 2.)  Show EPGs on interface\n' + 
                            '\t| 3.)  Add EPGs to interfaces\n' +
                            '\t| 4.)  Remove EPGs from interfaces\n' + 
                            '\t| 5.)  Show interfaces status\n' +
                            '\t| 6.)  Show Endpoints on interface (Not Available)\n' +
                            '\t ---------------------------------------------------\n\n' +
                            '\t  [FAULTS and LOGS]\n'
                            '\t ---------------------------------------------------\n' +
                            '\t| 7.)  Faults Summary\n' + 
                            '\t| 8.)  Recent Faults\n' +
                            '\t| 9.)  Recent Admin Changes\n' + 
                            '\t| 10.) Recent Events\n' +
                            '\t| 11.) Faults/Admin/Events Between Dates\n' + 
                            '\t| 12.) Faults/Admin/Events Between Dates (Detail)\n' +
                            '\t ---------------------------------------------------\n\n' +
                            '\t  [INFORMATION]\n'
                            '\t ---------------------------------------------------\n' +
                            '\t| 13.) Endpoint Search\n' + 
                            '\t| 14.) Show Leaf/Spine/APIC info (Not Available)\n' +
                            '\t| 15.) EPG to EPG troubleshooting (alpha)\n' +
                            '\t| 16.) Route lookup to endpoint \n' +
                            '\t ---------------------------------------------------\n\n' +
                            '\t  [CONFIGURATION]\n'
                            '\t ---------------------------------------------------\n' +
                            '\t| 17.) Configure Local Span\n' + 
                            '\t| 18.) Create EPGs (Not Available)\n' +
                            '\t| 19.) Configure interface Descriptions (Not Available)\n' + 
                            '\t| 20.) Import/Export interface Descriptions (Not Available)\n' + 
                            '\t ---------------------------------------------------\x1b[0m')
            print('\x1b[7')
            print('\x1b[1;33;40m\x1b[5;70H -----------------------------\x1b[0m')
            print('\x1b[1;33;40m\x1b[6;70H|           Hint:             \x1b[0m|')
            print('\x1b[1;33;40m\x1b[7;70H|  Type "exit" on any input   \x1b[0m|')
            print('\x1b[1;33;40m\x1b[8;70H|    to return to main menu   \x1b[0m|')
            print('\x1b[1;33;40m\x1b[9;70H -----------------------------\x1b[0m')
            print('\x1b[8')
            choosen = custom_raw_input('\x1b[u\x1b[40;1H Select a number: ')
            if choosen == '1':
                try:
                    shut_noshut_interfaces.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '2':
                try:
                    #show_epgs.main()
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '3':
                try:
                    assign_epg_interfaces.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue            
            elif choosen == '4':
                try:
                    remove_egps.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '5':
                try:
                    portsanddescriptions.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '6':
                try:
                    #portsanddescriptions.main(apic,cookie)
                    keyinterupt = False
                    continue
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '7':
                try:
                    fault_summary.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '8':
                try:
                    most_recent_fault_changes.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '9':
                try:
                    most_recent_admin_changes.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '10':
                try:
                    most_recent_event_changes.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '11':
                try:
                    alleventsbetweendates.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '12':
                try:
                    alleventsbetweendates_fulldetail.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '13':
                try:
                    ipendpoint.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '14':
                try:
                    routetranslation.main(apic,cookie)
                    keyinterupt = False
                    continue
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '15':
                try:
                    epg_troubelshooting.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '16':
                try:
                    check_routing.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue                
            elif choosen == '17':
                try:
                    create_local_span_session.main(apic,cookie)
                    keyinterupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            #elif choosen == 'exit':
            #    raise KeyboardInterrupt
        except urllib2.HTTPError as e:
            unauthenticated = True
            continue

        except KeyboardInterrupt as k:
            print('\nEnding Program\n')
            exit()
        #except Exception as e:
        #    print(e)
        #    break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print('\nEnding Program\n')
        #exit()
