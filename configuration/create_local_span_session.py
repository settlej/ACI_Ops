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
import datetime
import itertools
import trace
import pdb
import getpass
import datetime
from localutils.custom_utils import *
import interfaces.switchpreviewutil as switchpreviewutil
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)



def create_span_dest_url(dest_int, name, leaf):
    destport = dest_int.dn
    spandestgrpname = name + '_leaf' + leaf + '_' + dest_int.name.replace('/','_')
    spandestname = name + '_leaf' + leaf + '_' + dest_int.name.replace('/','_')
    desturl = """https://{apic}/api/node/mo/uni/infra/destgrp-{}.json""".format(spandestname,apic=apic)
    destdata = """{"spanDestGrp":{"attributes":{"name":"%s","status":"created"},"children":[{"spanDest":{"attributes":{"name":"%s","status":"created"},"children":[{"spanRsDestPathEp":{"attributes":{"tDn":"%s","status":"created"},"children":[]}}]}}]}}""" % (spandestgrpname, spandestname, destport)
    logger.info(desturl)
    logger.info(destdata)
    result, error = PostandGetResponseData(desturl, destdata, cookie)
    logger.debug(result)
    logger.debug(error)
    if result == []:
        print("Successfully added Destination Port")
        return 'Success'
    else: 
        print('\x1b[1;37;41mFailure\x1b[0m -- ' + error)
        return 'Failed'

def create_source_session_and_port(source_int, dest_int, name, leaf):
    sourcelist = []
    if len(source_int) >= 1:
        for source in source_int:
            spansourcename = name + '_leaf' + leaf + '_' + source.name.replace('/','_')
            sourcelist.append({"spanSrc":{"attributes":{"name":spansourcename,"status":"created"},"children":[{"spanRsSrcToPathEp":{"attributes":{"tDn":source.dn,"status":"created"},"children":[]}}]}})
    spandestname = name + '_leaf'  + leaf + '_'+ dest_int.name.replace('/','_')
    spansessionname = name  + '_leaf' + leaf + '_' + 'SPAN_SESSION' #+ datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S')
    #sourceport = source_int.dn
    sourceurl = """https://{apic}/api/node/mo/uni/infra/srcgrp-{}.json""".format(spansessionname,apic=apic)
    sourcedata = {"spanSrcGrp":{"attributes":{"name":spansessionname,"status":"created"},"children":[{"spanSpanLbl":{"attributes":{"name":spandestname,"status":"created"},"children":[]}}]}}
    sourcedata['spanSrcGrp']['children'].extend(sourcelist)
    sourcedata = json.dumps(sourcedata)
    logger.info(sourceurl)
    logger.info(sourcedata)
    result, error = PostandGetResponseData(sourceurl, sourcedata, cookie)
    logger.debug(result)
    logger.debug(error)
    if result == []:
        print("Successfully added Source Session and Source Port")
    else:
        print('\x1b[1;37;41mFailure\x1b[0m -- ' + error)


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    while True:
        clear_screen()
        location_banner('Local SPAN Port Creation Wizard')

        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?")
        print('\r')      
        time = get_APIC_clock(apic,cookie)
        name = time.replace(' ','T') + '_' + getpass.getuser()
        chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
        switchpreviewutil.main(apic,cookie,chosenleafs,purpose='port_status')
        direction= 'Source'
        print("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: \n".format(direction))
        source_returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
        #import pdb; pdb.set_trace()
        direction = 'Destination'
        print("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: \n".format(direction))
        dest_returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
        confirmstr = 'Local SPAN setup:\n Source Port:'
         #\x1b[1;33;40m{} {}\x1b[0m '.format(source_returnedlist[0].leaf, source_returnedlist[0].name)
        for source in source_returnedlist:
            confirmstr += ' \x1b[1;33;40m{} {}\x1b[0m'.format(source.leaf, source.name)
            if len(source_returnedlist) > 1 and source_returnedlist[-1] != source:
                confirmstr += ','
        for dest in dest_returnedlist:
            confirmstr += ' to Destination Port: \x1b[1;33;40m{} {}\x1b[0m '.format(dest.leaf, dest.name)
            if len(dest_returnedlist) > 1 and dest_returnedlist[-1] != dest:
                confirmstr += ','
        print(confirmstr)
       # import pdb; pdb.set_trace()
        while True:
            ask = custom_raw_input('\nConfirm Local SPAN deployment? [y|n]: ')
            if ask != '' and ask[0].lower() == 'y':
                break
            if ask != '' and ask[0].lower() == 'n':
                return
            else:
                continue
        print('\n')
        span_dest_result = create_span_dest_url(dest_returnedlist[0], name, chosenleafs[0])
        if span_dest_result == 'Failed':
            custom_raw_input("\n\x1b[1;37;41mFailed to created SPAN destination port\x1b[0m.  Press enter to continue...")
            continue
        create_source_session_and_port(source_returnedlist,dest_returnedlist[0], name, chosenleafs[0])
        cookie = refreshToken(apic, cookie)
        custom_raw_input('\n#Press enter to continue...')
        break

#if __name__ == '__main__':
#    try:
#        main()
#    except KeyboardInterrupt as k:
#        print('\n\nEnding Script....\n')
#        exit()


#name = custom_raw_input("What is the source interface? ")
#
#name = custom_raw_input(")
#
#{"spanDestGrp":{"attributes":{"dn":"uni/infra/destgrp-SPAN_Destination_eth1_30","name":"SPAN_Destination_eth1_30",
#"rn":"{rn}","status":"created"},"children":[{"spanDest":
#{"attributes":{"dn":"uni/infra/destgrp-SPAN_Destination_eth1_30/dest-SPAN_Destination_eth1_30",
#"name":"SPAN_Destination_eth1_30","rn":"dest-SPAN_Destination_eth1_30","status":"created"},
#"children":[{"spanRsDestPathEp":{"attributes":{"tDn":"topology/pod-1/paths-101/pathep-[eth1/30]",
#"status":"created"},"children":[]}}]}}]}}.format(dn=dn, name=name, rn=rn, spanDestdn=spanDestdn, spanDestrn=spanDestrn,
#destport=destport)
