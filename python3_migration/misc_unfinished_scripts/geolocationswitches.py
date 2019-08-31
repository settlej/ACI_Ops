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

def main():
    url = 'https://localhost/api/node/class/geoRsNodeLocation.json'
    result, totalCount = GetResponseData(url)
    print(result)

if __name__ == '__main__':
    main()