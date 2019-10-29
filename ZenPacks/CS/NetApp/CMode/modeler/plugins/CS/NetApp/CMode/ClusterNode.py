"""Models NetApp CMode device using ONTAP REST API"""

# stdlib Imports
import json
import urllib
import base64

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap


class ClusterNode(PythonPlugin):
    """NetApp CMode modeler plugin."""

    relname = 'clusterNodes'
    modname = 'ZenPacks.CS.NetApp.CMode.ClusterNode'

    requiredProperties = (
        'zNetAppAPI',
        'zNetAppUser',
        'zNetAppPassword',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        log.info('%s: collecting data', device.id)

        baseUrl = getattr(device, 'zNetAppAPI', None)
        if not baseUrl:
            manageIp = getattr(device, 'manageIp', None)
            if not manageIp:
                log.error("Please fill in zNetAppAPI property")
                returnValue(None)
            baseUrl = 'https://{ip}/api'.format(ip=manageIp)
        
        un = getattr(device, 'zNetAppUser', None)
        pw = getattr(device, 'zNetAppPassword', None)
	if un and pw:
            basic = base64.encodestring('{un}:{pw}'.format(un=un, pw=pw))
            auth = {'Authorization': 'Basic {b}'.format(b=basic.strip())}
        else:
            auth = {}
            log.info('Please consider using zNetAppUser and zNetAppPassword for authorization')

        try:
            response = yield getPage('{url}/cluster/nodes?fields=model,serial_number,location,version.full,membership,name,ha.enabled&return_records=true&return_timeout=15'.format(url=baseUrl), headers=auth)
            response = json.loads(response)
        except Exception, e:
            log.error('%s: %s', device.id, e)
            returnValue(None)

        noderm = self.relMap()
        for record in response['records']:
            om = self.objectMap()
            om.id = self.prepId(record['uuid'])
            om.node_name = record['name']
            om.serial_number = record['serial_number']
            om.location = record['location']
            om.model = record['model']
            om.version = record['version']['full']
            om.membership = record['membership']
            noderm.append(om)

            compname = 'clusterNodes/{0}'.format(om.id)
            sparerm = yield self.spares(device, record['uuid'], baseUrl, auth, compname, log)

        returnValue([noderm] + [sparerm])

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""
        return results

    @inlineCallbacks
    def spares(self, device, uuid, baseUrl, auth, compname, log):
        try:
            response = yield getPage('{url}/storage/disks?state=spare&fields=*&return_records=true&return_timeout=15'.format(url=baseUrl), headers=auth)
            response = json.loads(response)
        except Exception, e:
            log.error('%s: %s', device.id, e)
            returnValue(None)

        rm = RelationshipMap()
        rm.compname = compname
        rm.relname = 'spareDisks'
        rm.modname = 'ZenPacks.CS.NetApp.CMode.SpareDisk'
        rm.classname = 'SpareDisk'

        for record in response['records']:
            om = ObjectMap()
            om.modname = 'ZenPacks.CS.NetApp.CMode.SpareDisk'
            om.id = self.prepId(record['serial_number'])
            rm.append(om)
        
        log.error(rm)
        returnValue(rm)
