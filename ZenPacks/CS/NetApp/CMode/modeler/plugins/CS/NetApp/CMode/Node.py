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


class Node(PythonPlugin):
    """NetApp CMode modeler plugin."""

    relname = 'nodes'
    modname = 'ZenPacks.CS.NetApp.CMode.Node'

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

        rm = self.relMap()
        for record in response['records']:
            om = self.objectMap()
            om.id = self.prepId(record['name'])
            om.node_name = record['name']
            om.serial_number = record['serial_number']
            om.location = record['location']
            om.model = record['model']
            om.version = record['version']['full']
            om.membership = record['membership']
            rm.append(om)
        returnValue(rm)

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""
        return results
