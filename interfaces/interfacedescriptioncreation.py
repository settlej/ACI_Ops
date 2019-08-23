
def createinterfacedescr(overrideName, description, interface)
url =  https://localhost/api/node/mo/uni/infra/hpaths-{overrideName}.json.format(overrideName=overrideName)
payload{"infraHPathS":{"attributes":{"name":"%(overrideName)s","status":"created,modified","descr":"%(description)s"},"children":[{"infraRsHPathAtt":{"attributes":{"tDn":"%(interface)s"},"children":[]}}]}}
response: {"totalCount":"0","imdata":[]}