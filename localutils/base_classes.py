import re
#from localutils.custom_utils import *
import itertools
class interfacebase():
    def get_leaf(self, x):
        leafcompile = re.compile(r"((node-|paths-)\d+)")
        if leafcompile.search(x):
            return leafcompile.search(x).group(1)
        else:
            return None
    def get_pod(self, x):
        podcompile = re.compile(r"pod-\d+")
        if podcompile.search(x):
            return podcompile.search(x).group()
        else:
            return None
    def get_leaf_num(self, x):
        result = self.getleaf(x)
        if result:
            return re.search(r'\d+',result).group()
        else:
            return None
    def get_pod_num(self, x):
        result = self.getpod(x)
        if result:
            return re.search(r'\d+',result).group()
        else:
            return None    
    def get_pc_name(self, x):
        pccompile = re.compile(r"accbundle-([^/]*)")
        if pccompile.search(x):
            return pccompile.group(1)
        else:
            return None
    def get_pc_num(self, x, num_only=False):
        if num_only:
            pccompile = re.compile(r"aggr-\[po(\d+)\]")
        else:     
            pccompile = re.compile(r"aggr-\[(po\d+)\]")
        if pccompile.search(x):
            return pccompile.group(1)
        else:
            return None
    def get_eth(self,x, num_only=False):
        if num_only:
            if re.search(r"phys-\[eth(.*)\]",x):
                return re.search(r"phys-\[eth(.*)\]",x).group(1)
            else:
                return None
        else:
            if re.search(r"phys-\[(eth.*)\]",x):
                return re.search(r"phys-\[(eth.*)\]",x).group(1)
            else:
                return None
    def parse_pod_leaf_phyinterface(self, x, returntype='dict'):
        if re.search(r"pod-(\d+)\/paths-(\d+)\/pathep-\[(.*)\]",x):
            self._physpath =  re.findall(r"pod-(\d+)\/paths-(\d+)\/pathep-\[(.*)\]",x)
            import pdb; pdb.set_trace()
            self._pod, self._leaf, self._interface = self._physpath[0]
            if returntype == 'dict':
                return {'pod':self._pod,'leaf':self._leaf,'interface':self._interface}
            elif returntype == 'list':
                return self._physpath[0]
            else:
                raise NotImplementedError
        else:
            return None



class epgbase():
    def parse_tenant_app_epg(self,x, returntype='dict'):
        if re.search(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x):
            self._dngroups = re.findall(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x)
            self._tenant, self._app, self._epg = self._dngroups[0]
            if returntype == 'dict':
                return {'tenant':self._dngroups[0],'app':self._dngroups[1],'epg':self._dngroups[2]}
            elif returntype == 'list':
                return self._dngroups[0]
            else:
                raise NotImplementedError
        else:
            return None
    @staticmethod
    def _parse_tenant_app_epg(x, returntype='dict'):
        if re.search(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x):
            _dngroups = re.findall(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x)
            _tenant, _app, _epg = _dngroups[0]
            if returntype == 'dict':
                return {'tenant':_dngroups[0],'app':_dngroups[1],'epg':_dngroups[2]}
            elif returntype == 'list':
                return _dngroups[0]
            else:
                raise NotImplementedError
        else:
            return None

    def tenantappepg_formatter(self, x=None, delimiter='/'):
        if x == None:
            if hasattr(self,'tenant') and hasattr(self,'app') and hasattr(self,'epg'): 
                return delimiter.join((self.tenant,self.app,self.epg))
            else:
                return None
        elif isinstance(x,str) or isinstance(x,unicode):
            if re.search(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x):
                self.dngroups = re.findall(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x)
                return delimiter.join(*self.dngroups)
            else:
                return None
        elif isinstance(x,list) or isinstance(x,tuple):
            return delimiter.join(x)
        else:
            return None
    @staticmethod
    def _tenantappepg_formatter(x, delimiter='/'):
        if isinstance(x,str) or isinstance(x,unicode):
            if re.search(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x):
                dngroups = re.findall(r"tn-(.*)\/ap-(.*)\/epg-([^/]*)",x)
                return delimiter.join(*dngroups)
            else:
                return None
        elif isinstance(x,list) or isinstance(x,tuple):
            return delimiter.join(x)
        else:
            return None




class interfacelower(interfacebase,epgbase):
    def __init__(self,kwargs):
        self.__dict__.update(**kwargs)
        

if __name__ == '__main__':   
    interfacelist = [{'dn': u'topology/pod-1/paths-101/pathep-[eth1/34]', 'leaf': u'leaf-101', 'name': u'eth1/34', 'descr': u'', 'number': None, 'fexethname': None, 'fullethname': u'eth1/34', 'removedint': u'topology/pod-1/paths-101', 'shortname': u'34', 'epgfvRsPathAttlist': [], 'fex': None},
    {'dn': u'topology/pod-1/paths-102/pathep-[eth1/34]', 'leaf': u'leaf-101', 'name': u'eth1/34', 'descr': u'', 'number': None, 'fexethname': None, 'fullethname': u'eth1/34', 'removedint': u'topology/pod-1/paths-102', 'shortname': u'34', 'epgfvRsPathAttlist': [], 'fex': None},
    {'dn': u'topology/pod-1/paths-101/pathep-[eth1/35]', 'leaf': u'leaf-101', 'name': u'eth1/35', 'descr': u'', 'number': None, 'fexethname': None, 'fullethname': u'eth1/35', 'removedint': u'topology/pod-1/paths-101', 'shortname': u'35', 'epgfvRsPathAttlist': [], 'fex': None}]
    
    newinterfacelist = [interobject(x) for x in interfacelist] 
    finalinfralist = {k:list(g) for k, g in itertools.groupby(newinterfacelist, key=lambda x: x.fullethname)}
    #dn = "uni/tn-SI/ap-APP-AD/epg-EPG-VL11-AD/fltCnts"
    interfacedn = 'topology/pod-1/paths-101/pathep-[eth1/39]'
    #for x in newinterfacelist:
    j = interfacelower({'dn':interfacedn})
    print(j.parse_pod_leaf_phyinterface(interfacedn, returntype='dict'))
    #    print(j.tenantappepg_formatter())
    
    
    import pdb; pdb.set_trace()